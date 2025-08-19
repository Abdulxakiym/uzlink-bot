from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app import db, match
from app.i18n import T
from app.keyboards import (
    accept_kb_local,
    order_search_kb_local,
    body_types_kb_local,
    confirm_arrival_kb,
    start_delivery_kb,
    driver_arrived_kb,
    confirm_delivery_kb,
)
from app.validators import is_valid_date, is_valid_time, is_int
from handlers.consumers import consumer_menu_kb_local
from app.scheduler import schedule_driver_reminder, cancel_reminder


router = Router()

pending_consumer_location: dict[int, int] = {}
pending_driver_location: dict[int, int] = {}
driver_location_button_sent: set[int] = set()


class OrderCreate(StatesGroup):
    from_place = State()
    to_place = State()
    load_date = State()
    load_time = State()
    ship_date = State()
    ship_time = State()
    weight = State()
    choose = State()
    body_type = State()


@router.message()
async def order_start(message: Message, state: FSMContext):
    if message.text != await T(message.from_user.id, 'find_car'):
        return
    await state.set_state(OrderCreate.from_place)
    await message.answer(await T(message.from_user.id, 'from_place_prompt'))


@router.message(OrderCreate.from_place)
async def order_from(message: Message, state: FSMContext):
    await state.update_data(from_place=message.text)
    await state.set_state(OrderCreate.to_place)
    await message.answer(await T(message.from_user.id, 'to_place_prompt'))


@router.message(OrderCreate.to_place)
async def order_to(message: Message, state: FSMContext):
    await state.update_data(to_place=message.text)
    await state.set_state(OrderCreate.load_date)
    await message.answer(await T(message.from_user.id, 'load_date_prompt'))


@router.message(OrderCreate.load_date)
async def order_load_date(message: Message, state: FSMContext):
    if not is_valid_date(message.text):
        await message.answer(await T(message.from_user.id, 'invalid_date'))
        return
    await state.update_data(load_date=message.text)
    await state.set_state(OrderCreate.load_time)
    await message.answer(await T(message.from_user.id, 'load_time_prompt'))


@router.message(OrderCreate.load_time)
async def order_load_time(message: Message, state: FSMContext):
    if not is_valid_time(message.text):
        await message.answer(await T(message.from_user.id, 'invalid_time'))
        return
    await state.update_data(load_time=message.text)
    await state.set_state(OrderCreate.ship_date)
    await message.answer(await T(message.from_user.id, 'ship_date_prompt'))


@router.message(OrderCreate.ship_date)
async def order_ship_date(message: Message, state: FSMContext):
    if not is_valid_date(message.text):
        await message.answer(await T(message.from_user.id, 'invalid_date'))
        return
    await state.update_data(ship_date=message.text)
    await state.set_state(OrderCreate.ship_time)
    await message.answer(await T(message.from_user.id, 'ship_time_prompt'))


@router.message(OrderCreate.ship_time)
async def order_ship_time(message: Message, state: FSMContext):
    if not is_valid_time(message.text):
        await message.answer(await T(message.from_user.id, 'invalid_time'))
        return
    await state.update_data(ship_time=message.text)
    await state.set_state(OrderCreate.weight)
    await message.answer(await T(message.from_user.id, 'weight_prompt'))


@router.message(OrderCreate.weight)
async def order_weight(message: Message, state: FSMContext):
    if not is_int(message.text):
        await message.answer(await T(message.from_user.id, 'invalid_int'))
        return
    await state.update_data(weight_kg=int(message.text))
    await state.set_state(OrderCreate.choose)
    kb = await order_search_kb_local(message.from_user.id)
    await message.answer(
        await T(message.from_user.id, 'additional_options_prompt'),
        reply_markup=kb,
    )


