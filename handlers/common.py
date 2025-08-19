from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from app.keyboards import lang_kb, auth_kb
from app.i18n import t
from .auth import LanguageState, AuthState

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(LanguageState.choosing)
    await message.answer(t('select_language'), reply_markup=lang_kb)

@router.message(LanguageState.choosing)
async def choose_lang(message: Message, state: FSMContext):
    lang_map = {'english': 'en', 'russian': 'ru', 'uzbek': 'uz'}
    lang = lang_map.get(message.text.lower(), 'en')
    await state.update_data(lang=lang)
    await state.set_state(AuthState.choosing)
    await message.answer(t('login_or_register', lang), reply_markup=auth_kb)
