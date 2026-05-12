import sys
import glob
import importlib
from pathlib import Path
from pyrogram import idle
import logging
import logging.config
import asyncio
from datetime import date, datetime
import pytz

# Logging setup
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)

from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import *
from utils import temp
from typing import Union, Optional, AsyncGenerator
from pyrogram import types
from Script import script
from aiohttp import web
from plugins import load_plugins  # 🔥 NEW PLUGIN LOADER
from webapp import web_server, check_expired_premium  # 🔥 PREMIUM CHECKER

# Initialize bot
JisshuBot = Client("JisshuBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
loop = asyncio.get_event_loop()

ppath = "plugins/*.py"
files = glob.glob(ppath)

async def Jisshu_start():
    """Main startup with premium system"""
    print('\n🚀 Initializing Movie Bot + Premium System')
    
    # Start bot & get info
    bot_info = await JisshuBot.get_me()
    JisshuBot.username = bot_info.username
    
    # 🔥 LOAD PLUGINS WITH PREMIUM ✅
    plugins = load_plugins(JisshuBot)
    print(f"✅ Loaded {len(plugins)} plugins including Premium!")
    
    # Initialize clients & database
    await initialize_clients()
    await Media.ensure_indexes()
    
    # Load banned users/chats
    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    
    # Bot info
    me = await JisshuBot.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    JisshuBot.username = '@' + me.username
    
    # Log startup
    logging.info(f"{me.first_name} | Pyrogram v{__version__} (Layer {layer}) | {JisshuBot.username}")
    logging.info(script.LOGO)
    
    # Send restart message
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")
    
    await JisshuBot.send_message(
        chat_id=LOG_CHANNEL, 
        text=script.RESTART_TXT.format(today, time)
    )
    
    # 🔥 START PREMIUM EXPIRY CHECKER ✅
    asyncio.create_task(check_expired_premium(JisshuBot))
    print("⏰ Premium expiry checker started!")
    
    # 🔥 START WEB SERVER ✅
    web_app = await web_server()
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"🌐 Web server running on port {PORT}")
    
    # Import & load plugins manually (legacy support)
    for name in files:
        try:
            with open(name) as a:
                patt = Path(a.name)
                plugin_name = patt.stem.replace(".py", "")
                plugins_dir = Path(f"plugins/{plugin_name}.py")
                import_path = "plugins.{}".format(plugin_name)
                spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
                load = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(load)
                sys.modules["plugins." + plugin_name] = load
                print(f"📦 Legacy plugin: {plugin_name}")
        except Exception as e:
            print(f"⚠️ Skipped {name}: {e}")
    
    # Heroku ping
    if ON_HEROKU:
        asyncio.create_task(ping_server())
    
    print("\n🤖 Bot + Premium System FULLY STARTED!")
    print("💎 Commands ready: /plan, /myplan, /add_premium")
    print("🔍 Search with premium checks active!")
    
    # Keep alive
    await idle()

async def stop_handler():
    """Graceful shutdown"""
    print("\n👋 Shutting down gracefully...")
    await JisshuBot.stop()

if __name__ == '__main__':
    try:
        loop.run_until_complete(Jisshu_start())
    except KeyboardInterrupt:
        print('🛑 Bot stopped by user')
        asyncio.run(stop_handler())
    except Exception as e:
        print(f'💥 Fatal error: {e}')
        asyncio.run(stop_handler())
