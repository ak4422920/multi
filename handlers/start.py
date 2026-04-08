from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    # 1. More stable image link + Try/Except to prevent crashes
    banner_url = "https://img.freepik.com/free-vector/modern-desktop-concept-illustration_114360-1159.jpg"
    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📥 Download Short", callback_data="help_short"))
    builder.row(types.InlineKeyboardButton(text="🌍 Translate", callback_data="help_tr"))
    builder.row(types.InlineKeyboardButton(text="📋 Language Codes", callback_data="show_langs"))

    welcome_text = (
        f"<b>Welcome, {message.from_user.first_name}!</b> 🚀\n\n"
        "I am your <b>Multi-Tool Assistant</b>. I can help you download videos "
        "and translate languages instantly.\n\n"
        "<i>Click a button below for instructions!</i>"
    )

    try:
        await message.answer_photo(
            photo=banner_url,
            caption=welcome_text,
            reply_markup=builder.as_markup()
        )
    except Exception:
        # If the photo fails, we send text so the bot doesn't stop
        await message.answer(welcome_text, reply_markup=builder.as_markup())

# --- BUTTON LOGIC (CALLBACK HANDLERS) ---

@router.callback_query(F.data == "help_short")
async def help_short(callback: types.CallbackQuery):
    text = (
        "<b>📥 How to Download Shorts</b>\n\n"
        "1. Go to YouTube Shorts.\n"
        "2. Copy the link of the video.\n"
        "3. Type: <code>/short [paste-link]</code>\n\n"
        "<i>Example: /short https://youtube.com/shorts/...</i>"
    )
    await callback.message.answer(text)
    await callback.answer() # Removes the "loading" state from the button

@router.callback_query(F.data == "help_tr")
async def help_tr(callback: types.CallbackQuery):
    text = (
        "<b>🌍 How to Translate</b>\n\n"
        "Use the <code>/tr</code> command followed by the language code.\n\n"
        "<b>Format:</b> <code>/tr [code] [text]</code>\n"
        "<b>Example:</b> <code>/tr hi Hello Friend</code>"
    )
    await callback.message.answer(text)
    await callback.answer()

@router.callback_query(F.data == "show_langs")
async def help_langs(callback: types.CallbackQuery):
    # This just triggers the existing /langs command logic
    from handlers.translator import show_languages
    await show_languages(callback.message)
    await callback.answer()