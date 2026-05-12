from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from info import URL, LOG_CHANNEL
from urllib.parse import quote_plus
from database.users_chats_db import db  # 🔥 PREMIUM CHECK
import script
from Jisshu.util.file_properties import get_name, get_hash, get_media_file_size
from Jisshu.util.human_readable import humanbytes
import humanize
import random
from datetime import datetime

@Client.on_message(filters.private & filters.command("streams"))
async def streams_handler(client: Client, message: Message):
    """Streams handler with premium check"""
    user_id = message.from_user.id
    
    # 🔥 PREMIUM CHECK - Direct access for premium users
    is_premium = await db.is_premium_user(user_id)
    
    # Ask for file
    await message.reply_text(
        "**📤 Send me your video/file to generate streams & download links**"
        + ("\n\n💎 **Premium user - Instant links!**" if is_premium else "")
    )
    
    msg = await client.ask(message.chat.id, "**Send your media file:**")
    
    if not msg.media or msg.media not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.DOCUMENT]:
        await msg.reply("❌ **Please send VIDEO or DOCUMENT only!**")
        return
    
    try:
        # Get file info
        file = getattr(msg, msg.media.value)
        filename = file.file_name or "Unknown"
        filesize = humanbytes(file.file_size)
        fileid = file.file_id
        
        user = await client.get_users(user_id)
        username = user.mention
        user_id_str = str(user_id)
        
        # Forward to log channel & generate links
        log_msg = await client.send_cached_media(
            chat_id=LOG_CHANNEL,
            file_id=fileid,
        )
        
        file_name = quote_plus(get_name(log_msg))
        stream_link = f"{URL}watch/{log_msg.id}?hash={get_hash(log_msg)}"
        download_link = f"{URL}{log_msg.id}?hash={get_hash(log_msg)}"
        
        # Log message in log channel
        log_text = f"""🔗 **New Stream Generated**

👤 **User:** {username} (`{user_id_str}`)
📂 **File:** {file_name}
📦 **Size:** {filesize}
💎 **Premium:** {'✅' if is_premium else '❌'}

<i>Links valid forever!</i>"""
        
        log_buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🚀 Fast DL", url=download_link),
                InlineKeyboardButton("🖥️ Stream", url=stream_link)
            ],
            [InlineKeyboardButton("👤 User Profile", url=f"tg://user?id={user_id}")]
        ])
        
        await log_msg.reply_text(
            log_text,
            reply_markup=log_buttons,
            disable_web_page_preview=True
        )
        
        # User response
        user_text = f"""🎉 **Links Generated Successfully!**

📂 **File Name:** `{file_name}`
📦 **Size:** `{filesize}`
👤 **Generated for:** {username}

"""
        
        if is_premium:
            user_text += "💎 **Premium User - No Limits!**\n\n"
        else:
            user_text += "🔒 **Free User - Upgrade for more features!**\n\n"
        
        user_text += f"""📥 **Download:** `{download_link}`
🖥️ **Stream:** `{stream_link}`

🚨 **Note:** Links won't expire! 🔥"""
        
        user_buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📥 Download", url=download_link),
                InlineKeyboardButton("🖥️ Stream", url=stream_link)
            ],
            [
                InlineKeyboardButton("💎 Get Premium", callback_data="plan"),
                InlineKeyboardButton("📢 Support", url="https://t.me/betabot_hub")
            ]
        ])
        
        await msg.reply_text(
            user_text,
            reply_markup=user_buttons,
            disable_web_page_preview=True,
            quote=True
        )
        
        # Premium upsell for free users
        if not is_premium:
            await asyncio.sleep(3)
            await message.reply_text(
                script.PLAN_TEXT,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💎 View Plans", callback_data="plan")]
                ])
            )
            
    except Exception as e:
        await msg.reply_text(f"❌ **Error generating links:**\n`{str(e)}`")
        print(f"Streams error: {e}")

# Callback for premium upsell
@app.on_callback_query(filters.regex(r"^plan$"))
async def premium_upsell(client: Client, callback: CallbackQuery):
    buttons = [
        [InlineKeyboardButton("💎 1 Day - ₹2", callback_data="plan_1")],
        [InlineKeyboardButton("💎 30 Days - ₹39", callback_data="plan_30")],
        [InlineKeyboardButton("💎 60 Days - ₹59", callback_data="plan_60")],
        [InlineKeyboardButton("📞 Contact", url="https://t.me/betabot_hub")]
    ]
    await callback.edit_message_text(
        script.PLAN_TEXT,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
