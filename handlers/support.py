from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.config import ADMIN_TELEGRAM_ID, CALL_CENTER
from app.keyboards import support_kb_local, driver_menu_kb_local, consumer_menu_kb_local
from app.i18n import T
from app import db
from .drivers import DriverMenu
from .consumers import ConsumerMenu

router = Router()


class SupportState(StatesGroup):
    choosing = State()
    typing = State()


@router.message(DriverMenu.idle | ConsumerMenu.idle)
async def support_menu(message: Message, state: FSMContext):
    if message.text != await T(message.from_user.id, 'support'):
        return
    await state.set_state(SupportState.choosing)
    kb = await support_kb_local(message.from_user.id)
    await message.answer(await T(message.from_user.id, 'support_prompt'), reply_markup=kb)


@router.message(SupportState.choosing)
async def support_choose(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text
    if text == await T(user_id, 'back'):
        user = await db.fetch_user(user_id)
        if user['role'] == 'driver':
            await state.set_state(DriverMenu.idle)
            kb = await driver_menu_kb_local(user_id)
        else:
            await state.set_state(ConsumerMenu.idle)
            kb = await consumer_menu_kb_local(user_id)
        await message.answer(await T(user_id, 'menu'), reply_markup=kb)
        return
    if text == await T(user_id, 'call_center'):
        await message.answer(CALL_CENTER)
        return
    suggestions = await T(user_id, 'suggestions')
    complaints = await T(user_id, 'complaints')
    if text in {suggestions, complaints}:
        kind = 'suggestion' if text == suggestions else 'complaint'
        await state.update_data(kind=kind)
        await state.set_state(SupportState.typing)
        prompt = 'send_suggestion' if kind == 'suggestion' else 'send_complaint'
        await message.answer(await T(user_id, prompt))


@router.message(SupportState.typing)
async def save_support(message: Message, state: FSMContext):
    data = await state.get_data()
    kind = data.get('kind')
    await db.save_support_msg(message.from_user.id, kind, message.text)
    await message.bot.send_message(
        ADMIN_TELEGRAM_ID, f"{kind} from {message.from_user.id}: {message.text}"
    )
    await message.answer(await T(message.from_user.id, 'support_saved'))
    user = await db.fetch_user(message.from_user.id)
    if user['role'] == 'driver':
        await state.set_state(DriverMenu.idle)
        kb = await driver_menu_kb_local(message.from_user.id)
    else:
        await state.set_state(ConsumerMenu.idle)
        kb = await consumer_menu_kb_local(message.from_user.id)
    await message.answer(await T(message.from_user.id, 'menu'), reply_markup=kb)
