from aiogram import Router, types
from aiogram.filters import Command
from deep_translator import GoogleTranslator

router = Router()

@router.message(Command("langs"))
async def show_languages(message: types.Message):
    menu = (
        "<b>🌍 Supported Language Codes</b>\n"
        "<i>Tap a code to copy it!</i>\n\n"
        
        "<b>🏙️ Global Favorites:</b>\n"
        "• <code>en</code> (English)\n"
        "• <code>es</code> (Spanish)\n"
        "• <code>fr</code> (French)\n"
        "• <code>zh-CN</code> (Chinese)\n\n"
        
        "<b>🇮🇳 Indian Languages:</b>\n"
        "• <code>hi</code> (Hindi)\n"
        "• <code>bn</code> (Bengali)\n"
        "• <code>te</code> (Telugu)\n"
        "• <code>mr</code> (Marathi)\n"
        "• <code>ta</code> (Tamil)\n"
        "• <code>gu</code> (Gujarati)\n"
        "• <code>kn</code> (Kannada)\n"
        "• <code>ml</code> (Malayalam)\n"
        "• <code>pa</code> (Punjabi)\n\n"

        "<b>🌏 Asia & Middle East:</b>\n"
        "• <code>ar</code> (Arabic)\n"
        "• <code>ja</code> (Japanese)\n"
        "• <code>ko</code> (Korean)\n"
        "• <code>tr</code> (Turkish)\n"
        "• <code>vi</code> (Vietnamese)\n"
        "• <code>th</code> (Thai)\n\n"

        "<b>🇪🇺 Europe:</b>\n"
        "• <code>de</code> (German)\n"
        "• <code>it</code> (Italian)\n"
        "• <code>pt</code> (Portuguese)\n"
        "• <code>ru</code> (Russian)\n"
        "• <code>nl</code> (Dutch)\n\n"
        
        "<b>💡 Usage:</b>\n"
        "<code>/tr [code] [text]</code>"
    )
    await message.answer(menu, parse_mode="HTML")

@router.message(Command("tr"))
async def translate_text(message: types.Message):
    args = message.text.split(maxsplit=2)
    
    if len(args) < 3:
        return await message.answer("❌ <b>Use:</b> /tr [code] [text]\nExample: <code>/tr hi Hello</code>\nTap /langs to see codes.")

    dest_lang = args[1]
    text_to_translate = args[2]

    try:
        translated = GoogleTranslator(source='auto', target=dest_lang).translate(text_to_translate)
        
        response = (
            f"<b>🌐 Translation to {dest_lang.upper()}</b>\n"
            f"────────────────────\n"
            f"📝 <i>{text_to_translate}</i>\n"
            f"✅ <b>{translated}</b>"
        )
        await message.answer(response, parse_mode="HTML")
        
    except Exception:
        await message.answer("❌ <b>Invalid Code.</b> Tap /langs to see the list.")