import re
from os import environ, getenv
from Script import script

id_pattern = re.compile(r'^\.\d+$')

def is_enabled(value, default):
    if isinstance(value, bool):
        return value
    if not value:
        return default
    
    value = str(value).lower().strip()
    if value in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# --- Core Credentials ---
SESSION = environ.get('SESSION', 'Media_search')
API_ID = int(environ.get('API_ID', '31681117'))
API_HASH = environ.get('API_HASH', '56adbd4c29efd9d02d37d779b7732b60')
BOT_TOKEN = environ.get('BOT_TOKEN', '7807I9ygow9sLqNQuI7hsWPm5FLNfBr9c')

# --- Admin & Channels ---
ADMINS = [int(admin) if id_pattern.search(admin.strip()) else admin.strip() for admin in environ.get('ADMINS', '8418584090').split()]
USERNAME = environ.get('USERNAME', "https://t.me/betabot_hub")
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1003812209413'))
MOVIE_GROUP_LINK = environ.get('MOVIE_GROUP_LINK', 'https://t.me/+sLEVq3pYIiBiNGI9')
CHANNELS = [int(ch) if id_pattern.search(ch.strip()) else ch.strip() for ch in environ.get('CHANNELS', '-1003812209413').split()]

# --- 🔥 PREMIUM SYSTEM CONFIG 🔥 ---
PREMIUM_POINT = int(environ.get('PREMIUM_POINT', '1500'))  # Points needed for premium
REF_PREMIUM = int(environ.get('REF_PREMIUM', '30'))        # Days for referral premium
PREMIUM_UPI = environ.get('PREMIUM_UPI', 'yourupi@paytm')  # Your UPI ID
PREMIUM_SUPPORT = environ.get('PREMIUM_SUPPORT', 'https://t.me/betabot_hub')

# --- Database ---
DATABASE_URI = environ.get('DATABASE_URI', "mongodb+srv://shivbots:shivashish@cluster0.kdzu3eg.mongodb.net/?appName=Cluster0")
DATABASE_NAME = environ.get('DATABASE_NAME', "learningbots")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'Telegram_files')

# --- Logging & Support ---
LOG_API_CHANNEL = int(environ.get('LOG_API_CHANNEL', '0'))  
BIN_CHANNEL = int(environ.get('BIN_CHANNEL','0'))
DELETE_CHANNELS = int(environ.get('DELETE_CHANNELS','0'))
LOG_VR_CHANNEL = int(environ.get('LOG_VR_CHANNEL', '0'))
auth_channel = environ.get('AUTH_CHANNEL', '')
SUPPORT_GROUP = int(environ.get('SUPPORT_GROUP', '0'))
request_channel = environ.get('REQUEST_CHANNEL', '0')
MOVIE_UPDATE_CHANNEL = int(environ.get('MOVIE_UPDATE_CHANNEL', '0'))
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'https://t.me/')

# --- Verification ---
IS_VERIFY = is_enabled(environ.get('IS_VERIFY'), True)
TUTORIAL = environ.get("TUTORIAL", "https://t.me/")
VERIFY_IMG = environ.get("VERIFY_IMG", "https://graph.org/file/1669ab9af68eaa62c3ca4.jpg")

# --- Shorteners (3 Levels) ---
SHORTENER_API = environ.get("SHORTENER_API", "3097623f852197a9ce40d1212aaa8bbf2803e799")
SHORTENER_WEBSITE = environ.get("SHORTENER_WEBSITE", 'omegalinks.in')
SHORTENER_API2 = environ.get("SHORTENER_API2", "3097623f852197a9ce40d1212aaa8bbf2803e799")
SHORTENER_WEBSITE2 = environ.get("SHORTENER_WEBSITE2", 'omegalinks.in')
SHORTENER_API3 = environ.get("SHORTENER_API3", "3097623f852197a9ce40d1212aaa8bbf2803e799")
SHORTENER_WEBSITE3 = environ.get("SHORTENER_WEBSITE3", 'omegalinks.in')

TWO_VERIFY_GAP = int(environ.get('TWO_VERIFY_GAP', "14400"))
THREE_VERIFY_GAP = int(environ.get('THREE_VERIFY_GAP', "14400"))

