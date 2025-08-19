from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from app import db
from app.i18n import T
from app.keyboards import (
    settings_kb_local,
    contact_kb,
    profile_inline_kb,
)
from app.validators import is_valid_date

router = Router()


async def consumer_menu_kb_local(user_id: int) -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        types.KeyboardButton(await T(user_id, "settings")),
        types.KeyboardButton(await T(user_id, "support")),
        types.KeyboardButton(await T(user_id, "find_car")),
    )
    return kb


class ConsumerMenu(StatesGroup):
    idle = State()


class ConsumerSettings(StatesGroup):
    choosing = State()
    profile = State()
    change_phone = State()


class FindCar(StatesGroup):
    from_where = State()
    to_where = State()
    load_date = State()
    load_time = State()
    ship_date = State()
    ship_time = State()
    weight = State()
    body_type = State()


class ConsumerReg(StatesGroup):
    full_name = State()
    dob = State()
    phone = State()
    selfie = State()
    passport = State()


@router.message(F.text == '/consumer_reg')
async def consumer_reg_start(message: Message, state: FSMContext):
    await state.set_state(ConsumerReg.full_name)
    await message.answer(await T(message.from_user.id, 'full_name_prompt'))


@router.message(ConsumerReg.full_name)
async def reg_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(ConsumerReg.dob)
    await message.answer(await T(message.from_user.id, 'dob_prompt'))


@router.message(ConsumerReg.dob)
async def reg_dob(message: Message, state: FSMContext):
    if not is_valid_date(message.text):
        await message.answer(await T(message.from_user.id, 'invalid_date'))
        return
    await state.update_data(dob=message.text)
    await state.set_state(ConsumerReg.phone)
    kb = await contact_kb(message.from_user.id)
    await message.answer(await T(message.from_user.id, 'phone_prompt'), reply_markup=kb)


@router.message(ConsumerReg.phone, F.contact)
async def reg_phone_contact(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await state.set_state(ConsumerReg.selfie)
    await message.answer(await T(message.from_user.id, 'selfie_passport_prompt'))


@router.message(ConsumerReg.phone)
async def reg_phone_text(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(ConsumerReg.selfie)
    await message.answer(await T(message.from_user.id, 'selfie_passport_prompt'))


@router.message(ConsumerReg.selfie, F.photo)
async def reg_selfie(message: Message, state: FSMContext):
    await state.update_data(selfie=message.photo[-1].file_id)
    await state.set_state(ConsumerReg.passport)
    await message.answer(await T(message.from_user.id, 'passport_prompt'))


@router.message(ConsumerReg.passport, F.photo)
async def reg_finish(message: Message, state: FSMContext):
    await state.update_data(passport=message.photo[-1].file_id)
    data = await state.get_data()
    user_id = message.from_user.id
    await db.upsert_user(
        user_id,
        role='consumer',
        full_name=data.get('full_name'),
        dob=data.get('dob'),
        phone=data.get('phone'),
        selfie_file_id=data.get('selfie'),
        id_file_id=data.get('passport'),
    )
    await state.clear()
    await state.set_state(ConsumerMenu.idle)
    menu = await consumer_menu_kb_local(user_id)
    await message.answer(await T(user_id, 'reg_complete'))
    await message.answer(await T(user_id, 'menu'), reply_markup=menu)


@router.message(ConsumerMenu.idle)
async def consumer_settings(message: Message, state: FSMContext):
    if message.text != await T(message.from_user.id, 'settings'):
        return
    await state.set_state(ConsumerSettings.choosing)
    kb = await settings_kb_local(message.from_user.id)
    await message.answer(await T(message.from_user.id, 'settings'), reply_markup=kb)

@router.message(ConsumerSettings.choosing)
async def consumer_settings_back(message: Message, state: FSMContext):
    if message.text != await T(message.from_user.id, 'back'):
        if message.text == await T(message.from_user.id, 'profile'):
            return await consumer_profile(message, state)
        if message.text == await T(message.from_user.id, 'history_orders'):
            return await consumer_history(message, state)
        return
    await state.set_state(ConsumerMenu.idle)
    menu = await consumer_menu_kb_local(message.from_user.id)
    await message.answer(await T(message.from_user.id, 'menu'), reply_markup=menu)

async def consumer_profile(message: Message, state: FSMContext):
    user = await db.fetch_user(message.from_user.id)
    name_label = (await T(message.from_user.id, 'full_name_prompt')).rstrip('?')
    phone_label = await T(message.from_user.id, 'phone_prompt')
    text = f"{name_label}: {user['full_name']}\n{phone_label}: {user['phone']}"
    await state.set_state(ConsumerSettings.profile)
    kb = await profile_inline_kb(message.from_user.id, 'consumer')
    await message.answer(text, reply_markup=kb)

@router.callback_query(ConsumerSettings.profile, F.data == 'edit_phone')
async def consumer_change_phone_prompt(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(ConsumerSettings.change_phone)
    kb = await contact_kb(call.from_user.id)
    await call.message.answer(await T(call.from_user.id, 'phone_prompt'), reply_markup=kb)
    await call.answer()

@router.message(ConsumerSettings.change_phone)
async def consumer_change_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    await db.upsert_user(message.from_user.id, phone=phone)
    await message.answer(await T(message.from_user.id, 'phone_updated'))
    await state.set_state(ConsumerSettings.choosing)
    kb = await settings_kb_local(message.from_user.id)
    await message.answer(await T(message.from_user.id, 'settings'), reply_markup=kb)

@router.message(ConsumerSettings.profile)
async def consumer_profile_back(message: Message, state: FSMContext):
    if message.text != await T(message.from_user.id, 'back'):
        return
    await state.set_state(ConsumerSettings.choosing)
    kb = await settings_kb_local(message.from_user.id)
    await message.answer(await T(message.from_user.id, 'settings'), reply_markup=kb)

async def consumer_history(message: Message, state: FSMContext):
    orders = await db.fetch_orders_for_user(message.from_user.id, 'consumer')
    if not orders:
        await message.answer(await T(message.from_user.id, 'no_orders_yet'))
        return
    lines = [
        f"#{o['id']} • {o['from_place']} → {o['to_place']} • {await T(message.from_user.id, 'status_' + o['status'])}"
        for o in orders
    ]
    await message.answer('\n'.join(lines))
