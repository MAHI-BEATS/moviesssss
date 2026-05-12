# plugins/search.py - Complete Movie Search with Premium
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from database.users_chats_db import db
import script
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Mock search function - REPLACE with your actual search logic
async def search_movies(query: str):
    """Your actual movie search logic here"""
    # This is example data - replace with real database/search
    return [
        {"title": f"{query} (2023)", "file_id": "example_file_id", "size": "2.1 GB"},
        {"title": f"{query} Hindi Dubbed", "file_id": "example_file_id2", "size": "1.8 GB"}
    ]

@Client.on_message(filters.text & filters.private & ~filters.command(["start", "help", "plan", "myplan"]))
async def search_handler(client: Client, message: Message):
    """Main search handler with premium check"""
    user_id = message.from_user.id
    query = message.text.strip()
    
    if len(query) < 2:
        await message.reply("❌ **Minimum 2 characters required!**")
        return
    
    # 🔥 PREMIUM CHECK - MOST IMPORTANT 🔥
    is_premium = await db.is_premium_user(user_id)
    is_verified = await db.is_user_verified(user_id)
    
    # Loading message
    loading_msg = await message.reply_text("🔍 **Searching movies...**")
    
    try:
        # Search movies (your actual logic)
        results = await search_movies(query)
        
        if not results:
            await loading_msg.edit_text(script.NO_RESULT_TXT)
            return
        
        # 🔥 PREMIUM USER - DIRECT FILES 🔥
        if is_premium:
            await loading_msg.edit_text(
                f"💎 **Premium User - Direct Files!**\n\n"
                f"🎬 **Found {len(results)} results for:** `{query}`"
            )
            
            # Send files directly
            for i, movie in enumerate(results[:5], 1):  # Limit 5 files
                buttons = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📥 Save", callback_data=f"save_{movie['file_id']}")],
                    [InlineKeyboardButton("💎 Renew Plan", callback_data="plan")]
                ])
                await message.reply_cached_media(
                    movie['file_id'],
                    caption=f"**{i}.** {movie['title']}\n📦 {movie['size']}",
                    reply_markup=buttons
                )
                await asyncio.sleep(1)  # Rate limit
            
            await loading_msg.delete()
            return
        
        # ✅ VERIFIED FREE USER - Inline buttons
        if is_verified:
            buttons = []
            for movie in results[:10]:
                buttons.append([InlineKeyboardButton(
                    f"🎬 {movie['title'][:50]}...",
                    callback_data=f"movie_{movie['file_id']}"
                )])
            
            buttons.append([InlineKeyboardButton("💎 Get Premium", callback_data="plan")])
            
            await loading_msg.edit_text(
                f"✅ **{len(results)} results for:** `{query}`\n\n"
                f"🔒 **Free user - Click to get file**\n"
                f"💎 **Premium = Direct files!**",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return
        
        # ❌ NON-VERIFIED USER - Show verification
        buttons = [
            [InlineKeyboardButton("🔗 Verify Now", url="YOUR_VERIFY_LINK")],
            [InlineKeyboardButton("💎 Get Premium", callback_data="plan")],
            [InlineKeyboardButton("📢 Support", url="https://t.me/betabot_hub")]
        ]
        
        await loading_msg.edit_text(
            script.VERIFICATION_TEXT.format(
                message.from_user.first_name,
                message.from_user.mention
            ),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        await loading_msg.edit_text(f"❌ **Search failed:** `{str(e)}`")

# Callback handlers
@Client.on_callback_query(filters.regex(r"^movie_"))
async def movie_callback(client: Client, callback: CallbackQuery):
    """Handle movie selection"""
    user_id = callback.from_user.id
    file_id = callback.data.split("_")[1]
    
    # Premium users get direct file
    if await db.is_premium_user(user_id):
        await callback.message.reply_cached_media(
            file_id,
            caption="💎 **Premium - Direct file!**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 More", callback_data="search_back")]
            ])
        )
    else:
        # Free users get link/ad
        await callback.answer("🔒 Verify first!", show_alert=True)
    
    await callback.answer()

@Client.on_callback_query(filters.regex(r"^plan$"))
async def premium_plan(client: Client, callback: CallbackQuery):
    """Premium upsell"""
    buttons = [
        [InlineKeyboardButton("💎 1 Day - ₹2", callback_data="plan_1")],
        [InlineKeyboardButton("💎 30 Days - ₹39", callback_data="plan_30")],
        [InlineKeyboardButton("💎 60 Days - ₹59", callback_data="plan_60")],
        [InlineKeyboardButton("📞 Contact", url="https://t.me/betabot_hub")]
    ]
    await callback.edit_message_text(script.PLAN_TEXT, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^(plan_\d+|search_back)$"))
async def plan_details(client: Client, callback: CallbackQuery):
    """Plan details"""
    data = callback.data
    if data.startswith("plan_"):
        days = int(data.split("_")[1])
        price = f"₹{days//15 + 2 if days < 30 else days//10 * 2}"
        text = f"**💎 {days} Day Plan**\n💰 **Price:** `{price}`\n\n**UPI:** `yourupi@paytm`\n**Contact owner for payment**"
    else:
        text = "🔍 **Search another movie:**"
    
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="search_back")]]
    await callback.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))

# Group search (optional)
@Client.on_message(filters.text & filters.group & ~filters.command(["start"]))
async def group_search(client: Client, message: Message):
    """Group search with premium check"""
    user_id = message.from_user.id
    
    if await db.is_premium_user(user_id):
        await message.reply("💎 **Premium - Searching...**")
        # Group search logic
    else:
        await message.reply("🔒 **Use PM for search or get premium!**")

print("✅ Search plugin loaded with premium system!")
