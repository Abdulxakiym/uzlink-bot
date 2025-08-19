from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from app import db, match
from app.i18n import T
from app.keyboards import (
    accept_kb_local,
    contact_kb,
    driver_menu_kb_local,
    settings_kb_local,
    start_filter_kb_local,
    profile_inline_kb,
)
from app.validators import is_valid_date, is_int

router = Router()

class DriverMenu(StatesGroup):
    idle = State()

class DriverSettings(StatesGroup):
    choosing = State()
    profile = State()
    change_phone = State()
    change_car_brand = State()
    change_car_year = State()
    change_car_capacity = State()
    change_car_body = State()

class DriverStart(StatesGroup):
    mode = State()
    location = State()


class DriverReg(StatesGroup):
    full_name = State()
    dob = State()
    phone = State()
    exp = State()
    selfie = State()
    license = State()
    car_brand = State()
    car_year = State()
    capacity = State()
    body = State()


@router.message(F.text == '/driver_reg')
async def driver_reg_start(message: Message, state: FSMContext):
    await state.set_state(DriverReg.full_name)
    await message.answer(await T(message.from_user.id, 'full_name_prompt'))


@router.message(DriverReg.full_name)
async def reg_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(DriverReg.dob)
    await message.answer(await T(message.from_user.id, 'dob_prompt'))


@router.message(DriverReg.dob)
async def reg_dob(message: Message, state: FSMContext):
    if not is_valid_date(message.text):
        await message.answer(await T(message.from_user.id, 'invalid_date'))
        return
    await state.update_data(dob=message.text)
    await state.set_state(DriverReg.phone)
    kb = await contact_kb(message.from_user.id)
    await message.answer(await T(message.from_user.id, 'phone_prompt'), reply_markup=kb)


