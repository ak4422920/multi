import asyncio
import logging
import sys
import os
from aiohttp import web  # Render ke liye zaroori hai
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import BotCommand
from config import BOT_TOKEN

# 1. Feature handlers import
from handlers import start, downloader, translator

# --- RENDER DUMMY SERVER ---
# Ye function Render ko batata hai ki bot chalu hai
async def handle(request):
    return web.Response(text="🚀 @AkMovieVerse Bot is Running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render hamesha port 10000 mangta hai free tier pe
    site = web.TCPSite(runner, "0.0.0.0", 10000)
    await site.start()
    logging.info("🌐 Dummy Web Server started on port 10000")

# --- MAIN BOT LOGIC ---
async def main():
    # Logging setup
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout
    )
    logger = logging.getLogger("MultiBot")

    # Render testing ke liye background server start karna
    asyncio.create_task(start_web_server())

    # Cloud session management
    session = AiohttpSession()
    
    bot = Bot(
        token=BOT_TOKEN, 
        session=session,
        default=DefaultBotProperties(parse_mode='HTML')
    )
    
    dp = Dispatcher()

    # 2. Blue Menu Button setup
    try:
        await bot.set_my_commands([
            BotCommand(command="start", description="🏠 Main Menu"),
            BotCommand(command="dl", description="📥 Universal Video Downloader"),
            BotCommand(command="tr", description="🌍 Translate Text"),
            BotCommand(command="langs", description="📋 Language Codes")
        ])
        logger.info("✅ Bot commands registered successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to register commands: {e}")

    # 3. Register Routers
    dp.include_router(start.router)
    dp.include_router(downloader.router)
    dp.include_router(translator.router)

    # 4. Drop Pending Updates
    logger.info("🧹 Clearing old messages (dropping pending updates)...")
    await bot.delete_webhook(drop_pending_updates=True)

    # 5. Startup Confirmation
    me = await bot.get_me()
    print("-" * 30)
    print(f"🚀 {me.full_name} (@{me.username}) is now LIVE for Testing!")
    print(f"📂 Handlers Active: Start, Downloader, Translator")
    print("-" * 30)

    try:
        # Start polling
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"⚠️ Critical Error during polling: {e}")
    finally:
        # 6. Safety Close
        logger.info("📴 Shutting down session...")
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 Bot stopped manually.")