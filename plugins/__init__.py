# plugins/__init__.py
import os
import importlib
from pyrogram import Client
from info import ADMINS

__plugins__ = {}

def load_plugins(app: Client):
    """Auto load all plugins"""
    plugin_dir = os.path.dirname(__file__)
    
    for filename in os.listdir(plugin_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            plugin_name = filename[:-3]
            try:
                plugin_module = importlib.import_module(f".{plugin_name}", "plugins")
                __plugins__[plugin_name] = plugin_module
                ADMINS.append(app.me.id)
                print(f"✅ Loaded: {plugin_name}")
            except Exception as e:
                print(f"❌ Failed {plugin_name}: {e}")
    
    print(f"🚀 {len(__plugins__)} plugins loaded!")
    return __plugins__

async def is_premium_active(user_id):
    """Quick premium check"""
    from database.users_chats_db import db
    return await db.is_premium_user(user_id)