@router.message(OrderCreate.choose)
async def order_choose(message: Message, state: FSMContext):
    user_id = message.from_user.id
    find_label = await T(user_id, 'find_car_button')
    add_label = await T(user_id, 'additional_options_prompt')
    if message.text == find_label:
        data = await state.get_data()
        await finalize_order(message, state, data, None)
    elif message.text == add_label:
        await state.set_state(OrderCreate.body_type)
        kb = await body_types_kb_local(user_id)
        await message.answer(await T(user_id, 'body_type_prompt'), reply_markup=kb)


@router.message(OrderCreate.body_type)
async def order_body(message: Message, state: FSMContext):
    data = await state.get_data()
    await finalize_order(message, state, data, message.text)


async def finalize_order(message: Message, state: FSMContext, data: dict, body: str | None):
    user_id = message.from_user.id
    order_id = await db.create_order(
        consumer_id=user_id,
        from_place=data['from_place'],
        to_place=data['to_place'],
        load_date=data['load_date'],
        load_time=data['load_time'],
        ship_date=data['ship_date'],
        ship_time=data['ship_time'],
        weight_kg=data['weight_kg'],
        body_type=body,
        consumer_load_lat=data.get('consumer_load_lat'),
        consumer_load_lon=data.get('consumer_load_lon'),
    )
    order = {
        'id': order_id,
        'from_place': data['from_place'],
        'to_place': data['to_place'],
        'weight_kg': data['weight_kg'],
        'body_type': body,
        'consumer_load_lat': data.get('consumer_load_lat'),
        'consumer_load_lon': data.get('consumer_load_lon'),
    }
    drivers = await match.drivers_for_order(order)
    for d in drivers:
        template = await T(d, 'order_card')
        try:
            text = template.format(
                id=order_id,
                from_place=order['from_place'],
                to_place=order['to_place'],
                weight_kg=order['weight_kg'],
            )
        except Exception:
            text = f"Order #{order_id} {order['from_place']} → {order['to_place']} ({order['weight_kg']}kg)"
        kb = await accept_kb_local(d, order_id)
        await message.bot.send_message(d, text, reply_markup=kb)
    await message.answer(await T(user_id, 'order_sent_to_drivers'))
    menu = await consumer_menu_kb_local(user_id)
    await message.answer(await T(user_id, 'menu'), reply_markup=menu)
    await state.clear()


@router.callback_query(F.data.startswith('accept:'))
async def accept_order(callback: CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split(':')[1])
    driver_id = callback.from_user.id
    assigned = await db.assign_order(order_id, driver_id)
    if not assigned:
        await callback.answer('Already taken', show_alert=True)
        return
    order = await db.fetch_order(order_id)
    consumer_id = order['consumer_id']
    consumer = await db.fetch_user(consumer_id)
    driver = await db.fetch_user(driver_id)
    template_c = await T(consumer_id, 'order_card')
    template_d = await T(driver_id, 'order_card')
    try:
        text_c = template_c.format(
            id=order_id,
            from_place=order['from_place'],
            to_place=order['to_place'],
            weight_kg=order['weight_kg'],
        )
        text_d = template_d.format(
            id=order_id,
            from_place=order['from_place'],
            to_place=order['to_place'],
            weight_kg=order['weight_kg'],
        )
    except Exception:
        base = f"Order #{order_id} {order['from_place']} → {order['to_place']} ({order['weight_kg']}kg)"
        text_c = text_d = base
    await callback.message.bot.send_message(
        consumer_id,
        f"{text_c}\n{driver['full_name']} {driver['phone']}",
    )
    await callback.message.bot.send_message(
        driver_id,
        f"{text_d}\n{consumer['full_name']} {consumer['phone']}",
    )
    await db.log_event(order_id, f'accepted_by_{driver_id}')
    pending_consumer_location[consumer_id] = order_id
    await callback.message.bot.send_message(
        consumer_id,
        await T(consumer_id, 'send_loading_location'),
    )
    schedule_driver_reminder(callback.message.bot, order_id, driver_id)
    await callback.answer()


