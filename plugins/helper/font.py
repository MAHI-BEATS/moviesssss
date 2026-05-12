import os
from plugins.helper.fotnt_string import Fonts  # Fix typo: fotnt_string → font_string
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from database.users_chats_db import db  # 🔥 PREMIUM CHECK
import script
from info import ADMINS

@Client.on_message(filters.private & filters.command(["font"]))
async def font_handler(client: Client, message: Message):
    """Font generator with premium features"""
    user_id = message.from_user.id
    is_premium = await db.is_premium_user(user_id)
    
    # Premium users get special fonts + no limits
    if is_premium:
        await message.reply_text(
            "💎 **Premium User - Unlimited Fonts!**\n"
            "Send: `/font your text`",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✨ Premium Fonts", callback_data="premium_fonts")]
            ])
        )
        return
    
    # Show font menu
    buttons = await get_font_buttons()
    if len(message.text.split()) > 1:
        text = " ".join(message.text.split()[1:])
        await message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            reply_to_message_id=message.id
        )
    else:
        await message.reply_text(
            script.FONT_TXT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

async def get_font_buttons():
    """Font style buttons"""
    return [
        [
            InlineKeyboardButton('𝚃𝚢𝚙𝚎𝚠𝚛𝚒𝚝𝚎𝚛', callback_data='style+typewriter'),
            InlineKeyboardButton('𝕆𝕦𝕥𝕝𝕚𝕟𝕖', callback_data='style+outline'),
            InlineKeyboardButton('𝐒𝐞𝐫𝐢𝐟', callback_data='style+serif'),
        ], [
            InlineKeyboardButton('𝑺𝒆𝒓𝒊𝒇', callback_data='style+bold_cool'),
            InlineKeyboardButton('𝑆𝑒𝑟𝑖𝑓', callback_data='style+cool'),
            InlineKeyboardButton('Sᴍᴀʟʟ Cᴀᴘs', callback_data='style+small_cap'),
        ], [
            InlineKeyboardButton('𝓈𝒸𝓇𝒾𝓅𝓉', callback_data='style+script'),
            InlineKeyboardButton('𝓼𝓬𝓻𝓲𝓹𝓽', callback_data='style+script_bolt'),
            InlineKeyboardButton('ᵗⁱⁿʸ', callback_data='style+tiny'),
        ], [
            InlineKeyboardButton('ᑕOᗰIᑕ', callback_data='style+comic'),
            InlineKeyboardButton('𝗦𝗮𝗻𝘀', callback_data='style+sans'),
            InlineKeyboardButton('𝙎𝙖𝙣𝙨', callback_data='style+slant_sans'),
        ], [
            InlineKeyboardButton("➡️ More", callback_data="nxt"),
            InlineKeyboardButton("💎 Premium", callback_data="plan")
        ]
    ]

@Client.on_callback_query(filters.regex('^(nxt|premium_fonts)$'))
async def font_next(client: Client, callback: CallbackQuery):
    """Next page fonts or premium fonts"""
    if callback.data == "premium_fonts":
        # Premium exclusive fonts
        buttons = [
            [InlineKeyboardButton('✨ G̶l̶i̶t̶c̶h̶', callback_data='style+glitch')],
            [InlineKeyboardButton('🌈 R̷a̷i̷n̷b̷o̷w̷', callback_data='style+rainbow')],
            [InlineKeyboardButton('🔥 F̸i̸r̸e̸', callback_data='style+fire')],
            [InlineKeyboardButton("💎 /myplan", callback_data="myplan")],
            [InlineKeyboardButton("🔙 Back", callback_data="font_back")]
        ]
        await callback.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
        return
    
    if callback.data == "nxt":
        buttons = [
            [InlineKeyboardButton('🇸 🇵 🇪 🇨 🇮 🇦 🇱 ', callback_data='style+special')],
            [InlineKeyboardButton('🅂🅀🅄🄰🅁🄴🅂', callback_data='style+squares')],
            [InlineKeyboardButton('🆂︎🆀︎🆄︎🅰︎🆁︎🅴︎🆂︎', callback_data='style+squares_bold')],
            [InlineKeyboardButton('ꪖꪀᦔꪖꪶꪊᥴ𝓲ꪖ', callback_data='style+andalucia')],
            [InlineKeyboardButton("🔙 Back", callback_data="font_back")]
        ]
        await callback.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex('^font_back'))
