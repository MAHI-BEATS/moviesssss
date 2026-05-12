import datetime
import pytz
from motor.motor_asyncio import AsyncIOMotorClient
from info import SETTINGS, IS_PM_SEARCH, PREMIUM_POINT, REF_PREMIUM, IS_VERIFY, SHORTENER_WEBSITE3, SHORTENER_API3, THREE_VERIFY_GAP, LINK_MODE, FILE_CAPTION, TUTORIAL, DATABASE_NAME, DATABASE_URI, IMDB, IMDB_TEMPLATE, PROTECT_CONTENT, AUTO_DELETE, SPELL_CHECK, AUTO_FILTER, LOG_VR_CHANNEL, SHORTENER_WEBSITE, SHORTENER_API, SHORTENER_WEBSITE2, SHORTENER_API2, TWO_VERIFY_GAP

client = AsyncIOMotorClient(DATABASE_URI)
mydb = client[DATABASE_NAME]
fsubs = client['fsubs']

class Database:
    default = SETTINGS.copy()
    
    def __init__(self):
        self.col = mydb.users
        self.grp = mydb.groups
        self.misc = mydb.misc
        self.verify_id = mydb.verify_id
        self.users = mydb.users  # Fixed typo: was 'uersz'
        self.req = mydb.requests
        self.mGrp = mydb.mGrp
        self.pmMode = mydb.pmMode
        self.jisshu_ads_link = mydb.jisshu_ads_link
        self.grp_and_ids = fsubs.grp_and_ids
        self.movies_update_channel = mydb.movies_update_channel
        self.botcol = mydb.botcol
        self.premium_users = mydb.premium_users  # New collection for premium tracking
        
    def new_user(self, id, name):
        return dict(
            id=id,
            name=name,
            point=0,
            ban_status=dict(is_banned=False, ban_reason=""),
            is_premium=False,
            premium_expire=0,
            premium_added_date=0
        )

    async def get_settings(self, id):
        chat = await self.grp.find_one({'id': int(id)})
        if chat:
            return chat.get('settings', self.default)
        else:
            await self.grp.update_one({'id': int(id)}, {'$set': {'settings': self.default}}, upsert=True)
        return self.default

    async def find_join_req(self, id):
        return bool(await self.req.find_one({'id': id}))
        
    async def add_join_req(self, id):
        await self.req.insert_one({'id': id})

    async def del_join_req(self):
        await self.req.drop()

    def new_group(self, id, title):
        return dict(
            id=id,
            title=title,
            chat_status=dict(is_disabled=False, reason="")
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
        
    async def update_point(self, id):
        await self.col.update_one({'id': id}, {'$inc': {'point': 100}})
        point = (await self.col.find_one({'id': id}))['point']
        if point >= PREMIUM_POINT:
            seconds = (REF_PREMIUM * 24 * 60 * 60)
            oldEx = await self.users.find_one({'id': id})
            if oldEx:
                expiry_time = oldEx['premium_expire'] + datetime.timedelta(seconds=seconds)
            else:
                expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
            user_data = {"id": id, "premium_expire": expiry_time, "is_premium": True}
            await self.update_premium_user(user_data)
            await self.col.update_one({'id': id}, {'$set': {'point': 0}})
            
    async def get_point(self, id):
        newPoint = await self.col.find_one({'id': id})
        return newPoint['point'] if newPoint else None
        
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count
    
    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def delete_chat(self, id):
        await self.grp.delete_many({'id': int(id)})
        
    async def get_banned(self):
        users = self.col.find({'ban_status.is_banned': True})
        chats = self.grp.find({'chat_status.is_disabled': True})
        b_chats = [chat['id'] async for chat in chats]
        b_users = [user['id'] async for user in users]
        return b_users, b_chats
    
    async def add_chat(self, chat, title):
        chat = self.new_group(chat, title)
        await self.grp.insert_one(chat)

    async def get_chat(self, chat):
        chat = await self.grp.find_one({'id': int(chat)})
        return False if not chat else chat.get('chat_status')  

    async def update_settings(self, id, settings):
        await self.grp.update_one({'id': int(id)}, {'$set': {'settings': settings}})   
    
    async def total_chat_count(self):
        count = await self.grp.count_documents({})
        return count
    
    async def get_all_chats(self):
        return self.grp.find({})

    async def get_db_size(self):
        return (await mydb.command("dbstats"))['dataSize'] 

    # ========== VERIFICATION FUNCTIONS ==========
    async def get_notcopy_user(self, user_id):
        user_id = int(user_id)
        user = await self.misc.find_one({"user_id": user_id})
        ist_timezone = pytz.timezone('Asia/Kolkata')
        if not user:
            res = {
                "user_id": user_id,
                "last_verified": datetime.datetime(2020, 5, 17, 0, 0, 0, tzinfo=ist_timezone),
                "second_time_verified": datetime.datetime(2019, 5, 17, 0, 0, 0, tzinfo=ist_timezone),
                "third_time_verified": datetime.datetime(2018, 5, 17, 0, 0, 0, tzinfo=ist_timezone)
            }
            await self.misc.insert_one(res)
            user = await self.misc.find_one({"user_id": user_id})
        return user

    async def update_notcopy_user(self, user_id, value: dict):
        user_id = int(user_id)
        myquery = {"user_id": user_id}
        newvalues = {"$set": value}
        return await self.misc.update_one(myquery, newvalues)

    async def is_user_verified(self, user_id):
        user = await self.get_notcopy_user(user_id)
        try:
            pastDate = user["last_verified"]
        except Exception:
            user = await self.get_notcopy_user(user_id)
            pastDate = user["last_verified"]
        ist_timezone = pytz.timezone('Asia/Kolkata')
        pastDate = pastDate.astimezone(ist_timezone)
        current_time = datetime.datetime.now(tz=ist_timezone)
        seconds_since_midnight = (current_time - datetime.datetime(current_time.year, current_time.month, current_time.day, 0, 0, 0, tzinfo=ist_timezone)).total_seconds()
        time_diff = current_time - pastDate
        total_seconds = time_diff.total_seconds()
        return total_seconds <= seconds_since_midnight

    async def user_verified(self, user_id):
        user = await self.get_notcopy_user(user_id)
        try:
            pastDate = user["second_time_verified"]
        except Exception:
            user = await self.get_notcopy_user(user_id)
            pastDate = user["second_time_verified"]
        ist_timezone = pytz.timezone('Asia/Kolkata')
        pastDate = pastDate.astimezone(ist_timezone)
        current_time = datetime.datetime.now(tz=ist_timezone)
        seconds_since_midnight = (current_time - datetime.datetime(current_time.year, current_time.month, current_time.day, 0, 0, 0, tzinfo=ist_timezone)).total_seconds()
        time_diff = current_time - pastDate
        total_seconds = time_diff.total_seconds()
        return total_seconds <= seconds_since_midnight

    async def use_second_shortener(self, user_id, time):
        user = await self.get_notcopy_user(user_id)
        if not user.get("second_time_verified"):
            ist_timezone = pytz.timezone('Asia/Kolkata')
            await self.update_notcopy_user(user_id, {"second_time_verified": datetime.datetime(2019, 5, 17, 0, 0, 0, tzinfo=ist_timezone)})
            user = await self.get_notcopy_user(user_id)
        if await self.is_user_verified(user_id):
            try:
                pastDate = user["last_verified"]
            except Exception:
                user = await self.get_notcopy_user(user_id)
                pastDate = user["last_verified"]
            ist_timezone = pytz.timezone('Asia/Kolkata')
            pastDate = pastDate.astimezone(ist_timezone)
            current_time = datetime.datetime.now(tz=ist_timezone)
            time_difference = current_time - pastDate
            if time_difference > datetime.timedelta(seconds=time):
                pastDate = user["last_verified"].astimezone(ist_timezone)
                second_time = user["second_time_verified"].astimezone(ist_timezone)
                return second_time < pastDate
        return False

    async def use_third_shortener(self, user_id, time):
        user = await self.get_notcopy_user(user_id)
        if not user.get("third_time_verified"):
            ist_timezone = pytz.timezone('Asia/Kolkata')
            await self.update_notcopy_user(user_id, {"third_time_verified": datetime.datetime(2018, 5, 17, 0, 0, 0, tzinfo=ist_timezone)})
            user = await self.get_notcopy_user(user_id)
        if await self.user_verified(user_id):
            try:
                pastDate = user["second_time_verified"]
            except Exception:
                user = await self.get_notcopy_user(user_id)
                pastDate = user["second_time_verified"]
            ist_timezone = pytz.timezone('Asia/Kolkata')
            pastDate = pastDate.astimezone(ist_timezone)
            current_time = datetime.datetime.now(tz=ist_timezone)
            time_difference = current_time - pastDate
            if time_difference > datetime.timedelta(seconds=time):
                pastDate = user["second_time_verified"].astimezone(ist_timezone)
                second_time = user["third_time_verified"].astimezone(ist_timezone)
                return second_time < pastDate
        return False

    # ========== VERIFY ID FUNCTIONS ==========
    async def create_verify_id(self, user_id: int, hash):
        res = {"user_id": user_id, "hash": hash, "verified": False}
        return await self.verify_id.insert_one(res)

    async def get_verify_id_info(self, user_id: int, hash):
        return await self.verify_id.find_one({"user_id": user_id, "hash": hash})

    async def update_verify_id_info(self, user_id, hash, value: dict):
        myquery = {"user_id": user_id, "hash": hash}
        newvalues = {"$set": value}
        return await self.verify_id.update_one(myquery, newvalues)

    # ========== PREMIUM SYSTEM FUNCTIONS ==========
    async def get_user(self, user_id):
        """Get user premium data"""
        return await self.users.find_one({"id": user_id})

    async def add_premium_user(self, user_id: int, expire_seconds: int):
        """Add premium access to user"""
        current_time = datetime.datetime.now()
        expire_time = current_time + datetime.timedelta(seconds=expire_seconds)
        
        user_data = {
            "id": user_id,
            "is_premium": True,
            "premium_expire": expire_time,
            "premium_added_date": current_time
        }
        await self.users.update_one(
            {"id": user_id},
            {"$set": user_data},
            upsert=True
        )
        return True

    async def remove_premium_user(self, user_id: int):
        """Remove premium access"""
        await self.users.update_one(
            {"id": user_id},
            {"$set": {
                "is_premium": False,
                "premium_expire": datetime.datetime(1970, 1, 1),
                "premium_added_date": 0
            }}
        )
        return True

    async def is_premium_user(self, user_id: int) -> bool:
        """Check if user has active premium"""
        user_data = await self.get_user(user_id)
        if not user_data or not user_data.get("is_premium", False):
            return False
        
        expire_time = user_data.get("premium_expire")
        if isinstance(expire_time, datetime.datetime):
            if datetime.datetime.now() > expire_time:
                # Premium expired, remove it
                await self.remove_premium_user(user_id)
                return False
            return True
        return False

    async def get_premium_user(self, user_id: int):
        """Get premium user details with formatted expire date"""
        user_data = await self.get_user(user_id)
        if user_data and user_data.get("is_premium", False):
            expire_time = user_data.get("premium_expire")
            if isinstance(expire_time, datetime.datetime):
                return {
                    "expire_date": expire_time.strftime("%d/%m/%Y %H:%M:%S"),
                    "is_active": datetime.datetime.now() <= expire_time
                }
        return None

    async def get_all_premium_users_count(self):
        """Get count of active premium users"""
        current_time = datetime.datetime.now()
        count = await self.users.count_documents({
            "is_premium": True,
            "premium_expire": {"$gt": current_time}
        })
        return count

    async def get_premium_users_list(self):
        """Get list of all active premium users"""
        current_time = datetime.datetime.now()
        return self.users.find({
            "is_premium": True,
            "premium_expire": {"$gt": current_time}
        })

    # ========== BAN FUNCTIONS ==========
    async def ban_user(self, user_id, ban_reason="No Reason"):
        ban_status = dict(is_banned=True, ban_reason=ban_reason)
        await self.col.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

    async def remove_ban(self, id):
        ban_status = dict(is_banned=False, ban_reason='')
        await self.col.update_one({'id': id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        default = dict(is_banned=False, ban_reason='')
        user = await self.col.find_one({'id': int(id)})
        if not user:
            return default
        return user.get('ban_status', default)

    # ========== OTHER FUNCTIONS ==========
    async def update_user(self, user_data):
        await self.users.update_one({"id": user_data["id"]}, {"$set": user_data}, upsert=True)

    async def jisshu_set_ads_link(self, link):
        await self.jisshu_ads_link.update_one({}, {'$set': {'link': link}}, upsert=True)
    
    async def jisshu_get_ads_link(self):
        link = await self.jisshu_ads_link.find_one({})
        return link.get("link") if link else None
            
    async def jisshu_del_ads_link(self):
        result = await self.jisshu_ads_link.delete_one({})
        return result.deleted_count > 0

    async def setFsub(self, grpID, fsubID):
        return await self.grp_and_ids.update_one(
            {'grpID': grpID}, 
            {'$set': {'grpID': grpID, "fsubID": fsubID}}, 
            upsert=True
        )    
    
    async def getFsub(self, grpID):
        link = await self.grp_and_ids.find_one({"grpID": grpID})
        return link.get("fsubID") if link else None
            
    async def delFsub(self, grpID):
        result = await self.grp_and_ids.delete_one({"grpID": grpID})
        return result.deleted_count != 0

    async def get_pm_search_status(self, bot_id):
        bot = await self.botcol.find_one({'id': bot_id})
        return bot['bot_pm_search'] if bot and bot.get('bot_pm_search') else IS_PM_SEARCH

    async def update_pm_search_status(self, bot_id, enable):
        bot = await self.botcol.find_one({'id': int(bot_id)})
        if bot:
            await self.botcol.update_one({'id': int(bot_id)}, {'$set': {'bot_pm_search': enable}})
        else:
            await self.botcol.insert_one({'id': int(bot_id), 'bot_pm_search': enable})
            
    async def movies_update_channel_id(self, id=None):
        if id is None:
            myLinks = await self.movies_update_channel.find_one({})
            return myLinks.get("id") if myLinks else None
        return await self.movies_update_channel.update_one({}, {'$set': {'id': id}}, upsert=True)

db = Database()