@router.callback_query(F.data.startswith('confirm_arrival:'))
async def confirm_arrival(callback: CallbackQuery):
    order_id = int(callback.data.split(':')[1])
    await db.update_order(order_id, status='loading_confirmed')
    await db.log_event(order_id, 'consumer_confirmed_arrival')
    cancel_reminder(order_id)
    order = await db.fetch_order(order_id)
    driver_id = order['driver_id']
    await callback.message.edit_reply_markup()
    kb = await start_delivery_kb(driver_id, order_id)
    await callback.message.bot.send_message(
        driver_id, await T(driver_id, 'arrival_confirmed'), reply_markup=kb
    )
    await callback.answer()


@router.callback_query(F.data.startswith('start_delivery:'))
async def start_delivery(callback: CallbackQuery):
    order_id = int(callback.data.split(':')[1])
    driver_id = callback.from_user.id
    await db.update_order(order_id, status='in_transit')
    await db.log_event(order_id, 'driver_started_delivery')
    pending_driver_location[driver_id] = order_id
    await callback.message.edit_reply_markup()
    await callback.message.answer(await T(driver_id, 'send_live_location'))
    await callback.answer()


@router.callback_query(F.data.startswith('driver_arrived:'))
async def driver_arrived(callback: CallbackQuery):
    order_id = int(callback.data.split(':')[1])
    driver_id = callback.from_user.id
    await db.update_order(order_id, status='arrived')
    await db.log_event(order_id, 'driver_arrived_destination')
    order = await db.fetch_order(order_id)
    consumer_id = order['consumer_id']
    kb = await confirm_delivery_kb(consumer_id, order_id)
    await callback.message.bot.send_message(
        consumer_id,
        await T(consumer_id, 'driver_arrived'),
        reply_markup=kb,
    )
    await callback.message.edit_reply_markup()
    await callback.answer()


@router.callback_query(F.data.startswith('confirm_delivery:'))
async def confirm_delivery(callback: CallbackQuery):
    order_id = int(callback.data.split(':')[1])
    await db.update_order(order_id, status='completed')
    await db.log_event(order_id, 'consumer_confirmed_delivery')
    order = await db.fetch_order(order_id)
    consumer_id = order['consumer_id']
    driver_id = order['driver_id']
    await callback.message.edit_reply_markup()
    msg_c = await T(consumer_id, 'order_completed')
    msg_d = await T(driver_id, 'order_completed')
    await callback.message.bot.send_message(consumer_id, msg_c)
    await callback.message.bot.send_message(driver_id, msg_d)
    pending_driver_location.pop(driver_id, None)
    driver_location_button_sent.discard(driver_id)
    await callback.answer()


@router.message(F.location)
async def handle_location(message: Message):
    user_id = message.from_user.id
    loc = message.location
    if user_id in pending_consumer_location:
        order_id = pending_consumer_location.pop(user_id)
        await db.update_order(order_id, consumer_load_lat=loc.latitude, consumer_load_lon=loc.longitude)
        await db.log_event(order_id, "consumer_location_shared")
        order = await db.fetch_order(order_id)
        if order and order.get("driver_id"):
            await message.bot.send_location(order["driver_id"], loc.latitude, loc.longitude)
        kb = await confirm_arrival_kb(user_id, order_id)
        await message.answer(await T(user_id, "confirm_arrival_loading"), reply_markup=kb)
    elif user_id in pending_driver_location:
        order_id = pending_driver_location[user_id]
        order = await db.fetch_order(order_id)
        if order:
            await message.bot.send_location(order["consumer_id"], loc.latitude, loc.longitude)
        if user_id not in driver_location_button_sent:
            kb = await driver_arrived_kb(user_id, order_id)
            await message.answer(await T(user_id, "driver_arrived"), reply_markup=kb)
            driver_location_button_sent.add(user_id)
        await db.log_event(order_id, 'driver_live_location')
