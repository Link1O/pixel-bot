import discord
import dotenv
import os
import requests
import aiohttp
import random
import aiomysql
import datetime
import ast
import json
import requests
# arguments
message_threshold = 4
cooldown_duration = 2.5
url_pattern = r"https?://\S+"
# dotenv arguments
dotenv.load_dotenv()
token_main = os.getenv("TOKEN_MAIN")
token_testing = os.getenv("TOKEN_TESTING")
raw_whitelist = os.getenv("whitelist", "")
whitelist = [int(item.strip()) for item in raw_whitelist.split(",") if item]
feedback_channel = os.getenv("feedback_channel")
db = os.getenv("db")
db_host = os.getenv("db_host")
db_port = int(os.getenv("db_port"))
db_user = os.getenv("db_user")
db_password = os.getenv("db_password")
db_charset = os.getenv("db_charset")
tenor_apikey = os.getenv("tenor_apikey")
shards = int(os.getenv("shards"))
prefix = os.getenv("prefix")
bot_status= os.getenv("bot_status")
host_status= os.getenv("host_status")
global_path = os.getenv("global_path")
async def fetch_from_tenor(search_term):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url=f"https://tenor.googleapis.com/v2/search?q={search_term}&key={tenor_apikey}&limit=50"
        ) as response:
            data = await response.json()
            gif_list = data.get("results", [])
            if not gif_list:
                return None
            random_gif_url = gif_list and gif_list[0]["media_formats"]["gif"]["url"]
            return random_gif_url
        
async def fetch_from_boredapi():
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f"https://www.boredapi.com/api/activity") as response:
            await session.close()
            data = await response.json()
            return data["activity"]
async def fetch_waifu():
    async with aiohttp.ClientSession() as session:
        async with session.get(url="https://api.nekosapi.com/v3/images/random", params={
        'limit': 0
    }) as response:
            await session.close()
            data = await response.json()
            image = data['items'][0]["image_url"]
            return image
def parse_duration(duration):
    total_seconds = 0
    try:
        duration = duration.lower()
        if 'd' in duration:
            total_seconds = int(duration.split('d')[0]) * 86400
        if 'h' in duration:
            total_seconds = int(duration.split('h')[0]) * 3600
        if 'm' in duration:
            total_seconds = int(duration.split('m')[0]) * 60
        elif 's' in duration:
            total_seconds = int(duration.split('s')[0])
        return total_seconds
    except ValueError:
        return None
async def calculate_afk_duration(member_id):
    conn = await aiomysql.connect(
        db=db,
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        charset=db_charset,
        cursorclass=aiomysql.DictCursor
    )
    async with conn.cursor() as cursor:
        await cursor.execute('SELECT timestamp FROM afk WHERE member_id = %s', (member_id,))
        result = await cursor.fetchone()
        if result:
            timestamp = result['timestamp']
            stored_time = datetime.datetime.fromisoformat(timestamp)
            current_time = datetime.datetime.utcnow()
            afk_duration = current_time - stored_time
            return afk_duration.total_seconds()
        if not result:
            return None
def truncate_long_name(name, max_length):
    if len(name) > max_length:
        return name[:max_length] + "..."
    return name
def check_message(message):
    response = requests.get(f'http://www.purgomalum.com/service/containsprofanity?text={message}')
    return response.text == 'true'
def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)
# commands classes
class button_view_timeout(discord.ui.View):
    def __init__(self, timeout=60):
        super().__init__(timeout=timeout)
    @discord.ui.button(label="View timedout", style=discord.ButtonStyle.secondary, disabled=True)
    async def timeout_button(self):
        pass
# dictionary loading
chat_filter_settings = {}
try:
    with open(f"{global_path}/settings_data/chat_filter_settings.json", 'r') as f:
        chat_filter_settings = json.load(f)
except FileNotFoundError:
    pass
with open(f"{global_path}/settings_data/chat_filter_settings.json", 'w') as f:
    json.dump(chat_filter_settings, f, indent=4)
def save_chat_filter_settings():
    with open(f"{global_path}/settings_data/chat_filter_settings.json", 'w') as f:
        json.dump(chat_filter_settings, f, indent=4)
anti_spam_settings = {}
try:
    with open(f"{global_path}/settings_data/anti_spam_settings.json", 'r') as f:
        anti_spam_settings = json.load(f)
except FileNotFoundError:
    pass
def save_anti_spam_settings():
    with open(f"{global_path}/settings_data/anti_spam_settings.json", 'w') as f:
        json.dump(anti_spam_settings, f, indent=4)
anti_link_settings = {}
try:
    with open(f"{global_path}/settings_data/anti_link_settings.json", "r") as f:
        anti_link_settings = json.load(f)
except FileNotFoundError:
    pass
def save_anti_link_settings():
    with open(f"{global_path}/settings_data/anti_link_settings.json", "w") as f:
        json.dump(anti_link_settings, f, indent=4)
audit_log_settings = {}
try:
    with open(f"{global_path}/settings_data/audit_log_settings.json", "r") as f:
        audit_log_settings = json.load(f)
except FileNotFoundError:
    pass
def save_audit_log_settings():
    with open(f"{global_path}/settings_data/audit_log_settings.json", "w") as f:
        json.dump(audit_log_settings, f, indent=4)
mod_log_settings = {}
try:
    with open(f"{global_path}/settings_data/mod_log_settings.json", "r") as f:
        mod_log_settings = json.load(f)
except FileNotFoundError:
    pass
def save_mod_log_settings():
    with open(f"{global_path}/settings_data/mod_log_settings.json", "w") as f:
        json.dump(mod_log_settings, f, indent=4)
welcomer_settings = {}
try:
    with open(f"{global_path}/settings_data/welcomer_settings.json", "r") as f:
        welcomer_settings = json.load(f)
except FileNotFoundError:
    pass
def save_welcomer_settings():
    with open(f"{global_path}/settings_data/welcomer_settings.json", "w") as f:
        json.dump(welcomer_settings, f, indent=4)
farweller_settings = {}
try:
    with open(f"{global_path}/settings_data/farweller_settings.json", "r") as f:
        farweller_settings = json.load(f)
except FileNotFoundError:
    pass
def save_farweller_settings():
    with open(f"{global_path}/settings_data/farweller_settings.json", "w") as f:
        json.dump(farweller_settings, f, indent=4)
suggestion_settings = {}
try:
    with open(f"{global_path}/settings_data/suggestion_settings.json", "r") as f:
        suggestion_settings = json.load(f)
except FileNotFoundError:
    pass
def save_suggestion_settings():
    with open(f"{global_path}/settings_data/suggestion_settings.json", "w") as f:
        json.dump(suggestion_settings, f, indent=4)
suggestion_settings = {}
try:
    with open(f"{global_path}/settings_data/suggestion_settings.json", "r") as f:
        suggestion_settings = json.load(f)
except FileNotFoundError:
    pass
def save_suggestion_settings():
    with open(f"{global_path}/settings_data/suggestion_settings.json", "w") as f:
        json.dump(suggestion_settings, f, indent=4)