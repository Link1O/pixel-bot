import discord
from discord import app_commands
from discord.app_commands import Group
from discord.ui import View
from discord.ext import commands
from typing import Literal, Union
import datetime
import asyncio
import humanize
import string
from startup import deleted_messages
from utils.tools import *
locked_channels = {}
unlocked_channels = {}
locked_vc_channels = {}
unlocked_vc_channels = {}
muted_users = {}
class moderation(commands.Cog):
    def __init__(self, client):
        super().__init__()
        self.client = client
    @app_commands.command(name="lock", description="locks the channel")
    async def lock(self, interaction: discord.Interaction, channel: discord.TextChannel = None, duration: str = None):
        if channel is None:
            channel = interaction.channel
        overwrites = channel.overwrites_for(interaction.guild.default_role)
        if interaction.user.guild_permissions.manage_channels:
            if not overwrites.send_messages is False:
                if not duration:
                    try:
                        overwrites.send_messages = False
                        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrites)
                    except:
                        embed_perm_error = discord.Embed(
                            title="Error! 🚫",
                            description="❯ The bot doesn't have the required permissions. (`manage_channels`)",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.orange()
                        )
                        await interaction.response.send_message(embed=embed_perm_error, ephemeral = True)
                        return
                    if channel.id in unlocked_channels:
                        del unlocked_channels[channel.id]
                    embed = discord.Embed(
                        title="Channel Locked",
                        description=f"{channel.mention} has been locked",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.purple()
                    )
                    await interaction.response.send_message(embed=embed)
                    guild_id = str(interaction.guild.id)
                    mod_log_channel_id = mod_log_settings.get(guild_id)
                    if mod_log_channel_id:
                        mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                        if mod_log_channel:
                            embed_log = discord.Embed(
                                title="Channel Locked",
                                description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] locked: {channel.mention}",
                                timestamp=datetime.datetime.now(datetime.timezone.utc),
                                color=discord.Color.purple()
                            )
                            await mod_log_channel.send(embed=embed_log)
                    return
                duration = parse_duration(duration)
                if duration <= 0:
                    embed_time_error = discord.Embed(
                        title="Error! 🚫",
                        description="❯ Invalid duration format. Use 'd' for days or 'h' for hours or '1m' for minutes or '1s' for seconds.",
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_time_error, ephemeral = True)
                    return
                if duration:
                    try:
                        overwrites.send_messages = False
                        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrites)
                    except:
                        embed_perm_error = discord.Embed(
                            title="Error! 🚫",
                            description="❯ The bot doesn't have the required permissions. (`manage_channels`)",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.orange()
                        )
                        await interaction.response.send_message(embed=embed_perm_error, ephemeral = True)
                        return
                    unlock_time = datetime.datetime.now() + datetime.timedelta(seconds=duration)
                    locked_channels[channel.id] = unlock_time
                    if channel.id in unlocked_channels:
                        del unlocked_channels[channel.id]
                    embed = discord.Embed(
                        title="Channel Locked",
                        description=f"{channel.mention} has been locked, duration: {humanize.naturaldelta(datetime.timedelta(seconds=duration))}.",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.purple()
                    )
                    await interaction.response.send_message(embed=embed)
                    guild_id = str(interaction.guild.id)
                    mod_log_channel_id = mod_log_settings.get(guild_id)
                    if mod_log_channel_id:
                        mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                        if mod_log_channel:
                            embed_log = discord.Embed(
                                title="Channel Locked",
                                description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] locked: {channel.mention} duration: {humanize.naturaldelta(datetime.timedelta(seconds=duration))}.",
                                timestamp=datetime.datetime.now(datetime.timezone.utc),
                                color=discord.Color.purple()
                            )
                            await mod_log_channel.send(embed=embed_log)
                    await asyncio.sleep(duration)
                    unlock_time = locked_channels.get(channel.id)
                    if unlock_time and datetime.datetime.now() >= unlock_time:
                        overwrites.send_messages = True
                        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrites)
                        del locked_channels[channel.id]
                        unlock_embed = discord.Embed(
                            title="Channel automatically Unlocked",
                            description=f"❯ {channel.mention} has been automatically unlocked.",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.purple()
                        )
                        await interaction.channel.send(embed=unlock_embed)
                    guild_id = str(interaction.guild.id)
                    mod_log_channel_id = mod_log_settings.get(guild_id)
                    if mod_log_channel_id:
                        mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                        if mod_log_channel:
                            if unlock_time and datetime.datetime.now() >= unlock_time:
                                embed_log = discord.Embed(
                                    title="Channel automatically Unlocked",
                                    description=f"❯ {channel.mention} has been automatically unlocked.",
                                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                                    color=discord.Color.purple()
                                )
                                await mod_log_channel.send(embed=embed_log)
                    overwrites.send_messages = True
                    await channel.set_permissions(interaction.guild.default_role, overwrite=overwrites)
            else:
                embed_error_lock = discord.Embed(
                    title="Error! 🚫",
                    description="the channel seems to be already locked.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error_lock, ephemeral=True)
        else:
            embed_error = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`manage_channels`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True) 
    @app_commands.command(name="unlock", description="unlocks the channel")
    async def unlock(self, interaction: discord.Interaction, channel: discord.TextChannel = None, duration: str = None):
        if channel is None:
            channel = interaction.channel
        overwrites = channel.overwrites_for(interaction.guild.default_role)
        if interaction.user.guild_permissions.manage_channels:
            if not overwrites.send_messages is True:
                if not duration:
                    try:
                        overwrites.send_messages = True
                        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrites)
                    except:
                        embed_perm_error = discord.Embed(
                            title="Error! 🚫",
                            description="❯ The bot doesn't have the required permissions. (`manage_channels`)",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.orange()
                        )
                        await interaction.response.send_message(embed=embed_perm_error, ephemeral = True)
                        return
                    if channel.id in locked_channels:
                        del locked_channels[channel.id]
                    embed = discord.Embed(
                        title="channel unlocked",
                        description=f"{channel.mention} has been unlocked",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.purple()
                    )
                    await interaction.response.send_message(embed=embed)
                    guild_id = str(interaction.guild.id)
                    mod_log_channel_id = mod_log_settings.get(guild_id)
                    if mod_log_channel_id:
                        mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                        if mod_log_channel:
                            embed_log = discord.Embed(
                                title="channel unlocked",
                                description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] unlocked: {channel.mention}",
                                timestamp=datetime.datetime.now(datetime.timezone.utc),
                                color=discord.Color.purple()
                            )
                            await mod_log_channel.send(embed=embed_log)
                    return
                duration = parse_duration(duration)
                if duration <= 0:
                    embed_time_error = discord.Embed(
                        title="Error! 🚫",
                        description="❯ Invalid duration format. Use 'd' for days or 'h' for hours or '1m' for minutes or '1s' for seconds.",
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_time_error, ephemeral = True)
                    return
                if duration:
                    try:
                        overwrites.send_messages = True
                        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrites)
                    except:
                        embed_perm_error = discord.Embed(
                            title="Error! 🚫",
                            description="❯ The bot doesn't have the required permissions. (`manage_channels`)",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.orange()
                        )
                        await interaction.response.send_message(embed=embed_perm_error, ephemeral = True)
                        return
                    lock_time = datetime.datetime.now() + datetime.timedelta(seconds=duration)
                    unlocked_channels[channel.id] = lock_time
                    if channel.id in locked_channels:
                        del locked_channels[channel.id]
                    embed = discord.Embed(
                        title="channel unlocked",
                        description=f"{channel.mention} has been unlocked, duration: {humanize.naturaldelta(datetime.timedelta(seconds=duration))}.",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.purple()
                    )
                    await interaction.response.send_message(embed=embed)
                    guild_id = str(interaction.guild.id)
                    mod_log_channel_id = mod_log_settings.get(guild_id)
                    if mod_log_channel_id:
                        mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                        if mod_log_channel:
                            embed_log = discord.Embed(
                                title="channel unlocked",
                                description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] unlocked: {channel.mention} duration: {humanize.naturaldelta(datetime.timedelta(seconds=duration))}.",
                                timestamp=datetime.datetime.now(datetime.timezone.utc),
                                color=discord.Color.purple()
                            )
                            await mod_log_channel.send(embed=embed_log)
                    await asyncio.sleep(duration)
                    lock_time = unlocked_channels.get(channel.id)
                    if lock_time and datetime.datetime.now() >= lock_time:
                        overwrites.send_messages = False
                        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrites)
                        del unlocked_channels[channel.id]
                        unlock_embed = discord.Embed(
                            title="channel automatically locked",
                            description=f"❯ {channel.mention} has been automatically locked.",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.purple()
                        )
                        await interaction.channel.send(embed=unlock_embed)
                    guild_id = str(interaction.guild.id)
                    mod_log_channel_id = mod_log_settings.get(guild_id)
                    if mod_log_channel_id:
                        mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                        if mod_log_channel:
                            if lock_time and datetime.datetime.now() >= lock_time:
                                embed_log = discord.Embed(
                                    title="channel automatically locked",
                                    description=f"❯ {channel.mention} has been automatically locked.",
                                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                                    color=discord.Color.purple()
                                )
                                await mod_log_channel.send(embed=embed_log)
            else:
                embed_error_lock = discord.Embed(
                    title="Error! 🚫",
                    description="the channel seems to be already unlocked.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error_lock, ephemeral=True)
        else:
            embed_error = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`manage_channels`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)
    @app_commands.command(name="lock_vc", description="locks the voice channel channel")
    async def lock_vc(self, interaction: discord.Interaction, channel: discord.VoiceChannel, duration: str = None):
        if channel is None:
            channel = interaction.channel
        overwrites = channel.overwrites_for(interaction.guild.default_role)
        if interaction.user.guild_permissions.manage_channels:
            if not overwrites.connect is False:
                if not duration:
                    try:
                        overwrites.connect = False
                        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrites)
                    except:
                        embed_perm_error = discord.Embed(
                            title="Error! 🚫",
                            description="❯ The bot doesn't have the required permissions. (`manage_channels`)",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.orange()
                        )
                        await interaction.response.send_message(embed=embed_perm_error, ephemeral = True)
                        return
                    if channel.id in unlocked_vc_channels:
                        del unlocked_vc_channels[channel.id]
                    embed = discord.Embed(
                        title="voice channel locked",
                        description=f"{channel.mention} has been locked",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.purple()
                    )
                    await interaction.response.send_message(embed=embed)
                    guild_id = str(interaction.guild.id)
                    mod_log_channel_id = mod_log_settings.get(guild_id)
                    if mod_log_channel_id:
                        mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                        if mod_log_channel:
                            embed_log = discord.Embed(
                                title="voice channel locked",
                                description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] locked the voice channel: {channel.mention}",
                                timestamp=datetime.datetime.now(datetime.timezone.utc),
                                color=discord.Color.purple()
                            )
                            await mod_log_channel.send(embed=embed_log)
                    return
                duration = parse_duration(duration)
                if duration <= 0:
                    embed_time_error = discord.Embed(
                        title="Error! 🚫",
                        description="❯ Invalid duration format. Use 'd' for days or 'h' for hours or '1m' for minutes or '1s' for seconds.",
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_time_error, ephemeral = True)
                    return
                if duration:
                    try:
                        overwrites.connect = False
                        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrites)
                    except:
                        embed_perm_error = discord.Embed(
                            title="Error! 🚫",
                            description="❯ The bot doesn't have the required permissions. (`manage_channels`)",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.orange()
                        )
                        await interaction.response.send_message(embed=embed_perm_error, ephemeral = True)
                        return
                    unlock_vc_time = datetime.datetime.now() + datetime.timedelta(seconds=duration)
                    locked_vc_channels[channel.id] = unlock_vc_time
                    if channel.id in unlocked_vc_channels:
                        del unlocked_vc_channels[channel.id]
                    embed = discord.Embed(
                        title="voice channel locked",
                        description=f"{channel.mention} has been locked, duration: {humanize.naturaldelta(datetime.timedelta(seconds=duration))}.",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.purple()
                    )
                    await interaction.response.send_message(embed=embed)
                    guild_id = str(interaction.guild.id)
                    mod_log_channel_id = mod_log_settings.get(guild_id)
                    if mod_log_channel_id:
                        mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                        if mod_log_channel:
                            embed_log = discord.Embed(
                                title="voice channel locked",
                                description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] locked the voice channel: {channel.mention} duration: {humanize.naturaldelta(datetime.timedelta(seconds=duration))}.",
                                timestamp=datetime.datetime.now(datetime.timezone.utc),
                                color=discord.Color.purple()
                            )
                            await mod_log_channel.send(embed=embed_log)
                    await asyncio.sleep(duration)
                    unlock_vc_time = locked_vc_channels.get(channel.id)
                    if unlock_vc_time and datetime.datetime.now() >= unlock_vc_time:
                        overwrites.connect = True
                        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrites)
                        del locked_vc_channels[channel.id]
                        unlock_embed = discord.Embed(
                            title="voice channel automatically unlocked",
                            description=f"❯ {channel.mention} has been automatically unlocked.",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.purple()
                        )
                        await interaction.channel.send(embed=unlock_embed)
                    guild_id = str(interaction.guild.id)
                    mod_log_channel_id = mod_log_settings.get(guild_id)
                    if mod_log_channel_id:
                        mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                        if mod_log_channel:
                            if unlock_vc_time and datetime.datetime.now() >= unlock_vc_time:
                                embed_log = discord.Embed(
                                    title="voice channel automatically unlocked",
                                    description=f"❯ {channel.mention} has been automatically unlocked.",
                                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                                    color=discord.Color.purple()
                                )
                                await mod_log_channel.send(embed=embed_log)
                    overwrites.connect = True
                    await channel.set_permissions(interaction.guild.default_role, overwrite=overwrites)
            else:
                embed_error_lock = discord.Embed(
                    title="Error! 🚫",
                    description="the voice channel seems to be already locked.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error_lock, ephemeral=True)
        else:
            embed_error = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`manage_channels`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)
    @app_commands.command(name="unlock_vc", description="unlocks the voice channel")
    async def unlock_vc(self, interaction: discord.Interaction, channel: discord.VoiceChannel, duration: str = None):
        if channel is None:
            channel = interaction.channel
        overwrites = channel.overwrites_for(interaction.guild.default_role)
        if interaction.user.guild_permissions.manage_channels:
            if not overwrites.connect is True:
                if not duration:
                    try:
                        overwrites.connect = True
                        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrites)
                    except:
                        embed_perm_error = discord.Embed(
                            title="Error! 🚫",
                            description="❯ The bot doesn't have the required permissions. (`manage_channels`)",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.orange()
                        )
                        await interaction.response.send_message(embed=embed_perm_error, ephemeral = True)
                        return
                    if channel.id in locked_channels:
                        del locked_channels[channel.id]
                    embed = discord.Embed(
                        title="voice channel unlocked",
                        description=f"{channel.mention} has been unlocked",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.purple()
                    )
                    await interaction.response.send_message(embed=embed)
                    guild_id = str(interaction.guild.id)
                    mod_log_channel_id = mod_log_settings.get(guild_id)
                    if mod_log_channel_id:
                        mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                        if mod_log_channel:
                            embed_log = discord.Embed(
                                title="voice channel unlocked",
                                description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] unlocked the voice channel: {channel.mention}",
                                timestamp=datetime.datetime.now(datetime.timezone.utc),
                                color=discord.Color.purple()
                            )
                            await mod_log_channel.send(embed=embed_log)
                    return
                duration = parse_duration(duration)
                if duration <= 0:
                    embed_time_error = discord.Embed(
                        title="Error! 🚫",
                        description="❯ Invalid duration format. Use 'd' for days or 'h' for hours or '1m' for minutes or '1s' for seconds.",
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_time_error, ephemeral = True)
                    return
                if duration:
                    try:
                        overwrites.connect = True
                        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrites)
                    except:
                        embed_perm_error = discord.Embed(
                            title="Error! 🚫",
                            description="❯ The bot doesn't have the required permissions. (`manage_channels`)",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.orange()
                        )
                        await interaction.response.send_message(embed=embed_perm_error, ephemeral = True)
                        return
                    lock_vc_time = datetime.datetime.now() + datetime.timedelta(seconds=duration)
                    unlocked_vc_channels[channel.id] = lock_vc_time
                    if channel.id in locked_channels:
                        del locked_channels[channel.id]
                    embed = discord.Embed(
                        title="voice channel unlocked",
                        description=f"{channel.mention} has been unlocked, duration: {humanize.naturaldelta(datetime.timedelta(seconds=duration))}.",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.purple()
                    )
                    await interaction.response.send_message(embed=embed)
                    guild_id = str(interaction.guild.id)
                    mod_log_channel_id = mod_log_settings.get(guild_id)
                    if mod_log_channel_id:
                        mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                        if mod_log_channel:
                            embed_log = discord.Embed(
                                title="voice channel unlocked",
                                description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] unlocked the voice channel: {channel.mention} duration: {humanize.naturaldelta(datetime.timedelta(seconds=duration))}.",
                                timestamp=datetime.datetime.now(datetime.timezone.utc),
                                color=discord.Color.purple()
                            )
                            await mod_log_channel.send(embed=embed_log)
                    await asyncio.sleep(duration)
                    lock_vc_time = unlocked_vc_channels.get(channel.id)
                    if lock_vc_time and datetime.datetime.now() >= lock_vc_time:
                        overwrites.connect = False
                        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrites)
                        del unlocked_vc_channels[channel.id]
                        unlock_embed = discord.Embed(
                            title="voice channel automatically locked",
                            description=f"❯ {channel.mention} has been automatically locked.",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.purple()
                        )
                        await interaction.channel.send(embed=unlock_embed)
                    guild_id = str(interaction.guild.id)
                    mod_log_channel_id = mod_log_settings.get(guild_id)
                    if mod_log_channel_id:
                        mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                        if mod_log_channel:
                            if lock_vc_time and datetime.datetime.now() >= lock_vc_time:
                                embed_log = discord.Embed(
                                    title="voice channel automatically locked",
                                    description=f"❯ {channel.mention} has been automatically locked.",
                                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                                    color=discord.Color.purple()
                                )
                                await mod_log_channel.send(embed=embed_log)
                    overwrites.connect = True
                    await channel.set_permissions(interaction.guild.default_role, overwrite=overwrites)
            else:
                embed_error_lock = discord.Embed(
                    title="Error! 🚫",
                    description="the voice channel seems to be already locked.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error_lock, ephemeral=True)
        else:
            embed_error = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`manage_channels`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)
    @app_commands.command(name="purge", description="deletes messages based on the user input")
    async def purge(self, interaction: discord.Interaction, amount: app_commands.Range[int, 1, 300], channel: discord.TextChannel = None, member: discord.Member = None):
        if interaction.user.guild_permissions.manage_messages:
            if member and not channel:
                messages = []
                async for m in interaction.channel.history():
                    if len(messages) == amount:
                        break
                    if m.author == member:
                        messages.append(m)
                try:
                    await interaction.channel.delete_messages(messages)
                except discord.Forbidden:
                    embed_perm_error = discord.Embed(
                        title="Error! 🚫",
                        description="❯ The bot doesn't have the required permissions. (`manage_messages`)",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_perm_error, ephemeral=True)
                    return
                embed = discord.Embed(
                    title="Messages Purged",
                    description=f"❯ {int(amount)} messages were purged from: {member.mention}",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
                await interaction.channel.send(embed=embed)
                guild_id = str(interaction.guild.id)
                mod_log_channel_id = mod_log_settings.get(guild_id)
                if mod_log_channel_id:
                    mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                    if mod_log_channel:
                        embed_log = discord.Embed(
                            title="Messages Purged",
                            description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] purged {int(amount)} messages from: {member.mention}[`{member.id}`]",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.purple()
                        )
                        await mod_log_channel.send(embed=embed_log)
                return
            if channel and not member:
                try:
                    await channel.purge(limit=amount)
                except discord.Forbidden:
                    embed_perm_error = discord.Embed(
                        title="Error! 🚫",
                        description="❯ The bot doesn't have the required permissions. (`manage_messages`)",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_perm_error, ephemeral=True)
                    return
                embed = discord.Embed(
                    title="Messages Purged",
                    description=f"❯ {int(amount)} messages were purged in: {channel.mention}",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
                await interaction.channel.send(embed=embed, delete_after=3.5)
                if mod_log_channel_id:
                    mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                    if mod_log_channel:
                        embed_log = discord.Embed(
                            title="Messages Purged",
                            description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] purged {int(amount)} messages in: {channel.mention}[`{channel.id}`]",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.purple()
                        )
                        await mod_log_channel.send(embed=embed_log)
                return
            if member and channel:
                messages = []
                async for m in channel.history():
                    if len(messages) == amount:
                        break
                    if m.author == member:
                        messages.append(m)
                try:
                    await channel.delete_messages(messages)
                except discord.Forbidden:
                    embed_perm_error = discord.Embed(
                        title="Error! 🚫",
                        description="❯ The bot doesn't have the required permissions. (`manage_messages`)",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_perm_error, ephemeral=True)
                    return
                embed = discord.Embed(
                    title="Messages Purged",
                    description=f"❯ {int(amount)} messages were purged in: {channel.mention} from: {member.mention}",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
                await interaction.channel.send(embed=embed, delete_after=3.5)
                if mod_log_channel_id:
                    mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                    if mod_log_channel:
                        embed_log = discord.Embed(
                            title="Messages Purged",
                            description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] purged {int(amount)} messages in: {channel.mention}[`{channel.id}`] from: {member.mention}[`{member.id}`]",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.purple()
                        )
                        await mod_log_channel.send(embed=embed_log)
                return
            else:
                try:
                    await interaction.channel.purge(limit=amount)
                except discord.Forbidden:
                    embed_perm_error = discord.Embed(
                        title="Error! 🚫",
                        description="❯ The bot doesn't have the required permissions. (`manage_messages`)",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_perm_error, ephemeral=True)
                    return
                embed = discord.Embed(
                    title="Messages Purged",
                    description=f"❯ {int(amount)} messages were purged!",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
                await interaction.channel.send(embed=embed, delete_after=3.5)
                guild_id = str(interaction.guild.id)
                mod_log_channel_id = mod_log_settings.get(guild_id)
                if mod_log_channel_id:
                    mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                    if mod_log_channel:
                        embed_log = discord.Embed(
                            title="Messages Purged",
                            description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] purged {int(amount)} messages in: {interaction.channel.mention}",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.purple()
                        )
                        await mod_log_channel.send(embed=embed_log)
                return
        else:
            embed_error = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`manage_messages`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)
    @app_commands.command(name="snipe", description="Retrieve the most recently deleted message")
    async def snipe(self, interaction):
        if interaction.guild is None:
            return
        if interaction.user.guild_permissions.manage_messages:
            if interaction.channel.id in deleted_messages:
                deleted_message = deleted_messages[interaction.channel.id]
                author = deleted_message.author
                content = deleted_message.content

                embed = discord.Embed(
                    title="Sniped Message",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
                embed.add_field(name="Author", value=f"❯ {author.mention}", inline=False)
                embed.add_field(name="Content", value=f"❯ {content}", inline=False)
                await interaction.response.send_message(embed=embed)
            else:
                embed_error_found = discord.Embed(
                    title="Error",
                    description="❯ No deleted messages to snipe.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error_found, ephemeral = True)
        else:
            embed_error_perms = discord.Embed(
                title="Error! 🚫",
                description="You don't have permission to use this command. (`manage_messages`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_perms, ephemeral=True)
    @app_commands.command(name="role", description="Gives the user the chosen role")
    async def role(self, interaction: discord.Interaction, role_name: discord.Role, member: discord.Member = None):
        if not member:
            member = interaction.user
        if interaction.user.guild_permissions.manage_roles:
            if role_name in member.roles:
                embed_error_role_exists = discord.Embed(
                    title="Error! 🚫",
                    description=f"❯ {member.mention} already has the {role_name.mention} role.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error_role_exists, ephemeral = True)
            else:
                try:
                    await member.add_roles(role_name)
                except discord.Forbidden:
                    embed_perm_error = discord.Embed(
                        title="Error! 🚫",
                        description="❯ The bot doesn't have the required permissions. (`manage_roles`)",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_perm_error, ephemeral = True)
                    return
                embed = discord.Embed(
                    title="Role Added",
                    description=f"❯ The role {role_name.mention} has been given to {member.mention}",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
                await interaction.response.send_message(embed=embed)
        else:
            embed_error_perms = discord.Embed(
                title="Error! 🚫",
                description="You don't have permission to use this command. (`manage_roles`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed_error_perms, ephemeral=True)
    @app_commands.command(name="unrole", description="Removes the specified role from the user")
    async def unrole(self, interaction: discord.Interaction, role_name: discord.Role, member: discord.Member = None):
        if not member:
            member = interaction.user
        if interaction.user.guild_permissions.manage_roles:
            if role_name not in member.roles:
                embed_error_no_role = discord.Embed(
                    title="Error! 🚫",
                    description=f"❯ {member.mention} doesn't have the {role_name.mention} role.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error_no_role, ephemeral = True)
            else:
                try:
                    await member.add_roles(role_name)
                except discord.Forbidden:
                    embed_perm_error = discord.Embed(
                        title="Error! 🚫",
                        description="❯ The bot doesn't have the required permissions. (`manage_roles`)",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_perm_error, ephemeral = True)
                    return
                embed = discord.Embed(
                    title="Role Removed",
                    description=f"❯ The role {role_name.mention} has been removed from {member.mention}",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
                await interaction.response.send_message(embed=embed)
        else:
            embed_error_perms = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have permission to use this command. (`manage_roles`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_perms, ephemeral=True)
    @app_commands.guild_only()
    @app_commands.command(name="warn", description="warns the provided user")
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        if interaction.user.id == member.id:
            embed_error_author = discord.Embed(
                title="Error! 🚫",
                description="❯ you cannot warn yourself",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_author, ephemeral=True)
            return
        if not interaction.user.top_role > member.top_role:
            embed_error_role = discord.Embed(
                title="Error! 🚫",
                description="❯ Your role is too low.",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_role, ephemeral=True)
            return
        if interaction.user.guild_permissions.kick_members or interaction.user.guild_permissions.ban_members or interaction.user.guild_permissions.manage_roles or interaction.user.guild_permissions.manage_messages:
            warning_id = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
            async with aiomysql.connect(
                db=db,
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                charset=db_charset,
                cursorclass=aiomysql.DictCursor
            ) as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(
                        "INSERT INTO warnings (guild_id, member_id, moderator_id, reason, warning_id) VALUES (%s, %s, %s, %s, %s)",
                        (interaction.guild.id, member.id, interaction.user.id, reason, warning_id)
                    )
                    await connection.commit()
            embed = discord.Embed(
                title="Member Warned",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.purple()
            )
            embed.add_field(name="Warned", value=f"❯ {member.mention}", inline=False)
            embed.add_field(name="Warning ID", value=f"❯ {warning_id}", inline=False)
            embed.set_footer(text=f"Moderator: {interaction.user.display_name}")
            if reason:
                embed.add_field(name="Reason", value=f"❯ {reason}", inline=False)
            else:
                embed.add_field(name="Reason", value=f"❯ None", inline=False)

            await interaction.response.send_message(embed=embed)

            if not member.bot:
                embed_dm = discord.Embed(
                    title="You Got Warned",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
                embed_dm.add_field(name="Server", value=f"❯ {interaction.guild.name}", inline=False)
                embed_dm.add_field(name="Moderator", value=f"❯ {interaction.user.display_name}", inline=False)
                if reason:
                    embed_dm.add_field(name="Reason", value=f"❯ {reason}", inline=False)
                else:
                    embed_dm.add_field(name="Reason", value=f"❯ None", inline=False)

                try:
                    await member.send(embed=embed_dm)
                except discord.Forbidden:
                    embed_dm_error = discord.Embed(
                        title="Error! 🚫",
                        description="❯ Failed to send a DM to the warned user.",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.orange()
                    )
                    await interaction.channel.send(embed=embed_dm_error)

            mod_log_channel_id = mod_log_settings.get(str(interaction.guild.id))
            if mod_log_channel_id:
                mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                if mod_log_channel:
                    embed_log = discord.Embed(
                        title="Member Warned",
                        description=f"❯ {member.mention}[`{member.id}`] has been warned by {interaction.user.mention}[`{interaction.user.id}`] reason: {reason or 'None'}",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.purple()
                    )
                    await mod_log_channel.send(embed=embed_log)
        else:
            embed_error_perms = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`kick_members` or `ban_members` or `manage_roles` or `manage_messages`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_perms, ephemeral=True)
    @app_commands.command(name="warnings", description="shows the warnings in the users data base")
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        if interaction.user.guild_permissions.kick_members or interaction.user.guild_permissions.ban_members or interaction.user.guild_permissions.manage_roles or interaction.user.guild_permissions.manage_messages:
            async with aiomysql.connect(
                db=db,
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                charset=db_charset,
                cursorclass=aiomysql.DictCursor
            ) as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(
                        "SELECT moderator_id, reason, warning_id FROM warnings WHERE guild_id = %s AND member_id = %s",
                        (interaction.guild.id, member.id)
                    )
                    user_data = await cursor.fetchall()
            if not user_data:
                embed_error_no_warnings = discord.Embed(
                    title="Error! 🚫",
                    description="❯ no warnings found.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error_no_warnings, ephemeral=True)
                return
            embeds = []
            embed_limit = 5

            for i in range(0, len(user_data), embed_limit):
                embed = discord.Embed(
                    title=f"Warnings for {member.display_name} (found: {len(user_data)} warning(s))",
                    timestamp=datetime.datetime.now(datetime.timezone.utc)
                )
                if member.avatar:
                    embed.set_thumbnail(url=member.avatar.url)
                embed.set_footer(text="Page {}/{}".format((i // embed_limit) + 1, (len(user_data) - 1) // embed_limit + 1 if len(user_data) % embed_limit != 0 else len(user_data) // embed_limit))
                embed.color = discord.Color.purple()
                for idx, warning in enumerate(user_data[i:i + embed_limit], start=i + 1):
                    embed.add_field(
                        name=f"Warning {idx}",
                        value=f"❯ Moderator: <@{warning['moderator_id']}>, Reason: {warning['reason'] or 'None'}, Warning ID: {warning['warning_id']}",
                        inline=False
                    )
                embeds.append(embed)
            class ButtonView(View):
                def __init__(self, message, author, embeds, timeout=60):
                    super().__init__(timeout=timeout)
                    self.message = message
                    self.author = author
                    self.page = 0
                    self.embeds = embeds
                    previous_page_button = self.children[1]
                    double_previous_page_button = self.children[0]
                    next_page_button = self.children[2]
                    double_next_page_button = self.children[3]
                    if self.page == 0:
                        previous_page_button.disabled = True
                        double_previous_page_button.disabled = True
                    else:
                        previous_page_button.disabled = False
                        double_previous_page_button.disabled = False
                    if self.page == len(self.embeds) - 1:
                        next_page_button.disabled = True
                        double_next_page_button.disabled = True
                    else:
                        next_page_button.disabled = False
                        double_next_page_button.disabled = False
                    if self.page >= len(self.embeds) - 2:
                        double_next_page_button.disabled = True
                    if self.page <= 1:
                        double_previous_page_button.disabled = True
                async def update_buttons(self, interaction: discord.Interaction):
                    previous_page_button = self.children[1]
                    double_previous_page_button = self.children[0]
                    next_page_button = self.children[2]
                    double_next_page_button = self.children[3]
                    if self.page == 0:
                        previous_page_button.disabled = True
                        double_previous_page_button.disabled = True
                    else:
                        previous_page_button.disabled = False
                        double_previous_page_button.disabled = False
                    if self.page == len(self.embeds) - 1:
                        next_page_button.disabled = True
                        double_next_page_button.disabled = True
                    else:
                        next_page_button.disabled = False
                        double_next_page_button.disabled = False
                    if self.page >= len(self.embeds) - 2:
                        double_next_page_button.disabled = True
                    if self.page <= 1:
                        double_previous_page_button.disabled = True
                    await interaction.response.edit_message(embed=self.embeds[self.page], view=self)
                @discord.ui.button(emoji='<:discotoolsxyzicon20:1173040609980854352>', style=discord.ButtonStyle.secondary)
                async def double_previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if self.page > 1:
                        self.page -= 2
                        await self.update_buttons(interaction)
                @discord.ui.button(emoji='<:discotoolsxyzicon21:1173040950969385001>', style=discord.ButtonStyle.secondary)
                async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if self.page > 0:
                        self.page -= 1
                        await self.update_buttons(interaction)
                @discord.ui.button(emoji='<:discotoolsxyzicon18:1173038954719760424>', style=discord.ButtonStyle.secondary)
                async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if self.page < len(embeds) - 1:
                        self.page += 1
                        await self.update_buttons(interaction)
                @discord.ui.button(emoji='<:discotoolsxyzicon19:1173040213396828180>', style=discord.ButtonStyle.secondary)
                async def double_next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if self.page < len(embeds) - 1:
                        self.page += 2
                        await self.update_buttons(interaction)
                async def interaction_check(self, interaction: discord.Interaction):
                    if interaction.user.id != self.author.id:
                        embed_ownership = discord.Embed(
                            title="Error! 🚫",
                            description="You cannot interact with an other member interaction.",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.orange()
                        )
                        await interaction.response.send_message(embed=embed_ownership, ephemeral=True)
                        return False
                    return True
                async def on_timeout(self) -> None:
                    await self.message.edit_original_response(view=button_view_timeout())
            view = ButtonView(interaction, interaction.user, embeds)
            await interaction.response.send_message(embed=embeds[0], view=view)
        else:
            embed_error_perms = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`kick_members` or `ban_members` or `manage_roles` or `manage_messages`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_perms, ephemeral = True)    
    @app_commands.command(name="unwarn", description="removes a warning based on the ID provided")
    async def unwarn(self, interaction: discord.Interaction, warning_id: str):
        if interaction.user.guild_permissions.kick_members or interaction.user.guild_permissions.ban_members or interaction.user.guild_permissions.manage_roles or interaction.user.guild_permissions.manage_messages:
            async with aiomysql.connect(
                db=db,
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                charset=db_charset,
                cursorclass=aiomysql.DictCursor
            ) as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(
                        "SELECT guild_id, member_id, moderator_id FROM warnings WHERE warning_id = %s AND guild_id = %s",
                        (warning_id, interaction.guild.id)
                    )
                    removed_warning = await cursor.fetchone()
            if removed_warning:
                async with aiomysql.connect(
                    db=db,
                    host=db_host,
                    port=db_port,
                    user=db_user,
                    password=db_password,
                    charset=db_charset,
                    cursorclass=aiomysql.DictCursor
                ) as connection:
                    async with connection.cursor() as cursor:
                        await cursor.execute(
                            "DELETE FROM warnings WHERE warning_id = %s AND guild_id = %s",
                            (warning_id, interaction.guild.id)
                        )
                        await connection.commit()

                member_mention = f"<@{removed_warning['member_id']}>"
                moderator_mention = f"<@{removed_warning['moderator_id']}>"
                embed_success = discord.Embed(
                    title="Warning Removed",
                    description=f"❯ Warning with ID {warning_id} has been removed from {member_mention} by {interaction.user.mention}",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
                await interaction.response.send_message(embed=embed_success)

                mod_log_channel_id = mod_log_settings.get(str(interaction.guild.id))
                if mod_log_channel_id:
                    mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                    if mod_log_channel:
                        embed_log = discord.Embed(
                            title="Warning Removed",
                            description=f"❯ The warning with ID `{warning_id}` has been removed from {member_mention} by {interaction.user.mention}",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.purple()
                        )
                        await mod_log_channel.send(embed=embed_log)
            else:
                embed_error_not_found = discord.Embed(
                    title="Error! 🚫",
                    description=f"❯ No warning with ID {warning_id} found in the guild.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error_not_found, ephemeral=True)
        else:
            embed_error_perms = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`kick_members` or `ban_members` or `manage_roles` or `manage_messages`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_perms, ephemeral=True)
    @app_commands.command(name="clear_warnings", description="Clear all warnings for a user")
    async def clear_warnings(self, interaction: discord.Interaction, member: discord.Member):
        if interaction.user.guild_permissions.kick_members or interaction.user.guild_permissions.ban_members or interaction.user.guild_permissions.manage_roles or interaction.user.guild_permissions.manage_messages:
            async with aiomysql.connect(
                db=db,
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                charset=db_charset,
                cursorclass=aiomysql.DictCursor
            ) as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(
                        "SELECT * FROM warnings WHERE guild_id = %s AND member_id = %s",
                        (interaction.guild.id, member.id)
                    )
                    warnings = await cursor.fetchall()
                if warnings:
                    async with aiomysql.connect(
                        db=db,
                        host=db_host,
                        port=db_port,
                        user=db_user,
                        password=db_password,
                        charset=db_charset,
                        cursorclass=aiomysql.DictCursor
                    ) as connection:
                        async with connection.cursor() as cursor:
                            await cursor.execute(
                                "DELETE FROM warnings WHERE guild_id = %s AND member_id = %s",
                                (interaction.guild.id, member.id)
                            )
                            await connection.commit()
                    embed_success = discord.Embed(
                        title="Warnings Cleared",
                        description=f"❯ Warnings for {member.mention} have been cleared.",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.purple()
                    )
                    await interaction.response.send_message(embed=embed_success)

                    mod_log_channel_id = mod_log_settings.get(str(interaction.guild.id))
                    if mod_log_channel_id:
                        mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                        if mod_log_channel:
                            embed_log = discord.Embed(
                                title="Warnings Cleared",
                                description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] has cleared the warnings for {member.mention}[`{member.id}`]",
                                timestamp=datetime.datetime.now(datetime.timezone.utc),
                                color=discord.Color.purple()
                            )
                            await mod_log_channel.send(embed=embed_log)
                else:
                    embed_error_not_found = discord.Embed(
                        title="Error! 🚫",
                        description=f"❯ No warnings found for {member.mention} in your guild.",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_error_not_found, ephemeral=True)
        else:
            embed_error_perms = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`kick_members` or `ban_members` or `manage_roles` or `manage_messages`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_perms, ephemeral=True)     
    @app_commands.command(name="mute", description="mutes the chosen member")
    async def mute(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = None):
        if interaction.user.id is member.id:
            embed_error_author = discord.Embed(
                title="Error! 🚫",
                description="❯ you cannot mute your self",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_author, ephemeral=True)
            return
        if not interaction.user.top_role > member.top_role:
            embed_error_role = discord.Embed(
                title="Error! 🚫",
                description="❯ Your role is too low.",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_role, ephemeral=True)
            return
        if interaction.user.guild_permissions.manage_roles:
            mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
            if mute_role is None:
                try:
                    mute_role = await interaction.guild.create_role(name="Muted")
                    for channel in interaction.guild.channels:
                        await channel.set_permissions(mute_role, send_messages=False)
                except discord.Forbidden:
                    embed_perm_error = discord.Embed(
                        title="Error! 🚫",
                        description="❯ The bot doesn't have the required permissions.",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_perm_error, ephemeral = True)
                    return
            if mute_role in member.roles:
                embed_already_muted = discord.Embed(
                    title="Error! 🚫",
                    description=f"❯ {member.mention} is already muted.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_already_muted, ephemeral = True)
                return
            duration = parse_duration(duration)
            if duration <= 0:
                embed_time_error = discord.Embed(
                    title="Error! 🚫",
                    description="❯ Invalid duration format. Use 'd' for days or 'h' for hours or '1m' for minutes or '1s' for seconds.",
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_time_error, ephemeral = True)
                return
            try:
                await member.add_roles(mute_role, reason=reason)
            except discord.Forbidden:
                embed_perm_error = discord.Embed(
                    title="Error! 🚫",
                    description="❯ The bot doesn't have the required permissions. (`manage_roles`)",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_perm_error, ephemeral = True)
                return
            unmute_time = datetime.datetime.now() + datetime.timedelta(seconds=duration)
            muted_users[member.id] = unmute_time
            embed = discord.Embed(
                title=f"member muted",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.purple()
            )
            embed.add_field(name="muted", value=f"❯ {member.mention}", inline=False)
            embed.add_field(name="Duration", value=f"❯ {humanize.naturaldelta(datetime.timedelta(seconds=duration))}")
            embed.set_footer(text=f"Moderator: {interaction.user.display_name}")
            if reason:
                embed.add_field(name="reason", value=f"❯ {reason}", inline=False)
            if not reason:
                embed.add_field(name="reason", value=f"❯ None", inline=False)
            await interaction.response.send_message(embed=embed)
            if not member.bot:
                embed_dm = discord.Embed(
                    title="you got muted",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
                embed_dm.add_field(name="server", value=f"❯ {interaction.guild.name}", inline=False)
                embed_dm.add_field(name="Moderator", value=f"❯ {interaction.user.display_name}", inline=False)
                if reason:
                    embed_dm.add_field(name="Reason", value=f"❯ {reason}", inline=False)
                if not reason:
                    embed_dm.add_field(name="reason", value=f"❯ None", inline=False)
                embed_dm.add_field(name="duration", value=f"❯ {humanize.naturaldelta(datetime.timedelta(seconds=duration))}")
                try:
                    await member.send(embed=embed_dm)
                except discord.Forbidden:
                    embed_dm_error = discord.Embed(
                        title="Error! 🚫",
                        description="❯ Failed to send a DM to the muted user.",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.orange()
                    )
                    await interaction.channel.send(embed_dm_error)
            guild_id = str(interaction.guild.id)
            mod_log_channel_id = mod_log_settings.get(guild_id)
            if mod_log_channel_id:
                mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                if mod_log_channel:
                    embed_log = discord.Embed(
                        title="member muted",
                        description=f"❯ {member.mention}[`{member.id}`] has been muted by {interaction.user.mention}[`{interaction.user.id}`] reason: `{reason or 'None'}` duration: {humanize.naturaldelta(datetime.timedelta(seconds=duration))}",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.purple()
                    )
                    await mod_log_channel.send(embed=embed_log)
            await asyncio.sleep(duration)
            unmute_time = muted_users.get(member.id)
            if unmute_time and datetime.datetime.now() >= unmute_time:
                await member.remove_roles(mute_role)
                del muted_users[member.id]
                unmute_embed = discord.Embed(
                    title="member automatically unmuted",
                    description=f"❯ {member.mention} has been automatically unmuted.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
                await interaction.channel.send(embed=unmute_embed)
            guild_id = str(interaction.guild.id)
            mod_log_channel_id = mod_log_settings.get(guild_id)
            if mod_log_channel_id:
                mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                if mod_log_channel:
                    if unmute_time and datetime.datetime.now() >= unmute_time:
                        embed_log = discord.Embed(
                            title="member automatically unmuted",
                            description=f"❯ {member.mention}[`{member.id}`] has been automatically unmuted.",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.purple()
                        )
                        await mod_log_channel.send(embed=embed_log)
        else:
            embed_error = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have permission to use this command. (`manage_roles`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral = True) 
    @app_commands.command(name="unmute", description="unmutes the chosen member")
    async def unmute(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        if interaction.user.guild_permissions.manage_roles:
            mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
            if mute_role:
                if mute_role in member.roles:
                    try:
                        await member.remove_roles(mute_role, reason=reason)
                    except discord.Forbidden:
                        embed_perm_error = discord.Embed(
                            title="Error! 🚫",
                            description="❯ The bot doesn't have the required permissions. (`manage_roles`)",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.orange()
                        )
                        await interaction.response.send_message(embed=embed_perm_error, ephemeral = True)
                        return
                    if member.id in muted_users:
                        del muted_users[member.id]
                    embed = discord.Embed(
                        title=f"member unmuted",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.purple()
                    )
                    embed.add_field(name="unmuted", value=f"❯ {member.mention}", inline=False)
                    embed.set_footer(text="Moderator", value=f"❯ {interaction.user.display_name}")
                    if reason:
                        embed.add_field(name="reason", value=f"❯ {reason}", inline=False)
                    if not reason:
                        embed.add_field(name="reason", value=f"❯ None", inline=False)
                    await interaction.response.send_message(embed=embed)
                    guild_id = str(interaction.guild.id)
                    mod_log_channel_id = mod_log_settings.get(guild_id)
                    if mod_log_channel_id:
                        mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                        if mod_log_channel:
                            embed_log = discord.Embed(
                                title="member unmuted",
                                description=f"❯ {member.mention}[`{member.id}`] has been unmuted by {interaction.user.mention}[`{interaction.user.id}`] reason: `{reason or 'None'}`",
                                timestamp=datetime.datetime.now(datetime.timezone.utc),
                                color=discord.Color.purple()
                            )
                            await mod_log_channel.send(embed=embed_log)
                else:
                    embed_error = discord.Embed(
                        title="Error! 🚫",
                        description=f"❯ {member.mention} is not muted.",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_error, ephemeral = True)
                    return
            else:
                embed_error = discord.Embed(
                    title="Error! 🚫",
                    description="❯ The 'Muted' role does not exist.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error, ephemeral = True)
                return
        else:
            embed_error = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have permission to use this command. (`manage_roles`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral = True)
    @app_commands.command(name="mute-list", description="Lists muted members")
    async def mute_list(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.manage_roles:
            muted_members = [member for member_id in muted_users.keys() if (member := interaction.guild.get_member(member_id)) is not None]
            if muted_members:
                muted_list = "\n".join(["❯ " + member.mention for member in muted_members])
                embeds = []
                embed_limit = 10
                muted_list_lines = muted_list.split('\n')
                for i in range(0, len(muted_list_lines), embed_limit):
                    embed = discord.Embed(
                        title=f"Muted Members (found: {len(muted_members)} member(s))",
                        description="\n".join(muted_list_lines[i:i + embed_limit]),
                        timestamp=discord.utils.utcnow(),
                        color=discord.Color.purple()
                    )
                    embed.set_footer(text="Page {}/{}".format((i // embed_limit) + 1, (len(muted_list_lines) - 1) // embed_limit + 1 if len(muted_list_lines) % embed_limit != 0 else len(muted_list_lines) // embed_limit))
                    embeds.append(embed)
                class ButtonView(View):
                    def __init__(self, message, author, embeds, timeout=60):
                        super().__init__(timeout=timeout)
                        self.message = message
                        self.author = author
                        self.page = 0
                        self.embeds = embeds
                        previous_page_button = self.children[1]
                        double_previous_page_button = self.children[0]
                        next_page_button = self.children[2]
                        double_next_page_button = self.children[3]
                        if self.page == 0:
                            previous_page_button.disabled = True
                            double_previous_page_button.disabled = True
                        else:
                            previous_page_button.disabled = False
                            double_previous_page_button.disabled = False
                        if self.page == len(self.embeds) - 1:
                            next_page_button.disabled = True
                            double_next_page_button.disabled = True
                        else:
                            next_page_button.disabled = False
                            double_next_page_button.disabled = False
                        if self.page >= len(self.embeds) - 2:
                            double_next_page_button.disabled = True
                        if self.page <= 1:
                            double_previous_page_button.disabled = True
                    async def update_buttons(self, interaction: discord.Interaction):
                        previous_page_button = self.children[1]
                        double_previous_page_button = self.children[0]
                        next_page_button = self.children[2]
                        double_next_page_button = self.children[3]
                        if self.page == 0:
                            previous_page_button.disabled = True
                            double_previous_page_button.disabled = True
                        else:
                            previous_page_button.disabled = False
                            double_previous_page_button.disabled = False
                        if self.page == len(self.embeds) - 1:
                            next_page_button.disabled = True
                            double_next_page_button.disabled = True
                        else:
                            next_page_button.disabled = False
                            double_next_page_button.disabled = False
                        if self.page >= len(self.embeds) - 2:
                            double_next_page_button.disabled = True
                        if self.page <= 1:
                            double_previous_page_button.disabled = True
                        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)
                    @discord.ui.button(emoji='<:discotoolsxyzicon20:1173040609980854352>', style=discord.ButtonStyle.secondary)
                    async def double_previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                        if self.page > 1:
                            self.page -= 2
                            await self.update_buttons(interaction)
                    @discord.ui.button(emoji='<:discotoolsxyzicon21:1173040950969385001>', style=discord.ButtonStyle.secondary)
                    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                        if self.page > 0:
                            self.page -= 1
                            await self.update_buttons(interaction)
                    @discord.ui.button(emoji='<:discotoolsxyzicon18:1173038954719760424>', style=discord.ButtonStyle.secondary)
                    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                        if self.page < len(embeds) - 1:
                            self.page += 1
                            await self.update_buttons(interaction)
                    @discord.ui.button(emoji='<:discotoolsxyzicon19:1173040213396828180>', style=discord.ButtonStyle.secondary)
                    async def double_next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                        if self.page < len(embeds) - 1:
                            self.page += 2
                            await self.update_buttons(interaction)
                    async def interaction_check(self, interaction: discord.Interaction):
                        if interaction.user.id != self.author.id:
                            embed_ownership = discord.Embed(
                                title="Error! 🚫",
                                description="You cannot interact with an other member interaction.",
                                timestamp=datetime.datetime.now(datetime.timezone.utc),
                                color=discord.Color.orange()
                            )
                            await interaction.response.send_message(embed=embed_ownership, ephemeral=True)
                            return False
                        return True
                    async def on_timeout(self) -> None:
                        await self.message.edit_original_response(view=button_view_timeout())
                view = ButtonView(interaction, interaction.user, embeds)
                await interaction.response.send_message(embed=embeds[0], view=view)
            else:
                embed = discord.Embed(
                    title="Error! 🚫",
                    description="No muted members found.",
                    timestamp=discord.utils.utcnow(),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed_error = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have permission to use this command. (`manage_roles`)",
                timestamp=discord.utils.utcnow(),
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)
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
    @app_commands.command(name="kick", description="kicks the chosen member")
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        if interaction.user.id is member.id:
            embed_error_author = discord.Embed(
                title="Error! 🚫",
                description="❯ you cannot kick your self",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_author, ephemeral=True)
            return
        if not interaction.guild.me.guild_permissions.ban_members:
            embed_perm_error = discord.Embed(
                title="Error! 🚫",
                description="❯ The bot doesn't have the required permissions. (`kick_members`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_perm_error, ephemeral = True)
            return
        if not interaction.guild.me.top_role > member.top_role:
            embed_error_role = discord.Embed(
                title="Error! 🚫",
                description="❯ The bot role is too low.",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_role, ephemeral=True)
            return
        if not interaction.user.top_role > member.top_role:
            embed_error_role = discord.Embed(
                title="Error! 🚫",
                description="❯ Your role is too low.",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_role, ephemeral=True)
            return
        if interaction.user.guild_permissions.kick_members:
            if not member.bot:
                embed_dm = discord.Embed(
                    title="you got kicked",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
                embed_dm.add_field(name="server", value=f"❯ {interaction.guild.name}", inline=False)
                embed_dm.add_field(name="Moderator", value=f"❯ {interaction.user.display_name}", inline=False)
                if reason:
                    embed_dm.add_field(name="reason", value=f"❯ {reason}", inline=False)
                if not reason:
                    embed_dm.add_field(name="reason", value=f"❯ None", inline=False)
                try:
                    await member.send(embed=embed_dm)
                except discord.Forbidden:
                    embed_dm_error = discord.Embed(
                        title="Error! 🚫",
                        description="Failed to send a DM to the kicked user.",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.orange()
                    )
                    await interaction.channel.send(embed=embed_dm_error)
            try:
                if reason:
                    await member.kick(reason=reason)
                else:
                    await member.kick(reason="no reason provided.")
            except discord.NotFound:
                embed_error_not_found = discord.Embed(
                    title="Error! 🚫",
                    description="❯ member not found.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
                await interaction.response.send_message(embed=embed_error_not_found, ephemeral=True)
            embed = discord.Embed(
                title="member kicked",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.purple()
            )
            embed.add_field(name="kicked", value=f"❯ {member.mention}", inline=False)
            embed.set_footer(text=f"Moderator: {interaction.user.display_name}") 
            if reason:
                embed.add_field(name="reason", value=f"❯ {reason}", inline=False)
            if not reason:
                embed.add_field(name="reason", value=f"❯ None", inline=False)   
            await interaction.response.send_message(embed=embed)
            guild_id = str(interaction.guild.id)
            mod_log_channel_id = mod_log_settings.get(guild_id)
            if mod_log_channel_id:
                mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                if mod_log_channel:
                    embed_log = discord.Embed(
                        title="member kicked",
                        description=f"❯ {member.mention}[`{member.id}`] has been kicked by {interaction.user.mention}[`{interaction.user.id}`] reason: `{reason or 'None'}`",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.purple()
                    )
                    await mod_log_channel.send(embed=embed_log)
        else:
            embed_error = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have permission to use this command. (`kick_members`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral = True)            
    @app_commands.command(name="ban", description="bans the chosen member")
    async def ban(self, interaction: discord.Interaction, member: Union[discord.Member, discord.User], reason: str = None):
        if isinstance(member, discord.Member):
            if interaction.user.id is member.id:
                embed_error_author = discord.Embed(
                    title="Error! 🚫",
                    description="❯ you cannot ban your self",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error_author, ephemeral = True)
                return
            if not interaction.guild.me.guild_permissions.ban_members:
                embed_perm_error = discord.Embed(
                    title="Error! 🚫",
                    description="❯ The bot doesn't have the required permissions. (`ban_members`)",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_perm_error, ephemeral = True)
                return
            if not interaction.guild.me.top_role > member.top_role:
                embed_error_role = discord.Embed(
                    title="Error! 🚫",
                    description="❯ The bot role is too low.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error_role, ephemeral=True)
                return
            if not interaction.user.top_role > member.top_role:
                embed_error_role = discord.Embed(
                    title="Error! 🚫",
                    description="❯ Your role is too low.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error_role, ephemeral=True)
                return
            if interaction.user.guild_permissions.ban_members:
                if not member.bot:
                    embed_dm = discord.Embed(
                        title="you got banned",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.purple()
                    )
                    embed_dm.add_field(name="server", value=f"❯ {interaction.guild.name}", inline=False)
                    embed_dm.add_field(name="Moderator", value=f"❯ {interaction.user.display_name}", inline=False)
                    if reason:
                        embed_dm.add_field(name="reason", value=f"❯ {reason}", inline=False)
                    if not reason:
                        embed_dm.add_field(name="reason", value=f"❯ None", inline=False)
                    try:
                        await member.send(embed=embed_dm)
                    except discord.Forbidden:
                        embed_dm_error = discord.Embed(
                            title="Error! 🚫",
                            description="❯ Failed to send a DM to the banned user.",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.orange()
                        )
                        await interaction.channel.send(embed=embed_dm_error)
                try:
                    if reason:
                        await member.ban(reason=reason)
                    else:
                        await member.ban(reason="no reason provided.")
                except discord.NotFound:
                    embed_error_not_found = discord.Embed(
                        title="Error! 🚫",
                        description="❯ member not found.",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.purple()
                    )
                    await interaction.response.send_message(embed=embed_error_not_found, ephemeral=True)
                embed = discord.Embed(
                    title="Member banned",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
                embed.add_field(name="banned", value=f"❯ {member.mention}", inline=False)
                embed.set_footer(text=f"Moderator: {interaction.user.display_name}")
                if reason:
                    embed.add_field(name="reason", value=f"❯ {reason}", inline=False)
                if not reason:
                    embed.add_field(name="reason", value=f"❯ None", inline=False)
                await interaction.response.send_message(embed=embed)
                guild_id = str(interaction.guild.id)
                mod_log_channel_id = mod_log_settings.get(guild_id)
                if mod_log_channel_id:
                    mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                    if mod_log_channel:
                        embed_log = discord.Embed(
                            title="member banned",
                            description=f"❯ {member.mention}[`{member.id}`] has been banned by {interaction.user.mention}[`{interaction.user.id}`] reason: `{reason or 'None'}`",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.purple()
                        )
                        await mod_log_channel.send(embed=embed_log)
            else:
                embed_error = discord.Embed(
                    title="Error! 🚫",
                    description="❯ You don't have permission to use this command. (`ban_members`)",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error, ephemeral = True)
        if isinstance(member, discord.User):
            if interaction.user.id is member.id:
                embed_error_author = discord.Embed(
                    title="Error! 🚫",
                    description="❯ you cannot ban your self",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error_author, ephemeral = True)
                return
            if not interaction.guild.me.guild_permissions.ban_members:
                embed_perm_error = discord.Embed(
                    title="Error! 🚫",
                    description="❯ The bot doesn't have the required permissions. (`ban_members`)",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_perm_error, ephemeral = True)
                return
            if interaction.user.guild_permissions.ban_members:
                try:
                    if reason:
                        await interaction.guild.ban(member)
                    else:
                        await interaction.guild.ban(member, reason="no reason provided.")
                except discord.NotFound:
                    embed_error_not_found = discord.Embed(
                        title="Error! 🚫",
                        description="❯ member not found.",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.purple()
                    )
                    await interaction.response.send_message(embed=embed_error_not_found, ephemeral=True)
                embed = discord.Embed(
                    title="Member banned",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
                embed.add_field(name="banned", value=f"❯ {member.name}", inline=False)
                embed.set_footer(text=f"Moderator: {interaction.user.display_name}")
                if reason:
                    embed.add_field(name="reason", value=f"❯ {reason}", inline=False)
                if not reason:
                    embed.add_field(name="reason", value=f"❯ None", inline=False)
                await interaction.response.send_message(embed=embed)
                guild_id = str(interaction.guild.id)
                mod_log_channel_id = mod_log_settings.get(guild_id)
                if mod_log_channel_id:
                    mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                    if mod_log_channel:
                        embed_log = discord.Embed(
                            title="member banned",
                            description=f"❯ {member.name}[`{member.id}`] has been banned by {interaction.user.mention}[`{interaction.user.id}`] reason: `{reason or 'None'}`",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.purple()
                        )
                        await mod_log_channel.send(embed=embed_log)
            else:
                embed_error = discord.Embed(
                    title="Error! 🚫",
                    description="❯ You don't have permission to use this command. (`ban_members`)",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error, ephemeral = True)
    @app_commands.command(name='unban', description="unbans the chosen user")
    async def unban(self, interaction: discord.Interaction, member_id: str, reason: str = None):
        if interaction.user.guild_permissions.ban_members:
            try:
                user = await self.client.fetch_user(member_id)
            except discord.NotFound:
                embed_error_not_found = discord.Embed(
                    title="Error! 🚫",
                    description="❯ member not found.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error_not_found, ephemeral=True)       
            try:
                if reason:
                    await interaction.guild.unban(user, reason=reason)
                else:
                    await interaction.guild.unban(user, reason="no reason provided.")
            except discord.Forbidden:
                embed_perm_error = discord.Embed(
                    title="Error! 🚫",
                    description="❯ The bot doesn't have the required permissions. (`ban_members`)",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_perm_error, ephemeral = True)
                return
            except discord.NotFound:
                embed_error_exis = discord.Embed(
                    title="Error! 🚫",
                    description="❯ the chosen member is not banned.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error_exis, ephemeral=True)
                return
            embed = discord.Embed(
                title="member unbanned",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.purple()
            )
            embed.add_field(name="unbanned", value=f"❯ {user.display_name}")
            embed.set_footer(text=f"Moderator: {interaction.user.display_name}")
            if reason:
                embed.add_field(name="reason", value=f"❯ {reason}", inline=False)
            if not reason:
                embed.add_field(name="reason", value=f"❯ None", inline=False)
            await interaction.response.send_message(embed=embed)
            guild_id = str(interaction.guild.id)
            mod_log_channel_id = mod_log_settings.get(guild_id)
            if mod_log_channel_id:
                mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                if mod_log_channel:
                    embed_log = discord.Embed(
                        title="member unbanned",
                        description=f"❯ Member with the id `{member_id}` has been unbanned by {interaction.user.mention}[`{interaction.user.id}`] reason: `{reason or 'None'}`",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.purple()
                    )
                    await mod_log_channel.send(embed=embed_log)
        else:
            embed_error = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have permission to use this command. (`ban_members`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral = True)
class setting_group_moderation(commands.GroupCog, group_name='setting', group_description='`setting` commands group'):
    def __init__(self, client):
        super().__init__()
        self.client = client
    @app_commands.command(name="chat_filter", description="Enable or disable the chat-filter function")
    async def chat_filter(self, interaction: discord.Interaction, state:Literal["on", "off"]):
        if not interaction.user.guild_permissions.manage_messages:
            embed_error_perms = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`manage_messages`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_perms, ephemeral = True)
            return
        if not interaction.guild.me.guild_permissions.manage_messages:
            embed_perm_error = discord.Embed(
                title="Error! 🚫",
                description="❯ The bot doesn't have the required permissions. (`manage_messages`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_perm_error, ephemeral = True)
            return
        guild_id = str(interaction.guild.id)
        if state == 'on':
            if chat_filter_settings.get(guild_id, False):
                embed = discord.Embed(
                    title="Error! 🚫",
                    description="the chat-filter seems to be already `enabled`",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed, ephemeral = True)
            else:
                chat_filter_settings[guild_id] = True
                save_chat_filter_settings()
                embed = discord.Embed(
                    title="Server Protection Protocol",
                    description="Chat-filter is now `enabled` for this server.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
                await interaction.response.send_message(embed=embed)
                audit_log_channel_id = audit_log_settings.get(guild_id)
                if audit_log_channel_id:
                    audit_log_channel = interaction.guild.get_channel(audit_log_channel_id)
                    if audit_log_channel:
                        embed_log = discord.Embed(
                            title="log",
                            description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] has enabled the chat-filter setting",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.purple()
                        )
                        await audit_log_channel.send(embed=embed_log)
        elif state == 'off':
            if chat_filter_settings.get(guild_id, False):
                chat_filter_settings[guild_id] = False
                save_chat_filter_settings()
                embed = discord.Embed(
                    title="Server Protection Protocol",
                    description="Chat-filter is now `disabled` for this server.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
                await interaction.response.send_message(embed=embed)
                audit_log_channel_id = audit_log_settings.get(guild_id)
                if audit_log_channel_id:
                    audit_log_channel = interaction.guild.get_channel(audit_log_channel_id)
                    if audit_log_channel:
                        embed_log = discord.Embed(
                            title="log",
                            description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] has disabled the chat-filter setting",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.purple()
                        )
                        await audit_log_channel.send(embed=embed_log)
            else:
                embed = discord.Embed(
                    title="Error! 🚫",
                    description="❯ the chat-filter seems to be already `disabled`",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed, ephemeral = True)
    @app_commands.command(name="anti_spam", description="Toggle the anti-spam feature")
    async def anti_spam(self, interaction: discord.Interaction, state: Literal["on", "off"]):
        if not interaction.user.guild_permissions.manage_messages:
            embed_error_perms = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`manage_messages`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_perms, ephemeral=True)
            return
        if not interaction.guild.me.guild_permissions.manage_messages:
            embed_perm_error = discord.Embed(
                title="Error! 🚫",
                description="❯ The bot doesn't have the required permissions. (`manage_messages`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_perm_error, ephemeral = True)
            return
        guild_id = str(interaction.guild.id)
        if state == "on":
            if anti_spam_settings.get(guild_id, False):
                embed = discord.Embed(
                    title="Error! 🚫",
                    description="❯ The anti-spam feature seems to be already `enabled`",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                anti_spam_settings[guild_id] = True
                save_anti_spam_settings()
                embed = discord.Embed(
                    title="Anti-Spam Feature",
                    description="❯ The anti-spam feature is now `enabled` for this server.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
                await interaction.response.send_message(embed=embed)
                audit_log_channel_id = audit_log_settings.get(guild_id)
                if audit_log_channel_id:
                    audit_log_channel = interaction.guild.get_channel(audit_log_channel_id)
                    if audit_log_channel:
                        embed_log = discord.Embed(
                            title="log",
                            description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] has enabled the anti-spam setting",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.purple()
                        )
                        await audit_log_channel.send(embed=embed_log)
        elif state == "off":
            if anti_spam_settings.get(guild_id, False):
                anti_spam_settings[guild_id] = False
                save_anti_spam_settings()
                embed = discord.Embed(
                    title="Anti-Spam Feature",
                    description="❯ The anti-spam feature is now `disabled` for this server.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
                await interaction.response.send_message(embed=embed)
                audit_log_channel_id = audit_log_settings.get(guild_id)
                if audit_log_channel_id:
                    audit_log_channel = interaction.guild.get_channel(audit_log_channel_id)
                    if audit_log_channel:
                        embed_log = discord.Embed(
                            title="log",
                            description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] has disabled the anti-spam setting",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.purple()
                        )
                        await audit_log_channel.send(embed=embed_log)
            else:
                embed = discord.Embed(
                    title="Error! 🚫",
                    description="❯ The anti-spam feature seems to be already `disabled`",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
    @app_commands.command(name="anti_link", description="Enable or disable the anti-link function")
    async def anti_link(self, interaction: discord.Interaction, state:Literal["on", "off"]):
        if not interaction.user.guild_permissions.manage_messages:
            embed_error_perms = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`manage_messages`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_perms, ephemeral = True)
            return
        if not interaction.guild.me.guild_permissions.manage_messages:
            embed_perm_error = discord.Embed(
                title="Error! 🚫",
                description="❯ The bot doesn't have the required permissions. (`manage_messages`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_perm_error, ephemeral = True)
            return
        guild_id = str(interaction.guild.id)
        if state.lower() == "on":
            if anti_link_settings.get(guild_id, False):
                embed = discord.Embed(
                    title="Error! 🚫",
                    description="❯ the anti-link seems to be already `enabled`",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed, ephemeral = True)
            else:
                anti_link_settings[guild_id] = True
                save_anti_link_settings()
                embed = discord.Embed(
                    title="Server Protection Protocol",
                    description="❯ Anti-link is now `enabled` for this server.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
                await interaction.response.send_message(embed=embed)
                audit_log_channel_id = audit_log_settings.get(guild_id)
                if audit_log_channel_id:
                    audit_log_channel = interaction.guild.get_channel(audit_log_channel_id)
                    if audit_log_channel:
                        embed_log = discord.Embed(
                            title="log",
                            description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] has enabled the anti-link setting",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.purple()
                        )
                        await audit_log_channel.send(embed=embed_log)
        elif state.lower() == "off":
            if anti_link_settings.get(guild_id, False):
                anti_link_settings[guild_id] = False
                save_anti_link_settings() 
                embed = discord.Embed(
                    title="Server Protection Protocol",
                    description="❯ Anti-link is now `disabled` for this server.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
                await interaction.response.send_message(embed=embed)
                audit_log_channel_id = audit_log_settings.get(guild_id)
                if audit_log_channel_id:
                    audit_log_channel = interaction.guild.get_channel(audit_log_channel_id)
                    if audit_log_channel:
                        embed_log = discord.Embed(
                            title="log",
                            description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] has disabled the anti-link setting",
                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                            color=discord.Color.purple()
                        )
                        await audit_log_channel.send(embed=embed_log)
            else:
                embed = discord.Embed(
                    title="Error! 🚫",
                    description="❯ the anti-link seems to be already `disabled`",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed, ephemeral = True)
    @app_commands.command(name="audit_log_channel", description="Set the audit log channel")
    async def setting_audit_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.view_audit_log:
            embed_error_perms = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`view_audit_log`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_perms, ephemeral=True)
            return
        if not interaction.guild.me.guild_permissions.view_audit_log:
            embed_perm_error = discord.Embed(
                title="Error! 🚫",
                description="❯ The bot doesn't have the required permissions. (`view_audit_log`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_perm_error, ephemeral = True)
            return
        guild_id = str(interaction.guild.id)
        if guild_id in audit_log_settings:
            if audit_log_settings[guild_id] == channel.id:
                embed_error_set = discord.Embed(
                    title="Error! 🚫",
                    description="❯ The chosen channel is already set as the audit log channel.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error_set, ephemeral=True)
                return
        guild_id = str(interaction.guild.id)
        audit_log_settings[guild_id] = channel.id
        save_audit_log_settings()
        embed = discord.Embed(
            title="Audit Log Channel Set",
            description=f"❯ audit log channel has been set to {channel.mention}.",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed)
        mod_log_channel_id = mod_log_settings.get(guild_id)
        if mod_log_channel_id:
            mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
            if mod_log_channel:
                embed_log = discord.Embed(
                    title="audit setting",
                    description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] has set the audit log channel to {channel.mention}",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
            await mod_log_channel.send(embed=embed_log)
    remove_group = Group(name="remove", description="`remove` commands subgroup (parent group: `setting`)")
    @remove_group.command(name="audit_log_channel", description="Remove the audit log channel setting")
    async def remove_audit_log_channel(self, interaction):
        if not interaction.user.guild_permissions.view_audit_log:
            embed_error_perms = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`view_audit_log`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_perms, ephemeral=True)
            return
        guild_id = str(interaction.guild.id)
        mod_log_channel_id = mod_log_settings.get(guild_id)
        if mod_log_channel_id:
            mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
            if mod_log_channel:
                embed_log = discord.Embed(
                    title="audit log removed",
                    description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] has removed the audit log channel setting",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
                await mod_log_channel.send(embed=embed_log)
            del audit_log_settings[guild_id]
            save_audit_log_settings()
            embed = discord.Embed(
                title="Audit Log Channel Removed",
                description="❯ The audit log channel setting has been removed for this server.",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.purple()
            )
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Error! 🚫",
                description="❯ There was no audit log channel setting to remove.",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    @app_commands.command(name="mod_log_channel", description="Set the moderation log channel")
    async def setting_mod_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.view_audit_log:
            embed_error_perms = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`view_audit_log`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_perms, ephemeral=True)
            return
        if not interaction.guild.me.guild_permissions.view_audit_log:
            embed_perm_error = discord.Embed(
                title="Error! 🚫",
                description="❯ The bot doesn't have the required permissions. (`view_audit_log`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_perm_error, ephemeral = True)
            return
        guild_id = str(interaction.guild.id)
        if guild_id in mod_log_settings:
            if mod_log_settings[guild_id] == channel.id:
                embed_error_set = discord.Embed(
                    title="Error! 🚫",
                    description="❯ The chosen channel is already set as the moderation log channel.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error_set, ephemeral=True)
                return
        guild_id = str(interaction.guild.id)
        mod_log_settings[guild_id] = channel.id
        save_mod_log_settings()
        embed = discord.Embed(
            title="moderation Log Channel Set",
            description=f"❯ moderation log channel has been set to {channel.mention}.",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed)
        mod_log_channel_id = mod_log_settings.get(guild_id)
        if mod_log_channel_id:
            mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
            if mod_log_channel:
                embed_log = discord.Embed(
                    title="moderation Log Channel Set",
                    description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] has set the moderation log channel to {channel.mention}",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
            await mod_log_channel.send(embed=embed_log)
    @remove_group.command(name="mod_log_channel", description="Remove the moderation log channel setting")
    async def remove_mod_log_channel(self, interaction):
        if not interaction.user.guild_permissions.manage_messages:
            embed_error_perms = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`manage_messages`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_perms, ephemeral=True)
            return
        guild_id = str(interaction.guild.id)
        if guild_id in mod_log_settings:
            mod_log_channel_id = mod_log_settings.get(guild_id)
            if mod_log_channel_id:
                mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                if mod_log_channel:
                    embed_log = discord.Embed(
                        title="moderation log removed",
                        description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] has removed the moderation log channel setting",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.purple()
                    )
                await mod_log_channel.send(embed=embed_log)
            del mod_log_settings[guild_id]
            save_mod_log_settings()
            embed = discord.Embed(
                title="moderation Log Channel Removed",
                description="❯ The moderation log channel setting has been removed for this server.",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.purple()
            )
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Error! 🚫",
                description="❯ There was no moderation log channel setting to remove.",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    @app_commands.command(name="welcomer", description="Set the welcomer channel")
    async def setting_welcomer(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.manage_messages:
            embed_error_perms = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`manage_messages`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_perms, ephemeral=True)
            return
        guild_id = str(interaction.guild.id)
        if guild_id in welcomer_settings:
            if welcomer_settings[guild_id] == channel.id:
                embed_error_set = discord.Embed(
                    title="Error! 🚫",
                    description="❯ The chosen channel is already set as the welcomer channel.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error_set, ephemeral=True)
                return
        guild_id = str(interaction.guild.id)
        welcomer_settings[guild_id] = channel.id
        save_welcomer_settings()
        embed = discord.Embed(
            title="welcomer Channel Set",
            description=f"❯ Welcomer channel has been set to {channel.mention}.",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed)
        mod_log_channel_id = mod_log_settings.get(guild_id)
        if mod_log_channel_id:
            mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
            if mod_log_channel:
                embed_log = discord.Embed(
                    title="welcomer Channel Set",
                    description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] has set the welcomer channel to {channel.mention}",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
            await mod_log_channel.send(embed=embed_log)
    @remove_group.command(name="welcomer", description="Remove the welcomer channel setting")
    async def remove_welcomer(self, interaction):
        if not interaction.user.guild_permissions.manage_messages:
            embed_error_perms = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`manage_messages`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_perms, ephemeral=True)
            return

        guild_id = str(interaction.guild.id)
        if guild_id in welcomer_settings:
            del welcomer_settings[guild_id]
            save_welcomer_settings()
            embed = discord.Embed(
                title="welcomer Channel Removed",
                description="❯ The welcomer channel setting has been removed for this server.",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.purple()
            )
            await interaction.response.send_message(embed=embed)
            mod_log_channel_id = mod_log_settings.get(guild_id)
            if mod_log_channel_id:
                mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                if mod_log_channel:
                    embed_log = discord.Embed(
                        title="welcomer Channel Removed",
                        description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] has removed the welcomer channel setting",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.purple()
                    )
                await mod_log_channel.send(embed=embed_log)
        else:
            embed = discord.Embed(
                title="Error! 🚫",
                description="❯ There was no welcomer channel setting to remove.",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    @app_commands.command(name="farweller", description="Set the farweller channel")
    async def setting_farweller(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.manage_messages:
            embed_error_perms = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`manage_messages`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_perms, ephemeral=True)
            return
        guild_id = str(interaction.guild.id)
        if guild_id in farweller_settings:
            if farweller_settings[guild_id] == channel.id:
                embed_error_set = discord.Embed(
                    title="Error! 🚫",
                    description="❯ The chosen channel is already set as the farweller channel.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error_set, ephemeral=True)
                return
        guild_id = str(interaction.guild.id)
        farweller_settings[guild_id] = channel.id
        save_farweller_settings()
        embed = discord.Embed(
            title="Farweller Channel Set",
            description=f"❯ Farweller channel has been set to {channel.mention}.",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed)
        mod_log_channel_id = mod_log_settings.get(guild_id)
        if mod_log_channel_id:
            mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
            if mod_log_channel:
                embed_log = discord.Embed(
                    title="Farweller Channel Set",
                    description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] has set the farwell channel to {channel.mention}",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
            await mod_log_channel.send(embed=embed_log)
    @remove_group.command(name="farweller", description="Remove the Farweller channel setting")
    async def remove_farweller(self, interaction):
        if not interaction.user.guild_permissions.manage_messages:
            embed_error_perms = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`manage_messages`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_perms, ephemeral=True)
            return

        guild_id = str(interaction.guild.id)
        if guild_id in welcomer_settings:
            del farweller_settings[guild_id]
            save_farweller_settings()
            embed = discord.Embed(
                title="Farweller Channel Removed",
                description="❯ The Farweller channel setting has been removed for this server.",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.purple()
            )
            await interaction.response.send_message(embed=embed)
            mod_log_channel_id = mod_log_settings.get(guild_id)
            if mod_log_channel_id:
                mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                if mod_log_channel:
                    embed_log = discord.Embed(
                        title="Farweller Channel Removed",
                        description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] has removed the farwell channel setting",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.purple()
                    )
                await mod_log_channel.send(embed=embed_log)
        else:
            embed = discord.Embed(
                title="Error! 🚫",
                description="❯ There was no welcomer channel setting to remove.",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    @app_commands.command(name="suggestions", description="Set the suggestion channel")
    async def setting_suggestions(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.manage_messages:
            embed_error_perms = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`manage_messages`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_perms, ephemeral=True)
            return
        guild_id = str(interaction.guild.id)
        if guild_id in suggestion_settings:
            if suggestion_settings[guild_id] == channel.id:
                embed_error_set = discord.Embed(
                    title="Error! 🚫",
                    description="❯ The chosen channel is already set as the suggestions channel.",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error_set, ephemeral=True)
                return
        guild_id = str(interaction.guild.id)
        suggestion_settings[guild_id] = channel.id
        save_suggestion_settings()
        embed = discord.Embed(
            title="Suggestion Channel Set",
            description=f"❯ Suggestion channel has been set to {channel.mention}.",
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed)
        mod_log_channel_id = mod_log_settings.get(guild_id)
        if mod_log_channel_id:
            mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
            if mod_log_channel:
                embed_log = discord.Embed(
                    title="Suggestion Channel Set",
                    description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] has set the suggestions channel to {channel.mention}",
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                    color=discord.Color.purple()
                )
            await mod_log_channel.send(embed=embed_log)
    @remove_group.command(name="suggestions", description="Remove the suggestion channel setting")
    async def remove_suggestions(self, interaction):
        if not interaction.user.guild_permissions.manage_messages:
            embed_error_perms = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`manage_messages`)",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_perms, ephemeral=True)
            return

        guild_id = str(interaction.guild.id)
        if guild_id in suggestion_settings:
            del suggestion_settings[guild_id]
            save_suggestion_settings()
            embed = discord.Embed(
                title="Suggestion Channel Removed",
                description="❯ The suggestion channel setting has been removed for this server.",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.purple()
            )
            await interaction.response.send_message(embed=embed)
            mod_log_channel_id = mod_log_settings.get(guild_id)
            if mod_log_channel_id:
                mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                if mod_log_channel:
                    embed_log = discord.Embed(
                        title="Suggestion Channel Removed",
                        description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] has removed the suggestions channel setting",
                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                        color=discord.Color.purple()
                    )
                await mod_log_channel.send(embed=embed_log)
        else:
            embed = discord.Embed(
                title="Error! 🚫",
                description="❯ There was no suggestion channel setting to remove.",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
async def setup(client):
    await client.add_cog(moderation(client))
    await client.add_cog(setting_group_moderation(client))