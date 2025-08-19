from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from app import db
from app.keyboards import auth_kb, role_kb, driver_menu_kb, consumer_menu_kb
from .drivers import DriverMenu
from .consumers import ConsumerMenu

router = Router()

class LanguageState(StatesGroup):
    choosing = State()

class AuthState(StatesGroup):
    choosing = State()

class DriverReg(StatesGroup):
    full_name = State()
    dob = State()
    phone = State()
    exp = State()
    selfie = State()
    license = State()
    car_brand = State()
    car_year = State()
    car_capacity = State()
    car_body = State()

class ConsumerReg(StatesGroup):
    full_name = State()
    dob = State()
    phone = State()
    selfie = State()
    passport = State()

async def send_menu(message: Message, state: FSMContext, role: str):
    if role == 'driver':
        await state.set_state(DriverMenu.idle)
        await message.answer("Menu", reply_markup=driver_menu_kb)
    else:
        await state.set_state(ConsumerMenu.idle)
        await message.answer("Menu", reply_markup=consumer_menu_kb)

@router.message(AuthState.choosing)
async def auth_choice(message: Message, state: FSMContext):
    choice = message.text.lower()
    user_id = message.from_user.id
    data = await state.get_data()
    lang = data.get('lang', 'en')
    if choice == 'log in':
        user = await db.fetch_user(user_id)
        if user:
            await db.upsert_user(user_id, lang=lang)
            await send_menu(message, state, user['role'])
        else:
            await message.answer("No account. Please sign up.")
    elif choice == 'sign up':
        await message.answer("Register as", reply_markup=role_kb)
    elif choice == 'driver':
        await state.set_state(DriverReg.full_name)
        await state.update_data(role='driver', lang=lang)
        await message.answer("Full name?")
    elif choice == 'consumer':
        await state.set_state(ConsumerReg.full_name)
        await state.update_data(role='consumer', lang=lang)
        await message.answer("Full name?")

@router.message(DriverReg.full_name)
async def driver_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(DriverReg.dob)
    await message.answer("Date of birth dd/mm/yyyy")

@router.message(DriverReg.dob)
async def driver_dob(message: Message, state: FSMContext):
    await state.update_data(dob=message.text)
    await state.set_state(DriverReg.phone)
    await message.answer("Phone number")

@router.message(DriverReg.phone)
async def driver_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(DriverReg.exp)
    await message.answer("Years of experience driving a truck")

@router.message(DriverReg.exp)
async def driver_exp(message: Message, state: FSMContext):
    await state.update_data(exp=message.text)
    await state.set_state(DriverReg.selfie)
    await message.answer("Send selfie with driver's license")

@router.message(DriverReg.selfie, F.photo)
async def driver_selfie(message: Message, state: FSMContext):
    await state.update_data(selfie=message.photo[-1].file_id)
    await state.set_state(DriverReg.license)
    await message.answer("Send photo of driver's license")

@router.message(DriverReg.license, F.photo)
async def driver_license(message: Message, state: FSMContext):
    await state.update_data(license=message.photo[-1].file_id)
    await state.set_state(DriverReg.car_brand)
    await message.answer("Car brand")

@router.message(DriverReg.car_brand)
async def driver_car_brand(message: Message, state: FSMContext):
    await state.update_data(car_brand=message.text)
    await state.set_state(DriverReg.car_year)
    await message.answer("Car year")

@router.message(DriverReg.car_year)
async def driver_car_year(message: Message, state: FSMContext):
    await state.update_data(car_year=message.text)
    await state.set_state(DriverReg.car_capacity)
    await message.answer("Maximum load capacity (kg)")

@router.message(DriverReg.car_capacity)
async def driver_car_capacity(message: Message, state: FSMContext):
    await state.update_data(car_capacity=message.text)
    await state.set_state(DriverReg.car_body)
    await message.answer("Car body type")

@router.message(DriverReg.car_body)
async def driver_finish(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = message.from_user.id
    await db.upsert_user(
        user_id,
        role='driver',
        lang=data.get('lang'),
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
        car_capacity_kg=data.get('car_capacity'),
        car_body=data.get('car_body'),
    )
    await message.answer("Registration completed. Welcome!")
    await send_menu(message, state, 'driver')

@router.message(ConsumerReg.full_name)
async def consumer_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(ConsumerReg.dob)
    await message.answer("Date of birth dd/mm/yyyy")

@router.message(ConsumerReg.dob)
async def consumer_dob(message: Message, state: FSMContext):
    await state.update_data(dob=message.text)
    await state.set_state(ConsumerReg.phone)
    await message.answer("Phone number")

@router.message(ConsumerReg.phone)
async def consumer_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(ConsumerReg.selfie)
    await message.answer("Send selfie with passport")

@router.message(ConsumerReg.selfie, F.photo)
async def consumer_selfie(message: Message, state: FSMContext):
    await state.update_data(selfie=message.photo[-1].file_id)
    await state.set_state(ConsumerReg.passport)
    await message.answer("Send photo of passport")

@router.message(ConsumerReg.passport, F.photo)
async def consumer_finish(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = message.from_user.id
    await db.upsert_user(
        user_id,
        role='consumer',
        lang=data.get('lang'),
        full_name=data.get('full_name'),
        dob=data.get('dob'),
        phone=data.get('phone'),
        selfie_file_id=data.get('selfie'),
        id_file_id=message.photo[-1].file_id,
    )
    await message.answer("Registration completed. Welcome!")
    await send_menu(message, state, 'consumer')