# --- Search Settings ---
LANGUAGES = ["hindi", "english", "telugu", "tamil", "kannada", "malayalam", "bengali", "marathi", "gujarati", "punjabi"]
QUALITIES = ["HdRip","web-dl" ,"bluray", "hdr", "fhd" , "240p", "360p", "480p", "540p", "720p", "960p", "1080p", "1440p", "2K", "2160p", "4k", "5K", "8K"]
YEARS = [f'{i}' for i in range(202, 2002, -1)]
SEASONS = [f'season {i}' for i in range(1, 23)]

# --- Process Channels ---
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
REQUEST_CHANNEL = int(request_channel) if request_channel and id_pattern.search(request_channel) else None

# --- Images ---
START_IMG = (environ.get('START_IMG', 'https://files.catbox.moe/zgy7zs.jpg')).split()
FORCESUB_IMG = environ.get('FORCESUB_IMG', 'https://i.ibb.co/ZNC1Hnb/ad3f2c88a8f2.jpg')
REFER_PICS = (environ.get("REFER_PICS", "https://envs.sh/PSI.jpg")).split() 
PAYPICS = (environ.get('PAYPICS', 'https://files.catbox.moe/q3mbng.png')).split()
SUBSCRIPTION = environ.get('SUBSCRIPTION', 'https://files.catbox.moe/g5hjr7.png')
REACTIONS = ["👀", "😱", "🔥", "😍", "🎉", "🥰", "😇", "⚡"]

# --- Auto Features ---
FILE_AUTO_DEL_TIMER = int(environ.get('FILE_AUTO_DEL_TIMER', '600'))
AUTO_FILTER = is_enabled(environ.get('AUTO_FILTER'), True)
IS_PM_SEARCH = is_enabled(environ.get('IS_PM_SEARCH'), False)
PORT = environ.get('PORT', '5000')
MAX_BTN = int(environ.get('MAX_BTN', '8'))
AUTO_DELETE = is_enabled(environ.get('AUTO_DELETE'), True)
DELETE_TIME = int(environ.get('DELETE_TIME', 1200))
IMDB = is_enabled(environ.get('IMDB'), False)
FILE_CAPTION = environ.get('FILE_CAPTION', f'{script.FILE_CAPTION}')
IMDB_TEMPLATE = environ.get('IMDB_TEMPLATE', f'{script.IMDB_TEMPLATE_TXT}')
LONG_IMDB_DESCRIPTION = is_enabled(environ.get('LONG_IMDB_DESCRIPTION'), False)
PROTECT_CONTENT = is_enabled(environ.get('PROTECT_CONTENT'), False)
SPELL_CHECK = is_enabled(environ.get('SPELL_CHECK'), True)
LINK_MODE = is_enabled(environ.get('LINK_MODE'), True)

# --- Streaming ---
STREAM_MODE = is_enabled(environ.get('STREAM_MODE'), True)
MULTI_CLIENT = False
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))
ON_HEROKU = 'DYNO' in environ
URL = environ.get("FQDN", "")

# --- Premium Plans Pricing ---
PREMIUM_PLANS = {
    1: 2,    # 1 day = ₹2
    7: 10,   # 7 days = ₹10
    30: 39,  # 30 days = ₹39
    60: 59,  # 60 days = ₹59
    90: 79   # 90 days = ₹79
}

# --- Final Settings ---
SETTINGS = {
    'spell_check': SPELL_CHECK,
    'auto_filter': AUTO_FILTER,
    'file_secure': PROTECT_CONTENT,
    'auto_delete': AUTO_DELETE,
    'template': IMDB_TEMPLATE,
    'caption': FILE_CAPTION,
    'tutorial': TUTORIAL,
    'shortner': SHORTENER_WEBSITE,
    'api': SHORTENER_API,
    'shortner_two': SHORTENER_WEBSITE2,
    'api_two': SHORTENER_API2,
    'log': LOG_VR_CHANNEL,
    'imdb': IMDB,
    'link': LINK_MODE,
    'is_verify': IS_VERIFY,
    'verify_time': TWO_VERIFY_GAP,
    'shortner_three': SHORTENER_WEBSITE3,
    'api_three': SHORTENER_API3,
    'third_verify_time': THREE_VERIFY_GAP,
    'premium_upi': PREMIUM_UPI,
    'premium_support': PREMIUM_SUPPORT
}

print("✅ Config loaded with Premium System!")