async def font_back(client: Client, callback: CallbackQuery):
    """Back to main fonts"""
    buttons = await get_font_buttons()
    await callback.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex('^(style|plan|myplan)'))
async def font_style(client: Client, callback: CallbackQuery):
    """Generate font style"""
    if callback.data == "plan":
        # Premium upsell
        buttons = [
            [InlineKeyboardButton("💎 1 Day - ₹2", callback_data="plan_1")],
            [InlineKeyboardButton("💎 30 Days - ₹39", callback_data="plan_30")],
            [InlineKeyboardButton("📞 Contact", url="https://t.me/betabot_hub")]
        ]
        await callback.edit_message_text(
            script.PLAN_TEXT,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return
    
    if callback.data == "myplan":
        user_id = callback.from_user.id
        premium_info = await db.get_premium_user(user_id)
        if premium_info and premium_info.get("is_active"):
            await callback.answer("💎 Premium Active!", show_alert=True)
        else:
            await callback.answer("🔒 No Active Plan", show_alert=True)
        return
    
    # Font generation
    await callback.answer()
    cmd, style = callback.data.split('+')
    
    # Font styles dictionary
    fonts = {
        'typewriter': Fonts.typewriter,
        'outline': Fonts.outline,
        'serif': Fonts.serief,
        'bold_cool': Fonts.bold_cool,
        'cool': Fonts.cool,
        'small_cap': Fonts.smallcap,
        'script': Fonts.script,
        'script_bolt': Fonts.bold_script,
        'tiny': Fonts.tiny,
        'comic': Fonts.comic,
        'sans': Fonts.san,
        'slant_sans': Fonts.slant_san,
        'slant': Fonts.slant,
        'sim': Fonts.sim,
        'circles': Fonts.circles,
        'circle_dark': Fonts.dark_circle,
        'gothic': Fonts.gothic,
        'gothic_bolt': Fonts.bold_gothic,
        'cloud': Fonts.cloud,
        'happy': Fonts.happy,
        'sad': Fonts.sad,
        'special': Fonts.special,
        'squares': Fonts.square,
        'squares_bold': Fonts.dark_square,
        'andalucia': Fonts.andalucia,
        'manga': Fonts.manga,
        'stinky': Fonts.stinky,
        'bubbles': Fonts.bubbles,
        'underline': Fonts.underline,
        'ladybug': Fonts.ladybug,
        'rays': Fonts.rays,
        'birds': Fonts.birds,
        'slash': Fonts.slash,
        'stop': Fonts.stop,
        'skyline': Fonts.skyline,
        'arrows': Fonts.arrows,
        'qvnes': Fonts.rvnes,
        'strike': Fonts.strike,
        'frozen': Fonts.frozen,
        # Premium fonts
        'glitch': lambda x: ''.join([chr(ord(c) + random.randint(-1,1)) if c.isalpha() else c for c in x]),
        'rainbow': lambda x: ''.join(['🔴' if i%5==0 else '🟠' if i%5==1 else '🟡' if i%5==2 else '🟢' if i%5==3 else '🔵' for i,c in enumerate(x)] + [x]),
        'fire': lambda x: '🔥 ' + x + ' 🔥'
    }
    
    # Get original text
    try:
        original_msg = callback.message.reply_to_message or callback.message
        text = original_msg.text.split(maxsplit=1)[1] if len(original_msg.text.split()) > 1 else "Sample Text"
    except:
        text = "Sample Text"
    
    # Generate font
    if style in fonts:
        new_text = fonts[style](text)
    else:
        new_text = text
    
    # Premium badge
    is_premium = await db.is_premium_user(callback.from_user.id)
    badge = " 💎" if is_premium else ""
    
    # Send result
    await callback.edit_message_text(
        f"`{new_text}`{badge}\n\n"
        f"👆 **Click to Copy**\n"
        f"💎 **Premium = Exclusive fonts!**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 New Style", callback_data="font_back")],
            [InlineKeyboardButton("💎 Premium", callback_data="plan")]
        ])
    )

print("✅ Font plugin loaded with Premium!")
