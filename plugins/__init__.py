from aiohttp import web
from .route import routes
from asyncio import sleep
from datetime import datetime
import pytz
from database.users_chats_db import db
from info import LOG_CHANNEL

async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app

async def check_expired_premium(client):
    """Auto remove expired premium & notify users"""
    while True:
        try:
            # Get current time in IST
            ist_tz = pytz.timezone('Asia/Kolkata')
            current_time = datetime.now(ist_tz)
            
            # Find expired premium users
            expired_users = []
            async for user in db.users.find({
                "is_premium": True,
                "premium_expire": {"$lt": current_time}
            }).limit(50):  # Limit to avoid overload
                expired_users.append(user)
            
            print(f"🔍 Found {len(expired_users)} expired premium users")
            
            for user_data in expired_users:
                user_id = user_data["id"]
                
                # Remove premium access
                await db.remove_premium_user(user_id)
                
                try:
                    # Get user info
                    user = await client.get_users(user_id)
                    
                    # Send expiry message to user
                    await client.send_message(
                        chat_id=user_id,
                        text=f"""👋 <b>ʜᴇʏ {user.mention}!</b>

❌ <b>ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss ʜᴀs <u>ᴇxᴘɪʀᴇᴅ</u>!</b>

⏰ <b>Expired:</b> `{user_data.get('premium_expire', current_time).strftime('%d/%m/%Y %I:%M %p')}`

💎 <b>ᴡᴀɴᴛ ᴘʀᴇᴍɪᴜᴍ ᴀɢᴀɪɴ?</b>
- /plan - View all plans
- Direct files (No ads)
- High speed downloads

<b>ᴛʜᴀɴᴋ ʏᴏᴜ ꜰᴏʀ ᴜsɪɴɢ ᴏᴜʀ sᴇʀᴠɪᴄᴇ 😊</b>""",
                        disable_web_page_preview=True
                    )
                    
                    # Log to admin channel
                    if LOG_CHANNEL:
                        expire_time = user_data.get('premium_expire', current_time).strftime('%d/%m/%Y %I:%M %p')
                        await client.send_message(
                            LOG_CHANNEL,
                            f"""#Premium_Expired ✅

👤 <b>User:</b> [{user.first_name}](tg://user?id={user_id})
🆔 <b>ID:</b> `{user_id}`
⏰ <b>Expired:</b> `{expire_time}`
📊 <b>Checked:</b> {len(expired_users)} users"""
                        )
                        
                except Exception as e:
                    print(f"❌ Failed to notify {user_id}: {e}")
                
                # 2 sec delay between users
                await sleep(2)
            
            print("✅ Premium expiry check completed")
            
        except Exception as e:
            print(f"❌ Premium checker error: {e}")
        
        # Check every 30 minutes
        await sleep(1800)  # 30 minutes = 1800 seconds

# plugins/__init__.py
"""
Auto Plugin Loader for Movie Bot
Loads all .py files in plugins folder
"""
import os
import importlib
import sys
from pyrogram import Client
from info import ADMINS

__plugins__ = {}

def load_plugins(app: Client):
    """Load all plugins automatically"""
    plugin_dir = os.path.dirname(__file__)
    
    for filename in os.listdir(plugin_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            plugin_name = filename[:-3]  # Remove .py extension
            
            try:
                # Import plugin
                plugin_module = importlib.import_module(f".{plugin_name}", "plugins")
                __plugins__[plugin_name] = plugin_module
                
                # Add bot owner to ADMINS if not present
                if app.me.id not in ADMINS:
                    ADMINS.append(app.me.id)
                
                print(f"✅ Loaded: {plugin_name}")
                
            except Exception as e:
                print(f"❌ Failed to load {plugin_name}: {e}")
    
    print(f"🚀 Loaded {len(__plugins__)} plugins!")
    print("💎 Premium commands ready: /plan, /myplan")
    return __plugins__

# Premium quick check function (use in search handlers)
async def is_premium_active(user_id):
    """Quick premium check for search handlers"""
    from database.users_chats_db import db
    return await db.is_premium_user(user_id)

# Auto-run on import
def init_plugins(app):
    """Initialize plugins"""
    return load_plugins(app)
