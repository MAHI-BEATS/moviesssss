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
    while True:
        try:
            ist_tz = pytz.timezone('Asia/Kolkata')
            current_time = datetime.now(ist_tz)
            
            # Find expired users
            expired_users = []
            async for user in db.users.find({
                "is_premium": True,
                "premium_expire": {"$lt": current_time}
            }).limit(20):
                expired_users.append(user)
            
            for user_data in expired_users:
                user_id = user_data["id"]
                await db.remove_premium_user(user_id)
                
                try:
                    user = await client.get_users(user_id)
                    await client.send_message(
                        user_id,
                        f"""👋 <b>Premium Expired!</b>

❌ Your premium has expired!
⏰ `{user_data.get('premium_expire').strftime('%d/%m/%Y %I:%M %p')}`

💎 Get new plan: /plan""",
                        disable_web_page_preview=True
                    )
                    
                    if LOG_CHANNEL:
                        await client.send_message(
                            LOG_CHANNEL,
                            f"#Premium_Expired\n👤 [{user.first_name}](tg://user?id={user_id})\n🆔 `{user_id}`"
                        )
                except:
                    pass
                
                await sleep(1)
            
        except Exception as e:
            print(f"Premium checker error: {e}")
        
        await sleep(1800)  # 30 mins
