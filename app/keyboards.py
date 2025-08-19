from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from .i18n import T

lang_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Uzbek"), KeyboardButton("Russian"), KeyboardButton("English")
)
auth_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Log in"), KeyboardButton("Sign up")
)
role_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Driver"), KeyboardButton("Consumer")
)
driver_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Start"), KeyboardButton("Settings"), KeyboardButton("Support")
)
consumer_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Find a car"), KeyboardButton("Settings"), KeyboardButton("Support")
)
support_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Suggestions"), KeyboardButton("Complaints"), KeyboardButton("Call center"), KeyboardButton("Back")
)
settings_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("History of orders"), KeyboardButton("Profile"), KeyboardButton("Back")
)
start_filter_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("All available requests"), KeyboardButton("Nearby"), KeyboardButton("Back")
)
additional_options_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Refrigerated"), KeyboardButton("Flatbed"), KeyboardButton("Curtainsider"),
    KeyboardButton("Box"), KeyboardButton("Tanker"), KeyboardButton("Dump"),
    KeyboardButton("Container"), KeyboardButton("Insulated"), KeyboardButton("Back")
)
driver_profile_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Change phone"), KeyboardButton("Change car"), KeyboardButton("Back")
)
consumer_profile_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Change phone"), KeyboardButton("Back")
)


async def accept_kb_local(user_id: int, order_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(await T(user_id, "accept"), callback_data=f"accept:{order_id}"))
    return kb


async def confirm_arrival_kb(user_id: int, order_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(
            await T(user_id, "confirm_arrival_loading"), callback_data=f"confirm_arrival:{order_id}"
        )
    )
    return kb


async def start_delivery_kb(user_id: int, order_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(
            await T(user_id, "start_delivery"), callback_data=f"start_delivery:{order_id}"
        )
    )
    return kb


async def driver_arrived_kb(user_id: int, order_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(
            await T(user_id, "driver_arrived"), callback_data=f"driver_arrived:{order_id}"
        )
    )
    return kb


async def confirm_delivery_kb(user_id: int, order_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(
            await T(user_id, "confirm_delivery"), callback_data=f"confirm_delivery:{order_id}"
        )
    )
    return kb


async def driver_menu_kb_local(user_id: int) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton(await T(user_id, 'start')),
        KeyboardButton(await T(user_id, 'settings')),
        KeyboardButton(await T(user_id, 'support')),
    )
    return kb


async def settings_kb_local(user_id: int) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton(await T(user_id, 'history_orders')),
        KeyboardButton(await T(user_id, 'profile')),
        KeyboardButton(await T(user_id, 'back')),
    )
    return kb


async def support_kb_local(user_id: int) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton(await T(user_id, 'suggestions')),
        KeyboardButton(await T(user_id, 'complaints')),
        KeyboardButton(await T(user_id, 'call_center')),
        KeyboardButton(await T(user_id, 'back')),
    )
    return kb


async def start_filter_kb_local(user_id: int) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton(await T(user_id, 'all_requests')),
        KeyboardButton(await T(user_id, 'nearby')),
        KeyboardButton(await T(user_id, 'back')),
    )
    return kb


async def driver_profile_kb_local(user_id: int) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton(await T(user_id, 'change_phone')),
        KeyboardButton(await T(user_id, 'change_car')),
        KeyboardButton(await T(user_id, 'back')),
    )
    return kb


async def contact_kb(user_id: int) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton(await T(user_id, 'phone_prompt'), request_contact=True))
    return kb


async def order_search_kb_local(user_id: int) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(
        KeyboardButton(await T(user_id, 'find_car_button')),
        KeyboardButton(await T(user_id, 'additional_options_prompt')),
    )
    return kb


async def body_types_kb_local(user_id: int) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(
        KeyboardButton(await T(user_id, 'body_refrigerated')),
        KeyboardButton(await T(user_id, 'body_flatbed')),
        KeyboardButton(await T(user_id, 'body_curtainsider')),
        KeyboardButton(await T(user_id, 'body_box')),
        KeyboardButton(await T(user_id, 'body_tanker')),
        KeyboardButton(await T(user_id, 'body_dump')),
        KeyboardButton(await T(user_id, 'body_container')),
        KeyboardButton(await T(user_id, 'body_insulated')),
    )
    return kb


async def profile_inline_kb(user_id: int, role: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(
            await T(user_id, 'change_phone'), callback_data='edit_phone'
        )
    )
    if role == 'driver':
        kb.add(
            InlineKeyboardButton(
                await T(user_id, 'change_car'), callback_data='edit_car'
            )
        )
    return kb
