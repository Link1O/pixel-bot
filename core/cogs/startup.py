import os
import discord
from discord.ext import commands, tasks
from PIL import Image, ImageDraw, ImageFont
import io
from colorama import Fore
import time
import datetime
startup_time = datetime.datetime.now()
import aiomysql
import humanize
import re
from utillity import giveaway_check
from utils.tools import *
intents = discord.Intents.all()
message_count = {}
deleted_messages = {} 
warn_time_chat_filter = {}
warn_time_anti_spam = {}
warn_time_anti_link = {}
current_dir = os.path.dirname(os.path.abspath(f'{global_path}/core/arial.ttf'))
font_path = os.path.join(current_dir, 'arial.ttf')
mentions_allowed = discord.AllowedMentions(everyone=False, roles=True, users=True)
class client(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            shard_count=shards,
            intents=intents,
            command_prefix=prefix,
            help_command=None,
            allowed_mentions=mentions_allowed
            )
    async def setup_hook(self):
        start_time = datetime.datetime.now() 
        for filename in os.listdir(f'{global_path}/core/cogs'):
            if filename.endswith('.py') and not filename.startswith('startup'):
                await self.load_extension(filename[:-3])
                current_time = datetime.datetime.utcnow()
                formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
                print(Fore.LIGHTCYAN_EX + filename, Fore.MAGENTA +  f"has been loaded! [{formatted_time}]", Fore.RESET)
                end_time = datetime.datetime.now()
                time_took = (end_time - start_time).microseconds // 1000 
                if time_took < 100:
                    print(Fore.MAGENTA + "took:", Fore.GREEN + f"{time_took}ms", Fore.RESET)
                if time_took > 100 and time_took < 200:
                    print(Fore.MAGENTA + "took:", Fore.YELLOW + f"{time_took}ms", Fore.RESET)
                if time_took > 200:
                    print(Fore.MAGENTA + "took:", Fore.RED + f"{time_took}ms", Fore.RESET)
    async def on_ready(self):
        server_count = len(self.guilds)
        current_time = datetime.datetime.utcnow()
        formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
        print(Fore.GREEN + f'{self.user} is now running. [{formatted_time}]', Fore.RESET)
        @tasks.loop(minutes=5)
        async def update_server_count():
            nonlocal server_count
            server_count = len(self.guilds)
            await self.change_presence(status=discord.Status.idle, activity=discord.Game(name=f"/help | {server_count} servers"))
        update_server_count.start()
        giveaway_check.start()
    async def on_shard_ready(self, shard_id):
        current_time = datetime.datetime.utcnow()
        formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
        shard: discord.ShardInfo = self.get_shard(shard_id)
        print(Fore.GREEN + f'shard: {shard_id} has been connected. [{formatted_time}] (shard web socket latency: {round(shard.latency * 1000)}ms)', Fore.RESET)
    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        if self.user.mentioned_in(message) and not message.mention_everyone:
            if not message.author.bot:
                embed = discord.Embed(
                    title="hey!",
                    description="❯ feeling lost? start by typing /help!",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.purple()
                )
                await message.reply(embed=embed)
        if not message.author.bot:
            mentioned_users = message.mentions
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
                for user in mentioned_users:
                    await cursor.execute('SELECT message FROM afk WHERE member_id = %s', (user.id,))
                    result = await cursor.fetchone()
                    if result:
                        if not message.author.id == user.id:
                            afk_seconds = await calculate_afk_duration(user.id)
                            embed = discord.Embed(
                                title="Notice",
                                description=f"{user.display_name} is AFK: {result['message']} for: {humanize.naturaldelta(datetime.timedelta(seconds=afk_seconds))}",
                                timestamp=datetime.datetime.utcnow(),
                                color=discord.Color.purple()
                            )
                            await message.reply(embed=embed)
            conn.close()
        user = str(message.author.mention)
        user_id = str(message.author.id)
        channel = str(message.channel.mention)
        guild_id = str(message.guild.id)
        if guild_id in chat_filter_settings and chat_filter_settings[guild_id]:
            if check_message(message.content):
                await message.delete()
                if guild_id not in warn_time_chat_filter:
                    warn_time_chat_filter[guild_id] = {}
                last_warn_time = warn_time_chat_filter[guild_id].get(user_id, 0)
                if time.time() - last_warn_time >= 10:
                    if not message.author.bot:
                        embed = discord.Embed(
                            title="chat filter triggred",
                            description=f"❯ {message.author.mention}, watch your language.",
                            timestamp=datetime.datetime.utcnow(),
                            color=discord.Color.purple()
                        )
                        embed.set_footer(text=" |  auto-moderation", icon_url='https://cdn.discordapp.com/avatars/1155901354032758947/4f1a9c29d4d8df35b4739e2803e3f38f.png?size=1024')
                        try:
                            await message.author.send(embed=embed)
                        except discord.Forbidden:
                            await message.channel.send(embed=embed, delete_after=3)
                        warn_time_chat_filter[guild_id][user_id] = time.time()
                mod_log_channel_id = mod_log_settings.get(guild_id)
                if mod_log_channel_id:
                    mod_log_channel = message.guild.get_channel(mod_log_channel_id)
                    if mod_log_channel:
                        embed_log = discord.Embed(
                            title="auto-moderation",
                            description=f"❯ {user}[`{message.author.id}`] triggered the auto-moderation in {channel}",
                            timestamp=datetime.datetime.utcnow(),
                            color=discord.Color.purple()
                        )
                        await mod_log_channel.send(embed=embed_log)
        if guild_id in anti_spam_settings and anti_spam_settings[guild_id]:
            if guild_id not in message_count:
                message_count[guild_id] = {}
            if user_id not in message_count[guild_id]:
                message_count[guild_id][user_id] = 0
            if message_count[guild_id][user_id] > 0:
                current_time = time.time()
                last_message_time = message_count[guild_id].get(user_id + "_last_message_time", 0)
                if current_time - last_message_time >= cooldown_duration:
                    message_count[guild_id][user_id] = 0
            message_count[guild_id][user_id] += 1
            message_count[guild_id][user_id + "_last_message_time"] = time.time()
            if message_count[guild_id][user_id] > message_threshold:
                await message.delete()
                if guild_id not in warn_time_anti_spam:
                    warn_time_anti_spam[guild_id] = {}
                last_warn_time = warn_time_anti_spam[guild_id].get(user_id, 0)
                if time.time() - last_warn_time >= 15:
                    if not message.author.bot:
                        embed = discord.Embed(
                            title="anti spam triggred",
                            description=f"{message.author.mention}, stop spamming.",
                            timestamp=datetime.datetime.utcnow(),
                            color=discord.Color.purple()
                        )
                        embed.set_footer(text=" |  auto-moderation", icon_url='https://cdn.discordapp.com/avatars/1155901354032758947/4f1a9c29d4d8df35b4739e2803e3f38f.png?size=1024')
                        try:
                            await message.author.send(embed=embed)
                        except discord.Forbidden:
                            await message.channel.send(embed=embed, delete_after=3)
                        warn_time_anti_spam[guild_id][user_id] = time.time()
                mod_log_channel_id = mod_log_settings.get(guild_id)
                if mod_log_channel_id:
                    mod_log_channel = message.guild.get_channel(mod_log_channel_id)
                    if mod_log_channel:
                        embed_log = discord.Embed(
                            title="auto-moderation",
                            description=f"❯ {user}[`{message.author.id}`] triggered the auto-moderation in {channel}",
                            timestamp=datetime.datetime.utcnow(),
                            color=discord.Color.purple()
                        )
                        await mod_log_channel.send(embed=embed_log)
        if guild_id in anti_link_settings and anti_link_settings[guild_id]:
            links = re.findall(url_pattern, message.content)
            if links:
                for link in links:
                    await message.delete()
                    if guild_id not in warn_time_anti_link:
                        warn_time_anti_link[guild_id] = {}
                    last_warn_time = warn_time_anti_link[guild_id].get(user_id, 0)
                    if not message.author.bot:
                        embed = discord.Embed(
                            title="anti link triggred",
                            description=f"❯ {message.author.mention}, links are not allowed here.",
                            timestamp=datetime.datetime.utcnow(),
                            color=discord.Color.purple()
                        )
                        embed.set_footer(text=" |  auto-moderation", icon_url='https://cdn.discordapp.com/avatars/1155901354032758947/4f1a9c29d4d8df35b4739e2803e3f38f.png?size=1024')
                        try:
                            await message.author.send(embed=embed)
                        except discord.Forbidden:
                            await message.channel.send(embed=embed, delete_after=3)
                        warn_time_anti_link[guild_id][user_id] = time.time()
                    mod_log_channel_id = mod_log_settings.get(guild_id)
                    if mod_log_channel_id:
                        mod_log_channel = message.guild.get_channel(mod_log_channel_id)
                        if mod_log_channel:
                            embed_log = discord.Embed(
                                title="auto-moderation",
                                description=f"❯ {user}[`{message.author.id}`] triggered the auto-moderation in {channel}",
                                timestamp=datetime.datetime.utcnow(),
                                color=discord.Color.purple()
                            )
                            await mod_log_channel.send(embed=embed_log)
        if message.content.startswith(prefix):
            await self.process_commands(message)
        return False 
    async def on_message_delete(self, message):
        if message.author == self.user:
            return
        deleted_messages[message.channel.id] = message  
        user = str(message.author.mention)
        deleted_message = str(message.content)
        channel = str(message.channel.mention)
        guild_id = str(message.guild.id)
        audit_log_channel_id = audit_log_settings.get(guild_id)
        if audit_log_channel_id:
            audit_log_channel = message.guild.get_channel(audit_log_channel_id)
            if audit_log_channel:
                embed_log = discord.Embed(
                    title="message deleted",
                    description=f"❯ the message: `{deleted_message}` has been deleted in: {channel}",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.purple()
                )
                await audit_log_channel.send(embed=embed_log)
    async def on_message_edit(self, before, after):
        if before.author == self.user or before.content == after.content:
            return
        user = str(after.author.mention)
        user_id = str(after.author.id)
        original_content = str(before.content)
        edited_message = str(after.content)
        channel = str(after.channel.mention)
        guild_id = str(after.guild.id)
        if guild_id in chat_filter_settings and chat_filter_settings[guild_id]:
            if check_message(edited_message):
                await after.delete()
                embed = discord.Embed(
                    title="chat filter triggred",
                    description=f"❯ {after.author.mention}, watch your language.",
                    color=discord.Color.purple()
                )
                embed.set_footer(text=" |  auto-moderation", icon_url='https://cdn.discordapp.com/avatars/1155901354032758947/4f1a9c29d4d8df35b4739e2803e3f38f.png?size=1024')
                try:
                    await after.author.send(embed=embed)
                except discord.Forbidden:
                    pass
                mod_log_channel_id = mod_log_settings.get(guild_id)
                if mod_log_channel_id:
                    mod_log_channel = after.guild.get_channel(mod_log_channel_id)
                    if mod_log_channel:
                        embed_log = discord.Embed(
                            title="auto-moderation",
                            description=f"❯ {user}[`{after.author.id}`] triggered the auto-moderation in {channel}",
                            timestamp=datetime.datetime.utcnow(),
                            color=discord.Color.purple()
                        )
                        await mod_log_channel.send(embed=embed_log)
        guild_id = str(after.guild.id)
        audit_log_channel_id = audit_log_settings.get(guild_id)
        if audit_log_channel_id:
            audit_log_channel = before.guild.get_channel(audit_log_channel_id)
            if audit_log_channel:
                embed_log = discord.Embed(
                    title="message edited",
                    description=f"❯ the member: {user}[`{user_id}`] has edited the message: `{original_content}` to `{edited_message}` in: {channel}",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.purple()
                )
                await audit_log_channel.send(embed=embed_log)
    async def on_member_join(self, member):
        guild_id = str(member.guild.id)
        member_mention = str(member.mention)
        welcomer_channel_id = welcomer_settings.get(guild_id)
        if welcomer_channel_id:
            welcomer_channel = member.guild.get_channel(welcomer_channel_id)
            if welcomer_channel:
                existing_image = Image.open(f'{global_path}core/template_welcome.png')
                font = ImageFont.truetype(font_path, 12)
                draw = ImageDraw.Draw(existing_image)
                server = member.guild
                server_member_count = server.member_count
                white_color = (255, 255, 255)
                draw.text((153, 195), str(server_member_count), fill=white_color, font=font)
                if member.avatar.url:
                    response = requests.get(member.avatar.url)
                    if response.status_code == 200:
                        avatar_image = Image.open(io.BytesIO(response.content))
                        avatar_image = avatar_image.resize((77, 73))
                        mask = Image.new("L", avatar_image.size, 0)
                        draw = ImageDraw.Draw(mask)
                        draw.ellipse((0, 0, mask.size[0], mask.size[1]), fill=255)
                        avatar_image.putalpha(mask)
                        existing_image.paste(avatar_image, (163, 54), mask=mask)
                image_bytes = io.BytesIO()
                existing_image.save(image_bytes, format='PNG')
                image_bytes.seek(0)
                await welcomer_channel.send(member_mention, file=discord.File(image_bytes, filename='welcome.png'))
        audit_log_channel_id = audit_log_settings.get(str(member.guild.id))
        if audit_log_channel_id:
            audit_log_channel = member.guild.get_channel(audit_log_channel_id)
            if audit_log_channel:
                age = member.created_at.strftime("%b %d, %Y")
                embed_log = discord.Embed(
                    title=f"Member joined",
                    description=f"❯ the member: {member.mention}[`{member.id}`] has joined the server.",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.purple()
                )
                embed_log.add_field(name="Account creation date", value=age)
                await audit_log_channel.send(embed=embed_log)
    current_dir = os.path.dirname(os.path.abspath(f'{global_path}core/arial.ttf'))
    font_path = os.path.join(current_dir, 'arial.ttf')
    async def on_member_remove(self, member):
        guild_id = str(member.guild.id)
        farwell_channel_id = farweller_settings.get(guild_id)
        if farwell_channel_id:
            farwell_channel = member.guild.get_channel(farwell_channel_id)
            if farwell_channel:
                existing_image = Image.open(f'{global_path}/core/template_goodbye.png')
                font = ImageFont.truetype(font_path, 12)
                draw = ImageDraw.Draw(existing_image)
                server = member.guild
                server_member_count = server.member_count
                white_color = (255, 255, 255)
                draw.text((153, 195), str(server_member_count), fill=white_color, font=font)
                if member.avatar.url:
                        avatar_image = Image.open(io.BytesIO(member.avatar.ur))
                        avatar_image = avatar_image.resize((77, 73))
                        mask = Image.new("L", avatar_image.size, 0)
                        draw = ImageDraw.Draw(mask)
                        draw.ellipse((0, 0, mask.size[0], mask.size[1]), fill=255)
                        avatar_image.putalpha(mask)
                        existing_image.paste(avatar_image, (163, 54), mask=mask)
                image_bytes = io.BytesIO()
                existing_image.save(image_bytes, format='PNG')
                image_bytes.seek(0)
                await farwell_channel.send(file=discord.File(image_bytes, filename='goodbye.png'))
        audit_log_channel_id = audit_log_settings.get(str(member.guild.id))
        if audit_log_channel_id:
            audit_log_channel = member.guild.get_channel(audit_log_channel_id)
            if audit_log_channel:
                embed_log = discord.Embed(
                    title=f"Member leaved",
                    description=f"❯ the member: {member.mention}[`{member.id}`] has left the server.",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.purple()
                )
                await audit_log_channel.send(embed=embed_log)
        if member.guild.me.guild_permissions.view_audit_log:
            async for entry in member.guild.audit_logs(limit=1):
                if entry.action == discord.AuditLogAction.ban:
                    audit_log_channel_id = audit_log_settings.get(str(member.guild.id))
                    if audit_log_channel_id:
                        audit_log_channel = member.guild.get_channel(audit_log_channel_id)
                        if audit_log_channel:
                            embed_log = discord.Embed(
                                title=f"Member banned",
                                description=f"❯ the member: {member.mention}[`{member.id}`] has been banned by {entry.user.mention} (`{entry.user.id}`) Reason: `{entry.reason or 'None'}`",
                                timestamp=datetime.datetime.utcnow(),
                                color=discord.Color.purple()
                            )
                            await audit_log_channel.send(embed=embed_log)
                if entry.action == discord.AuditLogAction.kick:
                    audit_log_channel_id = audit_log_settings.get(str(member.guild.id))
                    if audit_log_channel_id:
                        audit_log_channel = member.guild.get_channel(audit_log_channel_id)
                        if audit_log_channel:
                            embed_log = discord.Embed(
                                title=f"Member kicked",
                                description=f"❯ the member: {member.mention}[`{member.id}`] has been kicked by {entry.user.mention} (`{entry.user.id}`) Reason: `{entry.reason or 'None'}`",
                                timestamp=datetime.datetime.utcnow(),
                                color=discord.Color.purple()
                            )
                            await audit_log_channel.send(embed=embed_log)
        else:
            audit_log_channel_id = audit_log_settings.get(str(member.guild.id))
            if audit_log_channel_id:
                audit_log_channel = member.guild.get_channel(audit_log_channel_id)
                if audit_log_channel:
                    embed_log = discord.Embed(
                        title=f"Log Error! 🚫",
                        description=f"❯ The bot doesn't have the required permissions. (`view_audit_log`)",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.purple()
                    )
                    await audit_log_channel.send(embed=embed_log)
                    return
    async def on_member_unban(self, guild, member):
        if guild.me.guild_permissions.view_audit_log:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban):
                if entry.action == discord.AuditLogAction.unban and entry.target == member:
                    audit_log_channel_id = audit_log_settings.get(str(guild.id))
                    if audit_log_channel_id:
                        audit_log_channel = guild.get_channel(audit_log_channel_id)
                        if audit_log_channel:
                            embed_log = discord.Embed(
                                title="Member Unbanned",
                                description=f"❯ the member with the id: `{member.id}`] has been unbanned by {entry.user.mention}[`{entry.user.id}`]",
                                timestamp=datetime.datetime.utcnow(),
                                color=discord.Color.purple()
                            )
                            await audit_log_channel.send(embed=embed_log)
        else:
            audit_log_channel_id = audit_log_settings.get(str(guild.guild.id))
            if audit_log_channel_id:
                audit_log_channel = guild.guild.get_channel(audit_log_channel_id)
                if audit_log_channel:
                    embed_log = discord.Embed(
                        title=f"Log Error! 🚫",
                        description=f"❯ The bot doesn't have the required permissions. (`view_audit_log`)",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.purple()
                    )
                    await audit_log_channel.send(embed=embed_log)
                    return
    async def on_guild_update(self, before, after):
        if before.guild.me.guild_permissions.view_audit_log:
            async for entry in before.guild.audit_logs(limit=1):
                if entry.action == discord.AuditLogAction.channel_update and entry.target.id == after.id:
                    audit_log_channel_id = audit_log_settings.get(str(before.guild.id))
                    if audit_log_channel_id:
                        audit_log_channel = before.guild.get_channel(audit_log_channel_id)
                        if audit_log_channel:
                            if after.name != before.name:
                                embed_log = discord.Embed(
                                    title="server Renamed",
                                    description=f"❯ the server has been renamed by: {entry.user.mention}[`{entry.user.id}`].\n"
                                                f"   Old Name: `{before.name}`\n   New Name: `{after.name}`",
                                    timestamp=datetime.datetime.utcnow(),
                                    color=discord.Color.purple()
                                )
                                await audit_log_channel.send(embed=embed_log)
                            else:
                                embed_log = discord.Embed(
                                    title="server updated",
                                    description=f"❯ the server has been updated by {entry.user.mention}[`{entry.user.id}`]",
                                    timestamp=datetime.datetime.utcnow(),
                                    color=discord.Color.purple()
                                )
                                await audit_log_channel.send(embed=embed_log)
        else:
            audit_log_channel_id = audit_log_settings.get(str(before.guild.id))
            if audit_log_channel_id:
                audit_log_channel = before.guild.get_channel(audit_log_channel_id)
                if audit_log_channel:
                    embed_log = discord.Embed(
                        title=f"Log Error! 🚫",
                        description=f"❯ The bot doesn't have the required permissions. (`view_audit_log`)",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.purple()
                    )
                    await audit_log_channel.send(embed=embed_log)
                    return
    async def on_guild_channel_create(self, channel):
        if channel.guild.me.guild_permissions.view_audit_log:
            async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create):
                if entry.action == discord.AuditLogAction.channel_create:
                    audit_log_channel_id = audit_log_settings.get(str(channel.guild.id))
                    if audit_log_channel_id:
                        audit_log_channel = channel.guild.get_channel(audit_log_channel_id)
                        if audit_log_channel:
                            embed_log = discord.Embed(
                                title="Channel Created",
                                description=f"❯ the channel: {channel.mention}[`{channel.id}`] has been created by {entry.user.mention}[`{entry.user.id}`]",
                                timestamp=datetime.datetime.utcnow(),
                                color=discord.Color.purple()
                            )
                            await audit_log_channel.send(embed=embed_log)
        else:
            audit_log_channel_id = audit_log_settings.get(str(channel.guild.id))
            if audit_log_channel_id:
                audit_log_channel = channel.guild.get_channel(audit_log_channel_id)
                if audit_log_channel:
                    embed_log = discord.Embed(
                        title=f"Log Error! 🚫",
                        description=f"❯ The bot doesn't have the required permissions. (`view_audit_log`)",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.purple()
                    )
                    await audit_log_channel.send(embed=embed_log)
                    return
    async def on_guild_channel_delete(self, channel):
        if channel.guild.me.guild_permissions.view_audit_log:
            async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
                if entry.action == discord.AuditLogAction.channel_delete:
                    audit_log_channel_id = audit_log_settings.get(str(channel.guild.id))
                    if audit_log_channel_id:
                        audit_log_channel = channel.guild.get_channel(audit_log_channel_id)
                        if audit_log_channel:
                            embed_log = discord.Embed(
                                title="Channel Deleted",
                                description=f"❯ the channel with the name: `{channel.name}` has been deleted by {entry.user.mention}[`{entry.user.id}`]",
                                timestamp=datetime.datetime.utcnow(),
                                color=discord.Color.purple()
                            )
                            await audit_log_channel.send(embed=embed_log)
        else:
            audit_log_channel_id = audit_log_settings.get(str(channel.guild.id))
            if audit_log_channel_id:
                audit_log_channel = channel.guild.get_channel(audit_log_channel_id)
                if audit_log_channel:
                    embed_log = discord.Embed(
                        title=f"Log Error! 🚫",
                        description=f"❯ The bot doesn't have the required permissions. (`view_audit_log`)",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.purple()
                    )
                    await audit_log_channel.send(embed=embed_log)
                    return
    async def on_guild_channel_update(self, before, after: discord.TextChannel):
        if before.guild.me.guild_permissions.view_audit_log:
            async for entry in before.guild.audit_logs(limit=1):
                if entry.action == discord.AuditLogAction.overwrite_update and entry.target.id == after.id:
                    audit_log_channel_id = audit_log_settings.get(str(before.guild.id))
                    if audit_log_channel_id:
                        audit_log_channel = before.guild.get_channel(audit_log_channel_id)
                        if audit_log_channel:
                            embed_log = discord.Embed(
                                title="Channel Permissions Changed",
                                description=f"❯ the channel: {after.mention}[`{after.id}`] Permissions has been changed by: {entry.user.mention}[`{entry.user.id}`]",
                                timestamp=datetime.datetime.utcnow(),
                                color=discord.Color.purple()
                            )
                            await audit_log_channel.send(embed=embed_log)
                if entry.action == discord.AuditLogAction.channel_update and entry.target.id == after.id:
                    audit_log_channel_id = audit_log_settings.get(str(before.guild.id))
                    if audit_log_channel_id:
                        audit_log_channel = before.guild.get_channel(audit_log_channel_id)
                        if audit_log_channel:
                            if after.name != before.name:
                                embed_log = discord.Embed(
                                    title="Channel Renamed",
                                    description=f"❯ the Channel: {after.mention}[`{after.id}`] has been renamed by {entry.user.mention}[`{entry.user.id}`].\n"
                                                f"   Old Name: `{before.name}`\n   New Name: `{after.name}`",
                                    timestamp=datetime.datetime.utcnow(),
                                    color=discord.Color.purple()
                                )
                                await audit_log_channel.send(embed=embed_log)
                            else:
                                embed_log = discord.Embed(
                                    title="Channel updated",
                                    description=f"❯ the Channel: {after.mention}[`{after.id}`] has been updated by {entry.user.mention}[`{entry.user.id}`]",
                                    timestamp=datetime.datetime.utcnow(),
                                    color=discord.Color.purple()
                                )
                                await audit_log_channel.send(embed=embed_log)
        else:
            audit_log_channel_id = audit_log_settings.get(str(before.guild.id))
            if audit_log_channel_id:
                audit_log_channel = before.guild.get_channel(audit_log_channel_id)
                if audit_log_channel:
                    embed_log = discord.Embed(
                        title=f"Log Error! 🚫",
                        description=f"❯ The bot doesn't have the required permissions. (`view_audit_log`)",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.purple()
                    )
                    await audit_log_channel.send(embed=embed_log)
                    return
    async def on_thread_create(self, thread: discord.Thread):
        if thread.guild.me.guild_permissions.view_audit_log:
            async for entry in thread.guild.audit_logs(limit=1, action=discord.AuditLogAction.thread_create):
                if entry.action == discord.AuditLogAction.thread_create:
                    audit_log_channel_id = audit_log_settings.get(str(thread.guild.id))
                    if audit_log_channel_id:
                        audit_log_channel = thread.guild.get_channel(audit_log_channel_id)
                        if audit_log_channel:
                            embed_log = discord.Embed(
                                title="thread created",
                                description=f"❯ the thread {thread.mention}[`{thread.id}`] has been created by: {entry.user.mention}[`{entry.user.id}`] parent channel: {thread.parent.mention}",
                                timestamp=datetime.datetime.utcnow(),
                                color=discord.Color.purple()
                            )
                            await audit_log_channel.send(embed=embed_log)
        else:
            audit_log_channel_id = audit_log_settings.get(str(thread.guild.id))
            if audit_log_channel_id:
                audit_log_channel = thread.guild.get_channel(audit_log_channel_id)
                if audit_log_channel:
                    embed_log = discord.Embed(
                        title="Log Error! 🚫",
                        description=f"❯ The bot doesn't have the required permissions. (`view_audit_log`)",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.purple()
                    )
                    await audit_log_channel.send(embed=embed_log)
                    return
    async def on_thread_delete(self, thread: discord.Thread):
        if thread.guild.me.guild_permissions.view_audit_log:
            async for entry in thread.guild.audit_logs(limit=1, action=discord.AuditLogAction.thread_delete):
                if entry.action == discord.AuditLogAction.thread_delete:
                    audit_log_channel_id = audit_log_settings.get(str(thread.guild.id))
                    if audit_log_channel_id:
                        audit_log_channel = thread.guild.get_channel(audit_log_channel_id)
                        if audit_log_channel:
                            embed_log = discord.Embed(
                                title="thread deleted",
                                description=f"❯ the thread with the name: `{thread.name}` has been deleted by: {entry.user.mention}[`{entry.user.id}`] parent channel: {thread.parent.mention}",
                                timestamp=datetime.datetime.utcnow(),
                                color=discord.Color.purple()
                            )
                            await audit_log_channel.send(embed=embed_log)
        else:
            audit_log_channel_id = audit_log_settings.get(str(thread.guild.id))
            if audit_log_channel_id:
                audit_log_channel = thread.guild.get_channel(audit_log_channel_id)
                if audit_log_channel:
                    embed_log = discord.Embed(
                        title="Log Error! 🚫",
                        description=f"❯ The bot doesn't have the required permissions. (`view_audit_log`)",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.purple()
                    )
                    await audit_log_channel.send(embed=embed_log)
                    return
    async def on_thread_update(self, before, after):
        if before.guild.me.guild_permissions.view_audit_log:
            async for entry in before.guild.audit_logs(limit=1, action=discord.AuditLogAction.thread_update):
                if entry.action == discord.AuditLogAction.thread_update and entry.target.id == after.id:
                    audit_log_channel_id = audit_log_settings.get(str(before.guild.id))
                    if audit_log_channel_id:
                        audit_log_channel = before.guild.get_channel(audit_log_channel_id)
                        if audit_log_channel:
                            if after.name != before.name:
                                embed_log = discord.Embed(
                                    title="thread Renamed",
                                    description=f"❯ the thread: {after.mention}[`{after.id}`] has been renamed by {entry.user.mention}[`{entry.user.id}`] parent channel: {after.parent.mention}\n"
                                                f"   Old Name: `{before.name}`\n   New Name: `{after.name}`",
                                    timestamp=datetime.datetime.utcnow(),
                                    color=discord.Color.purple()
                                )
                                await audit_log_channel.send(embed=embed_log)
                            else:
                                embed_log = discord.Embed(
                                    title="thread updated",
                                    description=f"❯ the thread: {after.mention}[`{after.id}`] has been updated by {entry.user.mention}[`{entry.user.id}`] parent channel: {after.parent.mention}",
                                    timestamp=datetime.datetime.utcnow(),
                                    color=discord.Color.purple()
                                )
                                await audit_log_channel.send(embed=embed_log)
        else:
            audit_log_channel_id = audit_log_settings.get(str(before.guild.id))
            if audit_log_channel_id:
                audit_log_channel = before.guild.get_channel(audit_log_channel_id)
                if audit_log_channel:
                    embed_log = discord.Embed(
                        title="Log Error! 🚫",
                        description=f"❯ The bot doesn't have the required permissions. (`view_audit_log`)",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.purple()
                    )
                    await audit_log_channel.send(embed=embed_log)
                    return
    async def on_webhooks_update(self, channel):
        if channel.guild.me.guild_permissions.view_audit_log:
            async for entry in channel.guild.audit_logs(limit=1):
                if entry.action == discord.AuditLogAction.webhook_create:
                    audit_log_channel_id = audit_log_settings.get(str(channel.guild.id))
                    if audit_log_channel_id:
                        audit_log_channel = channel.guild.get_channel(audit_log_channel_id)
                        if audit_log_channel:
                            embed_log = discord.Embed(
                                title="webhook created",
                                description=f"❯ a webhook has been created in the channel {channel.mention}[`{channel.id}`] by: {entry.user.mention}[`{entry.user.id}`]",
                                timestamp=datetime.datetime.utcnow(),
                                color=discord.Color.purple()
                            )
                            await audit_log_channel.send(embed=embed_log)
                            return
                if entry.action == discord.AuditLogAction.webhook_delete:
                    audit_log_channel_id = audit_log_settings.get(str(channel.guild.id))
                    if audit_log_channel_id:
                        audit_log_channel = channel.guild.get_channel(audit_log_channel_id)
                        if audit_log_channel:
                            embed_log = discord.Embed(
                                title="Webhook deleted",
                                description=f"❯ a webhook has been deleted in the channel {channel.mention}[`{channel.id}`] by: {entry.user.mention}[`{entry.user.id}`]",
                                timestamp=datetime.datetime.utcnow(),
                                color=discord.Color.purple()
                            )
                            await audit_log_channel.send(embed=embed_log)
                if entry.action == discord.AuditLogAction.webhook_update:
                    audit_log_channel_id = audit_log_settings.get(str(channel.guild.id))
                    if audit_log_channel_id:
                        audit_log_channel = channel.guild.get_channel(audit_log_channel_id)
                        if audit_log_channel:
                            if entry.after.name != entry.before.name:
                                embed_log = discord.Embed(
                                    title="Webhook Renamed",
                                    description=f"❯ The webhook in channel {channel.mention}[`{channel.id}`] has been renamed by {entry.user.mention}[`{entry.user.id}`]\n"
                                                f"   Old Name: `{entry.before.name}`\n   New Name: `{entry.after.name}`",
                                    timestamp=datetime.datetime.utcnow(),
                                    color=discord.Color.purple()
                                )
                                await audit_log_channel.send(embed=embed_log)
                            else:
                                embed_log = discord.Embed(
                                    title="Webhook updated",
                                    description=f"❯ the webhook: {channel.mention}[`{channel.id}`] has been updated by {entry.user.mention}[`{entry.user.id}`]",
                                    timestamp=datetime.datetime.utcnow(),
                                    color=discord.Color.purple()
                                )
                                await audit_log_channel.send(embed=embed_log)
        else:
            audit_log_channel_id = audit_log_settings.get(str(channel.guild.id))
            if audit_log_channel_id:
                audit_log_channel = channel.guild.get_channel(audit_log_channel_id)
                if audit_log_channel:
                    embed_log = discord.Embed(
                        title="Log Error! 🚫",
                        description=f"❯ The bot doesn't have the required permissions. (`view_audit_log`)",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.purple()
                    )
                    await audit_log_channel.send(embed=embed_log)
                    return
    async def on_guild_role_create(self, role):
        if role.guild.me.guild_permissions.view_audit_log:
            async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_create):
                if entry.action == discord.AuditLogAction.role_create:
                    audit_log_channel_id = audit_log_settings.get(str(role.guild.id))
                    if audit_log_channel_id:
                        audit_log_channel = role.guild.get_channel(audit_log_channel_id)
                        if audit_log_channel:
                            embed_log = discord.Embed(
                                title="Role Created",
                                description=f"❯ the role: {role.mention}[`{role.id}`] has been created by {entry.user.mention}[`{entry.user.id}`]",
                                timestamp=datetime.datetime.utcnow(),
                                color=discord.Color.purple()
                            )
                            await audit_log_channel.send(embed=embed_log)
        else:
            audit_log_channel_id = audit_log_settings.get(str(role.guild.id))
            if audit_log_channel_id:
                audit_log_channel = role.guild.get_channel(audit_log_channel_id)
                if audit_log_channel:
                    embed_log = discord.Embed(
                        title=f"Log Error! 🚫",
                        description=f"❯ The bot doesn't have the required permissions. (`view_audit_log`)",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.purple()
                    )
                    await audit_log_channel.send(embed=embed_log)
                    return
    async def on_guild_role_delete(self, role):
        if role.guild.me.guild_permissions.view_audit_log:
            async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
                if entry.action == discord.AuditLogAction.role_delete:
                    audit_log_channel_id = audit_log_settings.get(str(role.guild.id))
                    if audit_log_channel_id:
                        audit_log_channel = role.guild.get_channel(audit_log_channel_id)
                        if audit_log_channel:
                            embed_log = discord.Embed(
                                title="Role Deleted",
                                description=f"❯ the role with the name: `{role.name}` has been deleted by: {entry.user.mention}[`{entry.user.id}`]",
                                timestamp=datetime.datetime.utcnow(),
                                color=discord.Color.purple()
                            )
                            await audit_log_channel.send(embed=embed_log)
        else:
            audit_log_channel_id = audit_log_settings.get(str(role.guild.id))
            if audit_log_channel_id:
                audit_log_channel = role.guild.get_channel(audit_log_channel_id)
                if audit_log_channel:
                    embed_log = discord.Embed(
                        title=f"Log Error! 🚫",
                        description=f"❯ The bot doesn't have the required permissions. (`view_audit_log`)",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.purple()
                    )
                    await audit_log_channel.send(embed=embed_log)
                    return
    async def on_guild_role_update(self, before, after):
        if before.guild.me.guild_permissions.view_audit_log:
            async for entry in before.guild.audit_logs(limit=1):
                if entry.action == discord.AuditLogAction.role_update and entry.target.id == after.id:
                    audit_log_channel_id = audit_log_settings.get(str(before.guild.id))
                    if audit_log_channel_id:
                        audit_log_channel = before.guild.get_channel(audit_log_channel_id)
                        if audit_log_channel:
                            embed_log = discord.Embed(
                                title="Role Permissions Changed",
                                description=f"❯ the role: {after.mention}[`{after.id}`] Permissions have been changed by: {entry.user.mention}[`{entry.user.id}`]",
                                timestamp=datetime.datetime.utcnow(),
                                color=discord.Color.purple()
                            )
                            await audit_log_channel.send(embed=embed_log)
                if entry.action == discord.AuditLogAction.role_update and entry.target.id == after.id:
                    audit_log_channel_id = audit_log_settings.get(str(before.guild.id))
                    if audit_log_channel_id:
                        audit_log_channel = before.guild.get_channel(audit_log_channel_id)
                        if audit_log_channel:
                            if after.name != before.name:
                                embed_log = discord.Embed(
                                    title="Role Renamed",
                                    description=f"❯ Role {after.mention}[`{after.id}`] has been renamed by {entry.user.mention}[`{entry.user.id}`].\n"
                                                f"   Old Name: `{before.name}`\n   New Name: `{after.name}`",
                                    timestamp=datetime.datetime.utcnow(),
                                    color=discord.Color.purple()
                                )
                                await audit_log_channel.send(embed=embed_log)
                            else:
                                embed_log = discord.Embed(
                                    title="Role updated",
                                    description=f"❯ the Role: {after.mention}[`{after.id}`] has been updated by {entry.user.mention}[`{entry.user.id}`]",
                                    timestamp=datetime.datetime.utcnow(),
                                    color=discord.Color.purple()
                                )
                                await audit_log_channel.send(embed=embed_log)
        else:
            audit_log_channel_id = audit_log_settings.get(str(before.guild.id))
            if audit_log_channel_id:
                audit_log_channel = before.guild.get_channel(audit_log_channel_id)
                if audit_log_channel:
                    embed_log = discord.Embed(
                        title="Log Error! 🚫",
                        description=f"❯ The bot doesn't have the required permissions. (`view_audit_log`)",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.purple()
                    )
                    await audit_log_channel.send(embed=embed_log)
                    return
    async def on_member_update(self, before, after):
        added_roles = set(after.roles) - set(before.roles)
        removed_roles = set(before.roles) - set(after.roles)
        added_roles = set(after.roles) - set(before.roles)
        removed_roles = set(before.roles) - set(after.roles)
        if after.guild.me.guild_permissions.view_audit_log:
            async for entry in after.guild.audit_logs(limit=1):
                if entry.action == discord.AuditLogAction.member_role_update:
                    audit_log_channel_id = audit_log_settings.get(str(after.guild.id))
                    if audit_log_channel_id:
                        audit_log_channel = after.guild.get_channel(audit_log_channel_id)
                        if audit_log_channel:
                            embed_log = discord.Embed(
                                title=f"Roles updated",
                                description=f"❯ {after.mention}[`{after.id}`] roles has been updated by: {entry.user.mention}[`{entry.user.id}`]",
                                timestamp=datetime.datetime.utcnow(),
                                color=discord.Color.purple()
                            )
                            if added_roles:
                                embed_log.add_field(name="Roles Added", value=', '.join(role.mention for role in added_roles), inline=False)
                            if removed_roles:
                                embed_log.add_field(name="Roles Removed", value=', '.join(role.mention for role in removed_roles), inline=False)

                            await audit_log_channel.send(embed=embed_log)
        else:
            audit_log_channel_id = audit_log_settings.get(str(after.guild.id))
            if audit_log_channel_id:
                audit_log_channel = after.guild.get_channel(audit_log_channel_id)
                if audit_log_channel:
                    embed_log = discord.Embed(
                        title=f"Log Error! 🚫",
                        description=f"❯ The bot doesn't have the required permissions. (`view_audit_log`)",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.purple()
                    )
                    await audit_log_channel.send(embed=embed_log)
                    return
        if before.nick != after.nick:
            audit_log_channel_id = audit_log_settings.get(str(after.guild.id))
            if audit_log_channel_id:
                audit_log_channel = after.guild.get_channel(audit_log_channel_id)
                if audit_log_channel:
                    embed_log = discord.Embed(
                        title="Nickname Changed",
                        description=f"❯ {after.mention}'s nickname has been changed from `{before.nick}` to `{after.nick}`",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.purple()
                    )
                    await audit_log_channel.send(embed=embed_log)
client = client()
if __name__ == "__main__":
    client.run(token_main, reconnect=True)