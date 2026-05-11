from datetime import timedelta, datetime
import pytz
import datetime as dt
from Script import script 
from info import ADMINS, LOG_CHANNEL
from utils import get_seconds
from database.users_chats_db import db 
from pyrogram import Client, filters 
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

@Client.on_message(filters.command("add_premium"))
async def give_premium_cmd_handler(client, message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        await message.reply("**❌ No permission to use this command**")
        return
    
    if len(message.command) == 3:
        try:
            target_id = int(message.command[1])
            user = await client.get_users(target_id)
            duration = message.command[2]        
            seconds = await get_seconds(duration)
            
            if seconds > 0:
                # Calculate expiry time
                expiry_time = dt.datetime.now() + dt.timedelta(seconds=seconds)
                
                # Update database
                await db.update_premium_user(target_id, expiry_time)
                
                # Timezone formatting
                time_zone = dt.datetime.now(pytz.timezone("Asia/Kolkata"))
                current_time_str = time_zone.strftime("%d-%m-%Y\n⏱️ **Join Time:** %I:%M:%S %p")           
                
                # Convert expiry to IST
                expiry_ist = expiry_time.replace(tzinfo=dt.timezone.utc).astimezone(pytz.timezone("Asia/Kolkata"))
                expiry_str = expiry_ist.strftime("%d-%m-%Y\n⏱️ **Expiry:** %I:%M:%S %p")

                # Success message to admin
                await message.reply_text(
                    f"✅ **Premium Added Successfully!**\n\n"
                    f"👤 **User:** {user.mention}\n"
                    f"🆔 **ID:** `{target_id}`\n"
                    f"⏰ **Duration:** `{duration}`\n"
                    f"📅 **Start:** {current_time_str}\n"
                    f"⌛️ **Expiry:** {expiry_str}",
                    disable_web_page_preview=True
                )
                
                # Notify user
                try:
                    await client.send_message(
                        chat_id=target_id,
                        text=f"🎉 **Premium Activated!**\n\n"
                             f"✅ **Duration:** `{duration}`\n"
                             f"📅 **Start:** {current_time_str}\n"
                             f"⌛️ **Expiry:** {expiry_str}\n\n"
                             f"✨ **Enjoy ad-free experience!**",
                        disable_web_page_preview=True
                    )
                except:
                    pass
                
                # Log message
                if LOG_CHANNEL:
                    try:
                        await client.send_message(
                            LOG_CHANNEL, 
                            f"#Added_Premium\n\n"
                            f"👤 **User:** {user.mention}\n"
                            f"🆔 **ID:** `{target_id}`\n"
                            f"⏰ **Duration:** `{duration}`\n"
                            f"📅 **Start:** {current_time_str}\n"
                            f"⌛️ **Expiry:** {expiry_str}",
                            disable_web_page_preview=True
                        )
                    except:
                        pass
                        
            else:
                await message.reply_text("❌ **Invalid time format!**\n**Examples:** `10m`, `2h`, `1d`, `30d`")
        except ValueError:
            await message.reply_text("❌ **Invalid user ID!**")
        except Exception as e:
            await message.reply_text(f"❌ **Error:** `{e}`")
    else:
        await message.reply_text(
            "**Usage:** `/add_premium user_id duration`\n\n"
            "**Examples:**\n"
            "• `/add_premium 123456789 30d`\n"
            "• `/add_premium 123456789 1h`\n"
            "• `/add_premium 123456789 10m`"
        )

@Client.on_message(filters.command("myplan"))
async def check_plans_cmd(client, message):
    user_mention = message.from_user.mention
    user_id = message.from_user.id
    
    if await db.is_premium_user(user_id):         
        remaining_time = await db.get_premium_remaining(user_id)
        
        if remaining_time.total_seconds() > 0:
            days = remaining_time.days
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            formatted_time = f"{days}d {hours}h {minutes}m {seconds}s"
            
            # Calculate exact expiry
            expiry_dt = dt.datetime.now() + remaining_time
            ist_zone = pytz.timezone("Asia/Kolkata")
            expiry_ist = expiry_dt.replace(tzinfo=dt.timezone.utc).astimezone(ist_zone)
            
            expiry_date = expiry_ist.strftime("%d-%m-%Y")
            expiry_time_str = expiry_ist.strftime("%I:%M:%S %p")
            
            buttons = [[InlineKeyboardButton("🔄 Refresh", callback_data="refresh_plan")]]
            
            await message.reply_text(
                f"👑 **YOUR PREMIUM PLAN**\n\n"
                f"👤 **User:** {user_mention}\n"
                f"🆔 **ID:** `{user_id}`\n"
                f"📅 **Expires:** `{expiry_date}`\n"
                f"⏰ **Time:** `{expiry_time_str}`\n"
                f"⏳ **Remaining:** `{formatted_time}`\n\n"
                f"✅ **Status:** *Active*",
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode='Markdown'
            )
        else:
            await db.remove_premium_user(user_id)
            await check_plans_cmd(client, message)  # Recheck
    else:
        buttons = [ 
            [InlineKeyboardButton("🎁 Free Trial (5min)", callback_data="give_trial")],
            [InlineKeyboardButton("💎 View Plans", callback_data="seeplans")],
            [InlineKeyboardButton("📞 Contact Owner", url="https://t.me/betabot_hub")]
        ]
        await message.reply_text(
            f"😔 **No Active Premium Plan**\n\n"
            f"👤 **{user_mention}**\n\n"
            f"**Get Premium to:**\n"
            f"✅ Skip verification\n"
            f"✅ Direct files\n"
            f"✅ No ads\n"
            f"✅ High priority",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

@Client.on_message(filters.command("remove_premium"))
async def remove_premium(client, message):
    if message.from_user.id not in ADMINS:
        return await message.reply_text("❌ **No permission!**")
    
    if len(message.command) == 2:
        try:
            target_id = int(message.command[1])
            user = await client.get_users(target_id)
            
            if await db.remove_premium_user(target_id):
                await message.reply_text(
                    f"✅ **Premium Removed!**\n\n"
                    f"👤 **User:** {user.mention}\n"
                    f"🆔 **ID:** `{target_id}`"
                )
                
                try:
                    await client.send_message(
                        target_id, 
                        f"📢 **Premium Removed**\n\n"
                        f"👤 **{user.mention}**\n\n"
                        f"Your premium access has been removed."
                    )
                except:
                    pass
            else:
                await message.reply_text("❌ **User not found or no premium!**")
        except ValueError:
            await message.reply_text("❌ **Invalid user ID!**")
        except Exception:
            await message.reply_text("❌ **Something went wrong!**")
    else:
        await message.reply_text("**Usage:** `/remove_premium user_id`")

@Client.on_message(filters.command("premium_users"))
async def premium_users_info(client, message):
    if message.from_user.id not in ADMINS:
        return await message.reply("❌ **No permission!**")

    count = await db.count_premium_users()
    await message.reply(f"👥 **Total Premium Users:** `{count}`")

    users = await db.get_all_premium_users()
    if not users:
        return await message.reply("📝 **No active premium users!**")
    
    report = "📋 **ACTIVE PREMIUM USERS:**\n\n"
    user_count = 1
    
    for user_data in users[:50]:  # Limit to 50 users
        user_id = user_data.get('id')
        expiry = user_data.get("expiry_time")
        
        if not expiry:
            continue
            
        # Check if expired
        if isinstance(expiry, str):
            expiry = dt.datetime.fromisoformat(expiry.replace('Z', '+00:00'))
        elif expiry.tzinfo is None:
            expiry = pytz.utc.localize(expiry)
        
        current_time = dt.datetime.now(pytz.utc)
        if current_time > expiry:
            await db.remove_premium_user(user_id)
            continue
        
        # Convert to IST
        ist_expiry = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
        time_left = ist_expiry - dt.datetime.now(pytz.timezone("Asia/Kolkata"))
        
        try:
            user = await client.get_users(user_id)
            username = f"[{user.first_name}](tg://user?id={user_id})"
        except:
            username = f"`{user_id}`"
            
        report += f"{user_count}. {username} - `{ist_expiry.strftime('%d-%m-%Y')}`\n"
        report += f"   ⏳ `{time_left.days}d left`\n\n"
        user_count += 1
    
    if len(report) > 4096:
        with open('premium_users.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        await message.reply_document('premium_users.txt', caption=f"📊 **{count} Premium Users**")
    else:
        await message.reply(report, disable_web_page_preview=True, parse_mode='Markdown')

@Client.on_message(filters.command("plan"))
async def plan(client, message):
    buttons = [
        [InlineKeyboardButton("💎 1 Day Plan (₹2)", callback_data="plan_1d")],
        [InlineKeyboardButton("💎 1 Month (₹39)", callback_data="plan_30d")],
        [InlineKeyboardButton("💎 2 Months (₹59)", callback_data="plan_60d")],
        [InlineKeyboardButton("📞 Contact Owner", url="https://t.me/betabot_hub")],
        [InlineKeyboardButton("❓ Check My Plan", callback_data="myplan_cb")]
    ]
    
    await message.reply_photo(
        photo="https://files.catbox.moe/ce96vj.jpg",
        caption="🔥 **PREMIUM PLANS** 🔥\n\n"
                "**💎 1 Day** - ₹2\n"
                "**💎 1 Month** - ₹39\n"
                "**💎 2 Months** - ₹59\n\n"
                "**Benefits:**\n"
                "✅ Direct files\n"
                "✅ No verification\n"
                "✅ No ads\n"
                "✅ Priority support\n\n"
                "**Payment:** Send UPI to `shivashish-kumar@ptyes`\n"
                "**Send screenshot to owner after payment**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Callback handlers
@Client.on_callback_query(filters.regex(r"^(plan_(1d|30d|60d)|myplan_cb|refresh_plan|give_trial|seeplans)$"))
async def plan_callbacks(client: Client, callback: CallbackQuery):
    data = callback.data
    
    if data == "myplan_cb" or data == "refresh_plan":
        # Trigger myplan command
        await check_plans_cmd(client, callback.message)
        return
    
    if data == "give_trial":
        user_id = callback.from_user.id
        await db.add_trial_premium(user_id, 300)  # 5 minutes trial
        await callback.answer("🎁 5min trial activated!", show_alert=True)
        return
    
    if data == "seeplans":
        await plan(client, callback.message)
        return
    
    # Plan selection
    plans = {
        "plan_1d": {"days": 1, "price": "₹2"},
        "plan_30d": {"days": 30, "price": "₹39"},
        "plan_60d": {"days": 60, "price": "₹59"}
    }
    
    plan_data = data.split("_")[1]
    plan_info = plans.get(f"plan_{plan_data}")
    
    buttons = [
        [InlineKeyboardButton("💰 Pay Now", callback_data=f"pay_{plan_data}")],
        [InlineKeyboardButton("🔙 Back to Plans", callback_data="seeplans")]
    ]
    
    await callback.edit_message_text(
        f"💎 **Selected: {plan_data.replace('1d','1 Day').replace('30d','1 Month').replace('60d','2 Months')}**\n\n"
        f"💰 **Price:** {plan_info['price']}\n"
        f"📅 **Duration:** {plan_info['days']} days\n\n"
        f"**Payment:**\n"
        f"`shivashish-kumar@ptyes`\n\n"
        f"**After payment:**\n"
        f"1️⃣ Send screenshot to @MOVIE_BOX_REQUEST_ROBOT \n"
        f"2️⃣ Get activated in 5 mins",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