@router.message(DriverReg.phone, F.contact)
async def reg_phone_contact(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await state.set_state(DriverReg.exp)
    await message.answer(await T(message.from_user.id, 'exp_prompt'))


@router.message(DriverReg.phone)
async def reg_phone_text(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(DriverReg.exp)
    await message.answer(await T(message.from_user.id, 'exp_prompt'))


@router.message(DriverReg.exp)
async def reg_exp(message: Message, state: FSMContext):
    if not is_int(message.text):
        await message.answer(await T(message.from_user.id, 'invalid_int'))
        return
    await state.update_data(exp=int(message.text))
    await state.set_state(DriverReg.selfie)
    await message.answer(await T(message.from_user.id, 'selfie_license_prompt'))


@router.message(DriverReg.selfie, F.photo)
async def reg_selfie(message: Message, state: FSMContext):
    await state.update_data(selfie=message.photo[-1].file_id)
    await state.set_state(DriverReg.license)
    await message.answer(await T(message.from_user.id, 'license_prompt'))


@router.message(DriverReg.license, F.photo)
async def reg_license(message: Message, state: FSMContext):
    await state.update_data(license=message.photo[-1].file_id)
    await state.set_state(DriverReg.car_brand)
    await message.answer(await T(message.from_user.id, 'car_brand_prompt'))


@router.message(DriverReg.car_brand)
async def reg_car_brand(message: Message, state: FSMContext):
    await state.update_data(car_brand=message.text)
    await state.set_state(DriverReg.car_year)
    await message.answer(await T(message.from_user.id, 'car_year_prompt'))


@router.message(DriverReg.car_year)
async def reg_car_year(message: Message, state: FSMContext):
    if not is_int(message.text):
        await message.answer(await T(message.from_user.id, 'invalid_int'))
        return
    await state.update_data(car_year=int(message.text))
    await state.set_state(DriverReg.capacity)
    await message.answer(await T(message.from_user.id, 'car_capacity_prompt'))


@router.message(DriverReg.capacity)
async def reg_capacity(message: Message, state: FSMContext):
    if not is_int(message.text):
        await message.answer(await T(message.from_user.id, 'invalid_int'))
        return
    await state.update_data(capacity=int(message.text))
    await state.set_state(DriverReg.body)
    await message.answer(await T(message.from_user.id, 'car_body_prompt'))


@router.message(DriverReg.body)
async def reg_finish(message: Message, state: FSMContext):
    await state.update_data(car_body=message.text)
    data = await state.get_data()
    user_id = message.from_user.id
    await db.upsert_user(
        user_id,
        role='driver',
        full_name=data.get('full_name'),
        dob=data.get('dob'),
        phone=data.get('phone'),
        selfie_file_id=data.get('selfie'),
        id_file_id=data.get('license'),
    )
    await db.upsert_driver(
        user_id,
        exp_years=data.get('exp'),
        car_brand=data.get('car_brand'),
        car_year=data.get('car_year'),
        car_capacity_kg=data.get('capacity'),
        car_body=data.get('car_body'),
    )
    await state.clear()
    await state.set_state(DriverMenu.idle)
    await message.answer(await T(user_id, 'reg_complete'))
    menu = await driver_menu_kb_local(user_id)
    await message.answer(await T(user_id, 'menu'), reply_markup=menu)

@router.message(DriverMenu.idle, F.text == 'Start')
async def driver_start(message: Message, state: FSMContext):
    await state.set_state(DriverStart.mode)
    kb = await start_filter_kb_local(message.from_user.id)
    await message.answer(
        await T(message.from_user.id, "choose_request_filter"),
        reply_markup=kb,
    )

@router.message(DriverStart.mode, F.text == 'All available requests')
async def start_all(message: Message, state: FSMContext):
    await db.set_driver_settings(message.from_user.id, mode="all")
    orders = await match.orders_for_driver(message.from_user.id)
    for order in orders:
        text = f"Order #{order['id']} from {order['from_place']} to {order['to_place']} weight {order['weight_kg']}kg"
        kb = await accept_kb_local(message.from_user.id, order["id"])
        await message.answer(text, reply_markup=kb)
    await state.set_state(DriverMenu.idle)
    menu = await driver_menu_kb_local(message.from_user.id)
    await message.answer(await T(message.from_user.id, "menu"), reply_markup=menu)

@router.message(DriverStart.mode, F.text == 'Nearby')
async def start_nearby(message: Message, state: FSMContext):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        types.KeyboardButton(
            await T(message.from_user.id, "share_location"), request_location=True
        )
    )
    await state.set_state(DriverStart.location)
    await message.answer(
        await T(message.from_user.id, "send_location"), reply_markup=kb
    )

@router.message(DriverStart.location, F.location)
async def receive_location(message: Message, state: FSMContext):
    loc = message.location
    await db.set_driver_settings(message.from_user.id, mode='nearby', lat=loc.latitude, lon=loc.longitude)
    orders = await match.orders_for_driver(message.from_user.id)
    for order in orders:
        text = f"Order #{order['id']} from {order['from_place']} to {order['to_place']} weight {order['weight_kg']}kg"
        kb = await accept_kb_local(message.from_user.id, order['id'])
        await message.answer(text, reply_markup=kb)
    await state.set_state(DriverMenu.idle)
    menu = await driver_menu_kb_local(message.from_user.id)
    await message.answer(await T(message.from_user.id, 'menu'), reply_markup=menu)

@router.message(DriverStart.mode, F.text == 'Back')
async def start_back(message: Message, state: FSMContext):
    await state.set_state(DriverMenu.idle)
    menu = await driver_menu_kb_local(message.from_user.id)
    await message.answer(await T(message.from_user.id, 'menu'), reply_markup=menu)

@router.message(DriverMenu.idle, F.text == 'Settings')
async def driver_settings(message: Message, state: FSMContext):
    await state.set_state(DriverSettings.choosing)
    kb = await settings_kb_local(message.from_user.id)
    await message.answer(await T(message.from_user.id, 'settings'), reply_markup=kb)

@router.message(DriverSettings.choosing, F.text == 'Back')
async def settings_back(message: Message, state: FSMContext):
    await state.set_state(DriverMenu.idle)
    menu = await driver_menu_kb_local(message.from_user.id)
    await message.answer(await T(message.from_user.id, 'menu'), reply_markup=menu)

@router.message(DriverSettings.choosing, F.text == 'Profile')
async def show_profile(message: Message, state: FSMContext):
    user = await db.fetch_user(message.from_user.id)
    driver = await db.fetch_driver(message.from_user.id)
    name_label = (await T(message.from_user.id, 'full_name_prompt')).rstrip('?')
    phone_label = await T(message.from_user.id, 'phone_prompt')
    car_brand_label = await T(message.from_user.id, 'car_brand_prompt')
    car_year_label = await T(message.from_user.id, 'car_year_prompt')
    car_capacity_label = await T(message.from_user.id, 'car_capacity_prompt')
    car_body_label = await T(message.from_user.id, 'car_body_prompt')
    text = (
        f"{name_label}: {user['full_name']}\n"
        f"{phone_label}: {user['phone']}\n"
        f"{car_brand_label}: {driver['car_brand']}\n"
        f"{car_year_label}: {driver['car_year']}\n"
        f"{car_capacity_label}: {driver['car_capacity_kg']}\n"
        f"{car_body_label}: {driver['car_body']}"
    )
    await state.set_state(DriverSettings.profile)
    kb = await profile_inline_kb(message.from_user.id, 'driver')
    await message.answer(text, reply_markup=kb)

@router.callback_query(DriverSettings.profile, F.data == 'edit_phone')
async def change_phone_prompt(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(DriverSettings.change_phone)
    kb = await contact_kb(call.from_user.id)
    await call.message.answer(await T(call.from_user.id, 'phone_prompt'), reply_markup=kb)
    await call.answer()

@router.message(DriverSettings.change_phone)
async def change_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    await db.upsert_user(message.from_user.id, phone=phone)
    await message.answer(await T(message.from_user.id, 'phone_updated'))
    await state.set_state(DriverSettings.choosing)
    kb = await settings_kb_local(message.from_user.id)
    await message.answer(await T(message.from_user.id, 'settings'), reply_markup=kb)

@router.callback_query(DriverSettings.profile, F.data == 'edit_car')
async def change_car_prompt(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(DriverSettings.change_car_brand)
    await call.message.answer(await T(call.from_user.id, 'car_brand_prompt'))
    await call.answer()

@router.message(DriverSettings.change_car_brand)
async def change_car_brand(message: Message, state: FSMContext):
    await state.update_data(car_brand=message.text)
    await state.set_state(DriverSettings.change_car_year)
    await message.answer(await T(message.from_user.id, 'car_year_prompt'))

@router.message(DriverSettings.change_car_year)
async def change_car_year(message: Message, state: FSMContext):
    await state.update_data(car_year=message.text)
    await state.set_state(DriverSettings.change_car_capacity)
    await message.answer(await T(message.from_user.id, 'car_capacity_prompt'))

@router.message(DriverSettings.change_car_capacity)
async def change_car_capacity(message: Message, state: FSMContext):
    await state.update_data(car_capacity=message.text)
    await state.set_state(DriverSettings.change_car_body)
    await message.answer(await T(message.from_user.id, 'car_body_prompt'))

@router.message(DriverSettings.change_car_body)
async def change_car_body(message: Message, state: FSMContext):
    data = await state.get_data()
    await db.upsert_driver(
        message.from_user.id,
        car_brand=data.get('car_brand'),
        car_year=data.get('car_year'),
        car_capacity_kg=data.get('car_capacity'),
        car_body=message.text,
    )
    await message.answer(await T(message.from_user.id, 'car_info_updated'))
    await state.set_state(DriverSettings.choosing)
    kb = await settings_kb_local(message.from_user.id)
    await message.answer(await T(message.from_user.id, 'settings'), reply_markup=kb)

@router.message(DriverSettings.profile, F.text == 'Back')
async def profile_back(message: Message, state: FSMContext):
    await state.set_state(DriverSettings.choosing)
    kb = await settings_kb_local(message.from_user.id)
    await message.answer(await T(message.from_user.id, 'settings'), reply_markup=kb)

@router.message(DriverSettings.choosing, F.text == 'History of orders')
async def history_orders(message: Message, state: FSMContext):
    orders = await db.fetch_orders_for_user(message.from_user.id, 'driver')
    if not orders:
        await message.answer(await T(message.from_user.id, 'history_empty'))
        return
    lines = [
        f"#{o['id']} • {o['from_place']} → {o['to_place']} • {await T(message.from_user.id, 'status_' + o['status'])}"
        for o in orders
    ]
    await message.answer('\n'.join(lines))
