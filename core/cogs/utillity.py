import discord
from discord import app_commands
from discord.ui import View
from discord.ext import commands, tasks
import aiomysql
import os
import requests
import random
import datetime
import humanize
import re
import typing
from PIL import Image, ImageDraw, ImageFont
import io
from typing import Any, Coroutine, Literal, Optional, Type
from utils.tools import *
color_pallet_codes = [
    {"name": "Red", "hex": "FF0000"},
    {"name": "Green", "hex": "00FF00"},
    {"name": "Blue", "hex": "0000FF"},
    {"name": "Yellow", "hex": "FFFF00"},
    {"name": "Purple", "hex": "800080"},
    {"name": "Cyan", "hex": "00FFFF"},
    {"name": "Orange", "hex": "FFA500"},
    {"name": "Pink", "hex": "FFC0CB"},
    {"name": "Brown", "hex": "A52A2A"},
]
current_dir = os.path.dirname(os.path.abspath('/home/ore/Documents/pixel/core/arial.ttf'))
font_path = os.path.join(current_dir, 'arial.ttf')
giveaways = {}
voted_users = {}
async def handle_reaction_removal_after_end(message_id):
    if message_id in giveaways:
        giveaway_data = giveaways[message_id]
        channel = giveaway_data["channel"]
        participants = giveaway_data["participants"]
        if participants:
            winner = random.choice(list(participants))
            await channel.send(f"🎉 **Giveaway Ended!**\nWinner: {winner.mention}\nPrize: {giveaway_data['prize']}")
        else:
            await channel.send(f"🎉 **Giveaway Ended!**\nNo one participated. Prize: {giveaway_data['prize']}")
        del giveaways[message_id]
async def update_giveaway_participants(message_id, participants_count):
    if message_id in giveaways:
        giveaway_data = giveaways[message_id]
        embed = giveaway_data["message"].embeds[0]
        embed.set_field_at(1, name="Participants", value=str(participants_count), inline=True)
        await giveaway_data["message"].edit(embed=embed)
@tasks.loop(seconds=5)
async def giveaway_check():
    current_time = datetime.datetime.now()
    for message_id, giveaway_data in list(giveaways.items()):
        if current_time >= giveaway_data["end_time"]:
            await handle_reaction_removal_after_end(message_id)
        else:
            remaining_time = giveaway_data["end_time"] - current_time
            embed = giveaway_data["message"].embeds[0]
            embed.set_field_at(0, name="duration", value=humanize.naturaldelta(remaining_time), inline=True)
            await giveaway_data["message"].edit(embed=embed)
class utility(commands.Cog):
    def __init__(self, client):
        super().__init__()
        self.client = client
    @app_commands.command(name="server_info", description="Shows information about the server")
    async def server_info(self, interaction):
        server = interaction.guild
        if server is not None:
            total_members = server.member_count
            total_roles = len(server.roles)
            embed = discord.Embed(
                title=f"Server Information - {server.name}",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.purple()
            )
            if server.icon:
                embed.set_thumbnail(url=server.icon)
            embed.add_field(name="Server Name", value=f"❯ {server.name}", inline=False)
            embed.add_field(name="Server ID", value=f"❯ {server.id}", inline=False)
            embed.add_field(name="Owner", value=f"❯ {server.owner.mention}", inline=True)
            embed.add_field(name="Total Members", value=f"❯ {total_members}", inline=True)
            embed.add_field(name="Created On", value="❯ " + server.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
            embed.add_field(name="Number of Text Channels", value=f"❯ {len(server.text_channels)}", inline=True)
            embed.add_field(name="Number of Voice Channels", value=f"❯ {len(server.voice_channels)}", inline=True)
            embed.add_field(name="Total Roles", value=f"❯ {total_roles}", inline=True)
            await interaction.response.send_message(embed=embed)
    @app_commands.command(name="member_count", description="displays the member count of the current server")
    async def member_count(self, interaction):
        server = interaction.guild
        server_member_count = server.member_count
        embed = discord.Embed(
            title="member count",
            description=f"❯ {server_member_count}",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed)
    @app_commands.command(name="info", description="shows basic info about the user")
    async def info(self, interaction: discord.Interaction, member: discord.Member = None):
        if member is None:
            member = interaction.user
        embed_gen = discord.Embed(
            title="generation",
            description="generating the info image...",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed_gen)
        existing_image = Image.open('/home/ore/Documents/pixel/core/template_info.png')
        draw = ImageDraw.Draw(existing_image)
        font = ImageFont.truetype(font_path, 50)
        small_font = ImageFont.truetype(font_path, 45)
        white_color = (255, 255, 255)
        draw.text((118, 886), truncate_long_name(member.display_name, 15), fill=white_color, font=font)
        draw.text((125, 1067), truncate_long_name(member.name, 15), fill=white_color, font=font)
        draw.text((1090, 42), f"{member.id}", fill=white_color, font=small_font)
        draw.text((723, 886), f"{member.created_at.strftime('%Y-%m-%d %H:%M:%S')}", fill=white_color, font=font)
        draw.text((723, 1067), f"{member.joined_at.strftime('%Y-%m-%d %H:%M:%S')}", fill=white_color, font=font)
        roles = [role.name for role in member.roles if role.name != "@everyone"]
        if roles:
            max_role_chars = 20 
            roles_with_ellipsis = [f"@{role[:max_role_chars]}{'...' if len(role) > max_role_chars else ''}" for role in roles]
            role_text = ", ".join(roles_with_ellipsis)
            max_chars_per_line = 45
            max_lines = 4
            lines = []
            line_count = 0
            line = ""
            for word in role_text.split():
                if line_count >= max_lines:
                    break
                if len(line + word) <= max_chars_per_line:
                    line += word + " "
                else:
                    lines.append(line.strip())
                    line = word + " "
                    line_count += 1
            if line:
                lines.append(line.strip())
            if len(lines) > int(max_lines):
                lines = lines[:int(max_lines)]
                lines[-1] = lines[-1][:-3] + "..."
            role_y = 490
            for line in lines:
                draw.text((120, role_y), line, fill=white_color, font=font)
                role_y += 60
        user_nitro = await self.client.fetch_user(member.id)
        if user_nitro.banner is not None:
            banner_image_url = str(user_nitro.banner)
            response = requests.get(banner_image_url)
            banner_image_data = response.content
            banner_image = Image.open(io.BytesIO(banner_image_data))
            banner_image = banner_image.resize((1016, 285))
            radius = 28
            mask = Image.new("L", banner_image.size, 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.rounded_rectangle([(0, 0), banner_image.size], radius, fill=255)
            existing_image.paste(banner_image, (533, 102), mask=mask)
        if member.avatar.url:
            response = requests.get(member.avatar.url)
            if response.status_code == 200:
                avatar_image = Image.open(io.BytesIO(response.content))
                avatar_image = avatar_image.resize((386, 367))
                mask = Image.new("L", avatar_image.size, 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, mask.size[0], mask.size[1]), fill=255)
                avatar_image.putalpha(mask)
                existing_image.paste(avatar_image, (88, 61), mask=mask)
        image_bytes = io.BytesIO()
        existing_image.save(image_bytes, format='PNG')
        image_bytes.seek(0)
        generated_image = await interaction.followup.send(file=discord.File(image_bytes, filename='info.png'))
        class ButtonView(View):
            def __init__(self, message, author, timeout=60):
                super().__init__(timeout=timeout)
                self.message = message
                self.author = author
            @discord.ui.button(label="avatar", style=discord.ButtonStyle.grey)
            async def avatar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                if member.avatar:
                    avatar_url = member.avatar.url
                    embed = discord.Embed(
                        title=f"{member.display_name}'s Profile Picture",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.purple()
                    )
                    embed.set_image(url=avatar_url)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    embed_error = discord.Embed(
                        title="Error! 🚫",
                        description="the user doesnt seem to have an avatar.",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_error, ephemeral=True)
            @discord.ui.button(label="id", style=discord.ButtonStyle.grey)
            async def id_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                embed_member_id = discord.Embed(
                    title="id",
                    description=f"❯ member id: {member.id}",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.purple()
                )
                await interaction.response.send_message(embed=embed_member_id, ephemeral = True)
            @discord.ui.button(label="roles", style=discord.ButtonStyle.grey)
            async def roles_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                roles = [role.mention for role in member.roles if role.name != "@everyone"]
                if roles:
                    role_list = ', '.join(roles)
                else:
                    embed_error = discord.Embed(
                        title="Error! 🚫",
                        description="❯ No roles found.",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_error, ephemeral = True)
                    return
                embed = discord.Embed(
                    title=f"Roles for {member.display_name}",
                    description=f"❯ {role_list}",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.purple()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            async def interaction_check(self, interaction: discord.Interaction):
                if interaction.user.id != self.author.id:
                    embed_ownership = discord.Embed(
                        title="Error! 🚫",
                        description="You cannot interact with an other member interaction.",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_ownership, ephemeral=True)
                    return False
                return True
            async def on_timeout(self) -> None:
                await self.message.edit(view=button_view_timeout())
        view = ButtonView(generated_image, interaction.user)
        await generated_image.edit(view=view)
    @app_commands.command(name="roles", description="displays the user roles")
    async def roles(self, interaction: discord.Interaction, member: discord.Member = None):
        if not member:
            member = interaction.user
        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        if roles:
            role_list = ', '.join(roles)
        else:
            embed_error = discord.Embed(
                title="Error! 🚫",
                description="❯ No roles found.",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error)
            return
        embed = discord.Embed(
            title=f"Roles for {member.display_name}",
            description=f"❯ {role_list}",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url=member.avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral = True)
    @app_commands.command(name="avatar", description="shows the user avatar")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        if member is None:
            member = interaction.user
        if member.avatar:
            avatar_url = member.avatar.url
            embed = discord.Embed(
                title=f"{member.display_name}'s Profile Picture",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.purple()
            )
            embed.set_image(url=avatar_url)
            await interaction.response.send_message(embed=embed)
        else:
            embed_error = discord.Embed(
                title="Error! 🚫",
                description="the user doesnt seem to have an avatar.",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)
    @app_commands.command(name="giveaway", description="starts and giveaway")
    async def giveaway(self, interaction: discord.Interaction, prize: str, duration: str):
        if interaction.user.guild_permissions.manage_messages:
            duration_seconds = parse_duration(duration)
            if duration_seconds is None or duration_seconds <= 0:
                await interaction.response.send_message("Invalid duration format. Use 'd' for days or 'h' for hours or '1m' for minutes or '1s' for seconds.")
                return
            embed = discord.Embed(
                title="🎉 Giveaway",
                description=(f"prize: {prize}"),
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.purple()
            )
            embed.add_field(name="Remaining time", value=humanize.naturaldelta(datetime.timedelta(seconds=duration_seconds)), inline=True)
            embed.add_field(name="Participants", value="0", inline=True)
            embed.set_footer(text=f"Hosted by {interaction.user.display_name}")
            giveaway_message = await interaction.channel.send(embed=embed)
            await giveaway_message.add_reaction('🎉')
            giveaways[giveaway_message.id] = {
                "giveaway": giveaway_message.id,
                "channel": interaction.channel,
                "message": giveaway_message,
                "end_time": datetime.datetime.now() + datetime.timedelta(seconds=duration_seconds),
                "prize": prize,
                "participants": set()
            }
            embed = discord.Embed(
                title="success",
                description="❯ giveaway started",
                color=discord.Color.purple()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed_error = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`manage_messages`)",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        message_id = reaction.message.id
        if message_id in giveaways and reaction.emoji == "🎉":
            giveaways[message_id]["participants"].add(user)
            participants_count = len(giveaways[message_id]["participants"])
            await update_giveaway_participants(message_id, participants_count)
    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        message_id = reaction.message.id
        if message_id in giveaways and reaction.emoji == "🎉":
            if giveaways[message_id]["end_time"] > datetime.datetime.now():
                giveaways[message_id]["participants"].discard(user)
                participants_count = len(giveaways[message_id]["participants"])
                await update_giveaway_participants(message_id, participants_count)
    @app_commands.checks.cooldown(1, 1800, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name="suggest", description="Submit a suggestion")
    async def suggest(self, interaction: discord.Interaction, suggestion: str):
        guild_id = str(interaction.guild.id)
        suggestion_channel_id = suggestion_settings.get(guild_id)
        if suggestion_channel_id is None:
            embed_error_set = discord.Embed(
                title="Error! 🚫",
                description="❯ No suggestion channel has been set for this server.",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_set, ephemeral=True)
            return
        if guild_id in chat_filter_settings and chat_filter_settings[guild_id]:
            if check_message(suggestion):
                embed_error_content = discord.Embed(
                    title="Error! 🚫",
                    description="❯ Suggestion content is inappropriate.",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error_content, ephemeral=True)
                mod_log_channel_id = mod_log_settings.get(guild_id)
                if mod_log_channel_id:
                    mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                    if mod_log_channel:
                        embed_log = discord.Embed(
                            title="auto-moderation",
                            description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] triggered the auto-moderation in {interaction.channel.mention}",
                            timestamp=datetime.datetime.utcnow(),
                            color=discord.Color.purple()
                        )
                        await mod_log_channel.send(embed=embed_log)
                return
        if guild_id in anti_link_settings and anti_link_settings[guild_id]:
            links = re.findall(url_pattern, suggestion)
            if links:
                for link in links:
                    embed_error_content = discord.Embed(
                        title="Error! 🚫",
                        description="❯ Links are not allowed.",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_error_content, ephemeral=True)
                    mod_log_channel_id = mod_log_settings.get(guild_id)
                    if mod_log_channel_id:
                        mod_log_channel = interaction.guild.get_channel(mod_log_channel_id)
                        if mod_log_channel:
                            embed_log = discord.Embed(
                                title="auto-moderation",
                                description=f"❯ {interaction.user.mention}[`{interaction.user.id}`] triggered the auto-moderation in {interaction.channel.mention}",
                                timestamp=datetime.datetime.utcnow(),
                                color=discord.Color.purple()
                            )
                            await mod_log_channel.send(embed=embed_log)
                    return
        suggestion_channel = self.client.get_channel(suggestion_channel_id)
        upvotes = 0
        downvotes = 0
        total_votes = upvotes + downvotes
        upvotes_percentage = (upvotes / total_votes) * 100 if total_votes > 0 else 0
        downvotes_percentage = (downvotes / total_votes) * 100 if total_votes > 0 else 0
        original_user = interaction.user
        embed = discord.Embed(
            title="Suggestion",
            description=f"content: {suggestion} | upvotes: {upvotes} ({upvotes_percentage:.2f}%) | downvotes: {downvotes} ({downvotes_percentage:.2f}%) | status: pending",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        if original_user.avatar:
            embed.set_author(name=f" |  {original_user.display_name}", icon_url=original_user.avatar.url)
        if not original_user.avatar:
            embed.set_author(name=original_user.display_name)
        suggestion_message = await suggestion_channel.send(embed=embed)
        class ButtonView(View):
            def __init__(self, suggestion_message_id, upvotes, downvotes, author, timeout=None):
                super().__init__(timeout=timeout)
                self.suggestion_message_id = suggestion_message_id
                self.upvotes = upvotes
                self.downvotes = downvotes
                self.author = author
                self.status = "pending"
            @discord.ui.button(emoji="<:discotoolsxyzicon35:1178763469026246716>", style=discord.ButtonStyle.secondary, custom_id="Persistent_suggestion_button0")
            async def upvote(self, interaction: discord.Interaction, button: discord.ui.Button):
                user_id = interaction.user.id
                user_vote_key = (self.suggestion_message_id, user_id)
                if user_vote_key in voted_users:
                    embed_key_limit = discord.Embed(
                        title="Error! 🚫",
                        description="You have already voted on this suggestion.",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_key_limit, ephemeral=True)
                    return
                self.upvotes += 1
                total_votes = self.upvotes + self.downvotes
                upvotes_percentage = (self.upvotes / total_votes) * 100 if total_votes > 0 else 0
                downvotes_percentage = (self.downvotes / total_votes) * 100 if total_votes > 0 else 0
                embed = discord.Embed(
                    title="Suggestion",
                    description=f"content: {suggestion} | upvotes: {self.upvotes} ({upvotes_percentage:.2f}%) | downvotes: {self.downvotes} ({downvotes_percentage:.2f}%) | status: {self.status}",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.purple()
                )
                if original_user.avatar:
                    embed.set_author(name=f" |  {self.author.display_name}", icon_url=self.author.avatar.url)
                if not original_user.avatar:
                    embed.set_author(name=self.author.display_name)
                await suggestion_message.edit(embed=embed)
                voted_users[user_vote_key] = "voted"
                embed_success = discord.Embed(
                    title="upvoted",
                    description="suggestion upvoted successfully",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.purple()
                )
                await interaction.response.send_message(embed=embed_success, ephemeral=True)
            @discord.ui.button(emoji="<:discotoolsxyzicon36:1178763738287984750>", style=discord.ButtonStyle.secondary, custom_id="Persistent_suggestion_button1")
            async def downvote(self, interaction: discord.Interaction, button: discord.ui.Button):
                user_id = interaction.user.id
                user_vote_key = (self.suggestion_message_id, user_id)
                if user_vote_key in voted_users:
                    embed_key_limit = discord.Embed(
                        title="Error! 🚫",
                        description="You have already voted on this suggestion.",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_key_limit, ephemeral=True)
                    return
                self.downvotes += 1
                total_votes = self.upvotes + self.downvotes
                upvotes_percentage = (self.upvotes / total_votes) * 100 if total_votes > 0 else 0
                downvotes_percentage = (self.downvotes / total_votes) * 100 if total_votes > 0 else 0
                embed = discord.Embed(
                    title="Suggestion",
                    description=f"content: {suggestion} | upvotes: {self.upvotes} ({upvotes_percentage:.2f}%) | downvotes: {self.downvotes} ({downvotes_percentage:.2f}%) | status: {self.status}",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.purple()
                )
                if original_user.avatar:
                    embed.set_author(name=f" |  {self.author.display_name}", icon_url=self.author.avatar.url)
                if not original_user.avatar:
                    embed.set_author(name=self.author.display_name)
                await suggestion_message.edit(embed=embed)
                voted_users[user_vote_key] = "voted"
                embed_success = discord.Embed(
                    title="upvoted",
                    description="suggestion downvoted successfully",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.purple()
                )
                await interaction.response.send_message(embed=embed_success, ephemeral=True)
            @discord.ui.button(emoji="<:discotoolsxyzicon39:1183954029638864967>", style=discord.ButtonStyle.secondary, custom_id="voters_button")
            async def display_voters(self, interaction: discord.Interaction, button: discord.ui.Button):
                if not interaction.user.guild_permissions.manage_messages:
                    embed_error = discord.Embed(
                        title="Error! 🚫",
                        description="❯ You don't have the required permissions to use this interaction. (`manage_messsages`)",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_error, ephemeral=True)
                    return
                suggestion_ids = set([key[0] for key in voted_users.keys()])
                embeds = []
                embed_limit = 10
                voters_exist = False
                for suggestion_id in suggestion_ids:
                    voters_for_suggestion = [user_id for (suggestion, user_id) in voted_users if suggestion == suggestion_id]  
                    if voters_for_suggestion:
                        voters_mentions = [f"<@{voter}>" for voter in voters_for_suggestion]
                        voters_list_pages = [voters_mentions[i:i + embed_limit] for i in range(0, len(voters_mentions), embed_limit)]

                        for i, voters_page in enumerate(voters_list_pages):
                            embed = discord.Embed(
                                title=f"List of Voters (found: {len(voters_mentions)} voter(s))",
                                description='\n'.join(voters_page),
                                timestamp=datetime.datetime.utcnow(),
                                color=discord.Color.purple()
                            )
                            embed.set_footer(text="Page {}/{}".format((i // embed_limit) + 1, (len(voters_list_pages) - 1) // embed_limit + 1 if len(voters_list_pages) % embed_limit != 0 else len(voters_list_pages) // embed_limit))
                            embeds.append(embed)
                            voters_exist = True
                if not voters_exist:
                    embed_error_exis = discord.Embed(
                        title=f"Error! 🚫",
                        description="no voters found.",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_error_exis, ephemeral=True)
                    return
                class ButtonViewIn(View):
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
                                timestamp=datetime.datetime.utcnow(),
                                color=discord.Color.orange()
                            )
                            await interaction.response.send_message(embed=embed_ownership, ephemeral=True)
                            return False
                        return True
                view = ButtonViewIn(interaction, interaction.user, embeds)
                await interaction.response.send_message(embed=embeds[0], view=view, ephemeral=True)
            @discord.ui.button(emoji="<:discotoolsxyzicon37:1178763859071344701>", style=discord.ButtonStyle.secondary, custom_id="Persistent_suggestion_button2")
            async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
                if not interaction.user.guild_permissions.manage_messages:
                    embed_error = discord.Embed(
                        title="Error! 🚫",
                        description="❯ You don't have the required permissions to use this interaction. (`manage_messsages`)",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_error, ephemeral=True)
                    return 
                self.status = f"approved by: {interaction.user.mention}"
                total_votes = self.upvotes + self.downvotes
                upvotes_percentage = (self.upvotes / total_votes) * 100 if total_votes > 0 else 0
                downvotes_percentage = (self.downvotes / total_votes) * 100 if total_votes > 0 else 0
                embed = discord.Embed(
                    title="Suggestion",
                    description=f"content: {suggestion} | upvotes: {self.upvotes} ({upvotes_percentage:.2f}%) | downvotes: {self.downvotes} ({downvotes_percentage:.2f}%) | status: {self.status}",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.green()
                )
                if original_user.avatar:
                    embed.set_author(name=f" |  {self.author.display_name}", icon_url=self.author.avatar.url)
                if not original_user.avatar:
                    embed.set_author(name=self.author.display_name)
                embed_status_confirm = discord.Embed(
                    title="approved",
                    description="suggestion approved successfully",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.purple()
                )
                await interaction.response.send_message(embed=embed_status_confirm, ephemeral=True)
                for item in view.children:
                    item.disabled = True
                await suggestion_message.edit(embed=embed, view=view)
            @discord.ui.button(emoji="<:discotoolsxyzicon38:1178763916914991164>", style=discord.ButtonStyle.secondary, custom_id="Persistent_suggestion_button3")
            async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
                if not interaction.user.guild_permissions.manage_messages:
                    embed_error = discord.Embed(
                        title="Error! 🚫",
                        description="❯ You don't have the required permissions to use this interaction. (`manage_messsages`)",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_error, ephemeral=True)
                    return
                self.status = f"rejected by: {interaction.user.mention}"
                total_votes = self.upvotes + self.downvotes
                upvotes_percentage = (self.upvotes / total_votes) * 100 if total_votes > 0 else 0
                downvotes_percentage = (self.downvotes / total_votes) * 100 if total_votes > 0 else 0
                embed = discord.Embed(
                    title="Suggestion",
                    description=f"content: {suggestion} | upvotes: {self.upvotes} ({upvotes_percentage:.2f}%) | downvotes: {self.downvotes} ({downvotes_percentage:.2f}%) | status: {self.status}",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.red()
                )
                if original_user.avatar:
                    embed.set_author(name=f" |  {self.author.display_name}", icon_url=self.author.avatar.url)
                if not original_user.avatar:
                    embed.set_author(name=self.author.display_name)
                embed_status_confirm = discord.Embed(
                    title="rejected",
                    description="suggestion rejected successfully",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.purple()
                )
                await interaction.response.send_message(embed=embed_status_confirm, ephemeral=True)
                for item in view.children:
                    item.disabled = True
                await suggestion_message.edit(embed=embed, view=view)
            async def interaction_check(self, interaction: discord.Interaction):
                if interaction.user.id == self.author.id:
                    embed_ownership = discord.Embed(
                        title="Error! 🚫",
                        description="You cannot interact with your own suggestion.",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_ownership, ephemeral=True)
                    return False
                return True
        view = ButtonView(suggestion_message.id, upvotes, downvotes, original_user)
        await suggestion_message.edit(view=view)
        embed_success = discord.Embed(
            title="Suggestion Submitted",
            description="❯ Your suggestion has been submitted successfully.",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed_success)
    @suggest.error
    async def suggest_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, discord.app_commands.CommandOnCooldown):
            remaining_time = humanize.naturaldelta(error.retry_after)
            embed = discord.Embed(
                title="Cooldown! ⏳",
                description=f"❯ Please wait {remaining_time} before using this command again.",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(f"{str(error)}", ephemeral=True)
    @app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
    @app_commands.command(name="shorten_url", description="shortens the provided url")
    async def shorten_url(self, interaction: discord.Interaction, url: str):
        try:
            response = requests.get(f'http://tinyurl.com/api-create.php?url={url}')
            if response.status_code == 200:
                short_url = response.text
                embed = discord.Embed(
                    title="url shortened",
                    description=f"Shortened URL: {short_url}",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.purple()
                )
                await interaction.response.send_message(embed=embed, ephemeral = True)
            else:
                embed_error = discord.Embed(
                    title="Error! 🚫",
                    description="Failed to shorten the URL.",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error, ephemeral = True)
        except Exception as e:
            embed_error_exc = discord.Embed(
                title="Error! 🚫",
                description=f"An error occurred: {str(e)}",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_exc, ephemeral = True)
    @shorten_url.error
    async def shorten_url_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, discord.app_commands.CommandOnCooldown):
            remaining_time = humanize.naturaldelta(error.retry_after)
            embed = discord.Embed(
                title="Cooldown! ⏳",
                description=f"❯ Please wait {remaining_time} before using this command again.",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(f"{str(error)}", ephemeral=True)
class embed_group_utillity(commands.GroupCog, group_name="embed", group_description="`embed` commands group"):
    def __init__(self, client):
        super().__init__()
        self.client = client
    @app_commands.command(name="create", description="Creates an embed based on user input")
    async def embed_create(self, interaction: discord.Interaction, embed_color: app_commands.Range[str, 1, 16], timestamp_state:Literal["on", "off"], title: app_commands.Range[str, 1, 250], description: app_commands.Range[str, 1, 4000], fields: app_commands.Range[str, 1, 6000] = None, author: app_commands.Range[str, 1, 250] = None, author_img_url: app_commands.Range[str, 1, 150] = None, footer: app_commands.Range[str, 1, 2000] = None, footer_img_url: app_commands.Range[str, 1, 150] = None, embed_thumbnail_url: app_commands.Range[str, 1, 150] = None):
        if interaction.user.guild_permissions.manage_messages:
            color = discord.Color(int(embed_color, 16))
            if timestamp_state == "off":
                embed = discord.Embed(title=title, description=description, color=color)
            if timestamp_state == "on":
                embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.datetime.utcnow())
            if fields:
                field_items = fields.split('|')
                if len(field_items) % 2 == 0:
                    for i in range(0, len(field_items), 2):
                        header = field_items[i]
                        field = field_items[i + 1]
                        embed.add_field(name=header, value=field, inline=False)
                else:
                    await interaction.channel.send("Invalid number of field parameters. You should provide pairs of header and value separated by '|'.")   
            if author:
                if not author_img_url:
                    embed.set_author(name=author)
            if not author:
                if author_img_url:
                    embed.set_author(name=" |  ", icon_url=author_img_url)
            if author and author_img_url:
                embed.set_author(name=f" |  {author}", icon_url=author_img_url)
            if footer:
                if not footer_img_url:
                    embed.set_footer(text=footer)
            if not footer:
                if footer_img_url:
                    embed.set_footer(text=f" |  ", icon_url=footer_img_url)
            if footer and footer_img_url:
                embed.set_footer(text=f" |  {footer}", icon_url=footer_img_url)
            if footer_img_url:
                if not footer:
                    embed.set_footer(text="  -", icon_url=footer_img_url)
            if embed_thumbnail_url:
                embed.set_thumbnail(url=embed_thumbnail_url)
            generated_embed = await interaction.channel.send(embed=embed)
            conn = await aiomysql.connect(
                host="161.97.78.70",
                port=3306,
                user="u38240_JdAbZAvfxO",
                password="H2wzrrusqEf@Hj7slG1LuKF@",
                db="s38240_database",
                charset='utf8mb4',
                cursorclass=aiomysql.DictCursor
            )
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO embeds (guild_id, channel_id, message_id) VALUES (%s, %s, %s)",
                    (interaction.guild.id, interaction.channel.id, generated_embed.id)
                )
                await conn.commit()
            conn.close()
            embed_success = discord.Embed(
                title="success",
                description="the embed has been created successfully",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.purple()
            )
            await interaction.response.send_message(embed=embed_success, ephemeral = True)
        else:
            embed_error = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`manage_messages`)",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)
    @app_commands.command(name="edit", description="Edits an existing generated embed based on user input")
    async def embed_edit(self, interaction: discord.Interaction, embed_id: str, embed_color: app_commands.Range[str, 1, 16], timestamp_state:Literal["on", "off"], title: app_commands.Range[str, 1, 250], description: app_commands.Range[str, 1, 4000], fields: app_commands.Range[str, 1, 6000] = None, author: app_commands.Range[str, 1, 250] = None, author_img_url: app_commands.Range[str, 1, 150] = None, footer: app_commands.Range[str, 1, 2000] = None, footer_img_url: app_commands.Range[str, 1, 150] = None, embed_thumbnail_url: app_commands.Range[str, 1, 150] = None):
        if interaction.user.guild_permissions.manage_messages:
            conn = await aiomysql.connect(
                host="161.97.78.70",
                port=3306,
                user="u38240_JdAbZAvfxO",
                password="H2wzrrusqEf@Hj7slG1LuKF@",
                db="s38240_database",
                charset='utf8mb4',
                cursorclass=aiomysql.DictCursor
            )
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT * FROM embeds WHERE guild_id = %s AND message_id = %s", (interaction.guild.id, embed_id))
                data = await cursor.fetchone()
            if data:
                try:
                    channel = await interaction.guild.fetch_channel(data['channel_id'])
                    original_message = await channel.fetch_message(embed_id)
                except discord.Forbidden:
                    embed_error = discord.Embed(
                        title="Error! 🚫",
                        description="Cannot fetch the embed id.",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_error, ephemeral=True)
                    return
                color = discord.Color(int(embed_color, 16))
                if timestamp_state == "off":
                    embed = discord.Embed(title=title, description=description, color=color)
                if timestamp_state == "on":
                    embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.datetime.utcnow())  
                if fields:
                    field_items = fields.split('|')
                    if len(field_items) % 2 == 0:
                        for i in range(0, len(field_items), 2):
                            header = field_items[i]
                            field = field_items[i + 1]
                            embed.add_field(name=header, value=field, inline=False)
                    else:
                        await interaction.response.send_message("Invalid number of field parameters. You should provide pairs of header and value separated by '|'.")
                        return
                if author:
                    if not author_img_url:
                        embed.set_author(name=author)
                if not author:
                    if author_img_url:
                            embed.set_author(name=" |  ", icon_url=author_img_url)
                if author and author_img_url:
                    embed.set_author(name=f" |  {author}", icon_url=author_img_url)
                if footer:
                    if not footer_img_url:
                        embed.set_footer(text=footer)
                if not footer:
                    if footer_img_url:
                        embed.set_footer(text=f" |  ", icon_url=footer_img_url)
                if footer and footer_img_url:
                    embed.set_footer(text=f" |  {footer}", icon_url=footer_img_url)
                if footer_img_url:
                    if not footer:
                        embed.set_footer(text="  -", icon_url=footer_img_url)
                if embed_thumbnail_url:
                    embed.set_thumbnail(url=embed_thumbnail_url)
                try:
                    await original_message.edit(embed=embed)
                except discord.Forbidden:
                    embed_error = discord.Embed(
                        title="Error! 🚫",
                        description="Cannot edit the message",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_error, ephemeral=True)
                    return
                embed_success = discord.Embed(
                    title="Success",
                    description="The embed has been `edited` successfully",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.purple()
                )  
                await interaction.response.send_message(embed=embed_success)
            else:
                embed_error_fetch = discord.Embed(
                    title="Error! 🚫",
                    description="❯ invalid id.",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error_fetch, ephemeral=True)
        else:
            embed_error = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`manage_messages`)",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)
    @app_commands.command(name="color_codes", description="shows an list of hex color codes to use in embed creation")
    async def embed_colors(self, interaction):
        embed = discord.Embed(
            title="Hex Color Codes pallet",
            description="❯ Here are some colors with their names and hex codes:",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        for color in color_pallet_codes:
            embed.add_field(name=color["name"], value=f"❯ {color['hex']}", inline=True)
        embed.add_field(name="You can choose more specific colors in", value="❯ [here](https://htmlcolorcodes.com/color-picker/)", inline=False)
        await interaction.response.send_message(embed=embed)
class tag_group_utillity(commands.GroupCog, group_name="tag", group_description="`tag` commands group"):
    def __init__(self, client):
        super().__init__()
        self.client = client
    @app_commands.command(name="add", description="adds a tag")
    @app_commands.describe(tag_name="the tag name", tag_content="the tag content", display_as_embed="display the tag as an embed (on/off)")
    async def add_tag(self, interaction: discord.Interaction, tag_name: str, tag_content: app_commands.Range[str, 30, 1000], display_as_embed: Literal["on", "off"]):
        if interaction.user.guild_permissions.manage_messages:
            async with aiomysql.connect(
                host="161.97.78.70",
                port=3306,
                user="u38240_JdAbZAvfxO",
                password="H2wzrrusqEf@Hj7slG1LuKF@",
                db="s38240_database",
                charset='utf8mb4',
                cursorclass=aiomysql.DictCursor
            ) as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(
                        "SELECT * FROM tags WHERE guild_id = %s AND tag_name = %s",
                        (interaction.guild.id, tag_name)
                    )
                    existing_tag = await cursor.fetchone()
                    if existing_tag:
                        embed_error_exis = discord.Embed(
                            title="Error! 🚫",
                            description=f"The tag with the name: **{tag_name}** already exists.",
                            timestamp=datetime.datetime.utcnow(),
                            color=discord.Color.orange()
                        )
                        await interaction.response.send_message(embed=embed_error_exis, ephemeral=True)
                        return

                async with aiomysql.connect(
                    host="161.97.78.70",
                    port=3306,
                    user="u38240_JdAbZAvfxO",
                    password="H2wzrrusqEf@Hj7slG1LuKF@",
                    db="s38240_database",
                    charset='utf8mb4',
                    cursorclass=aiomysql.DictCursor
                ) as connection:
                    async with connection.cursor() as cursor:
                        await cursor.execute(
                            "INSERT INTO tags (guild_id, tag_name, tag_content, is_embed) VALUES (%s, %s, %s, %s)",
                            (interaction.guild.id, tag_name, tag_content, display_as_embed)
                        )
                        await connection.commit()
                embed_desc = f"The tag: **{tag_name}** has been added"
                if display_as_embed == 'on':
                    embed_desc += " and will be displayed as an embed"
                embed = discord.Embed(
                    title="Tag Added",
                    description=embed_desc,
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.purple()
                )
                await interaction.response.send_message(embed=embed)
        else:
            embed_error = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`manage_messages`)",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)
    @app_commands.command(name="edit", description="Edits the content of the tag")
    @app_commands.describe(tag_name="The tag name", new_content="The new tag content", display_as_embed="Display the tag as an embed (on/off)")
    async def tag_edit(self, interaction: discord.Interaction, tag_name: str, new_content: app_commands.Range[str, 30, 1000], display_as_embed: Literal["on", "off"]):
        if interaction.user.guild_permissions.manage_messages:
            display_as_embed = 'embed' if display_as_embed == 'on' else ''
            async with aiomysql.connect(
                host="161.97.78.70",
                port=3306,
                user="u38240_JdAbZAvfxO",
                password="H2wzrrusqEf@Hj7slG1LuKF@",
                db="s38240_database",
                charset='utf8mb4',
                cursorclass=aiomysql.DictCursor
            ) as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(
                        "SELECT tag_content, is_embed FROM tags WHERE guild_id = %s AND tag_name = %s",
                        (interaction.guild.id, tag_name)
                    )
                    found_tag = await cursor.fetchone()

                    if not found_tag:
                        embed_error_exis = discord.Embed(
                            title="Error! 🚫",
                            description=f"No tags found with name: **{tag_name}**",
                            timestamp=datetime.datetime.utcnow(),
                            color=discord.Color.orange()
                        )
                        await interaction.response.send_message(embed=embed_error_exis, ephemeral=True)
                        return

                    old_content, old_is_embed = found_tag['tag_content'], found_tag['is_embed']
                    if new_content == old_content:
                        embed_error_same_content = discord.Embed(
                            title="Error! 🚫",
                            description="The new content is the same as the old content.",
                            timestamp=datetime.datetime.utcnow(),
                            color=discord.Color.orange()
                        )
                        await interaction.response.send_message(embed=embed_error_same_content, ephemeral=True)
                        return
                    await cursor.execute(
                        "UPDATE tags SET tag_content = %s, is_embed = %s WHERE guild_id = %s AND tag_name = %s",
                        (new_content, display_as_embed, interaction.guild.id, tag_name)
                    )
                    await connection.commit()

                    embed_desc = f"Tag **{tag_name}** has been edited"
                    if display_as_embed == 'embed':
                        embed_desc += " and will be displayed as an embed"

                    embed = discord.Embed(
                        title="Tag Edited ✏️",
                        description=embed_desc,
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.purple()
                    )
                    embed.add_field(name="Old Content", value=old_content)
                    embed.add_field(name="New Content", value=new_content)
                    await interaction.response.send_message(embed=embed)
        else:
            embed_error = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`manage_messages`)",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)
    @tag_edit.autocomplete('tag_name')
    async def tag_edit_autocomplete(
        self, 
        interaction: discord.Interaction,
        current: str,
    ) -> typing.List[app_commands.Choice[str]]:
        tags = []
        async with aiomysql.connect(
            host="161.97.78.70",
            port=3306,
            user="u38240_JdAbZAvfxO",
            password="H2wzrrusqEf@Hj7slG1LuKF@",
            db="s38240_database",
            charset='utf8mb4',
            cursorclass=aiomysql.DictCursor
        ) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT tag_name FROM tags WHERE guild_id = %s AND tag_name LIKE %s",
                    (interaction.guild.id, f"%{current}%")
                )
                tags = await cursor.fetchall()
        choices = [
            app_commands.Choice(name=tag['tag_name'], value=tag['tag_name'])
            for tag in tags[:5]
        ]
        return choices
    @app_commands.command(name="remove", description="Removes the tag")
    @app_commands.describe(tag_name="the tag name")
    async def tag_remove(self, interaction: discord.Interaction, tag_name: str):
        if interaction.user.guild_permissions.manage_messages:
            async with aiomysql.connect(
                host="161.97.78.70",
                port=3306,
                user="u38240_JdAbZAvfxO",
                password="H2wzrrusqEf@Hj7slG1LuKF@",
                db="s38240_database",
                charset='utf8mb4',
                cursorclass=aiomysql.DictCursor
            ) as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(
                        "SELECT tag_name FROM tags WHERE guild_id = %s AND tag_name = %s",
                        (interaction.guild.id, tag_name)
                    )
                    found_tag = await cursor.fetchone()
                    if not found_tag:
                        embed_error_exis = discord.Embed(
                            title="Error! 🚫",
                            description=f"No tags found with name: **{tag_name}**",
                            timestamp=datetime.datetime.utcnow(),
                            color=discord.Color.orange()
                        )
                        await interaction.response.send_message(embed=embed_error_exis, ephemeral=True)
                        return
                    await cursor.execute(
                        "DELETE FROM tags WHERE guild_id = %s AND tag_name = %s",
                        (interaction.guild.id, tag_name)
                    )
                    await connection.commit()
                    embed = discord.Embed(
                        title="Tag Removed",
                        description=f"The tag with the name: **{tag_name}** has been removed.",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.purple()
                    )
                    await interaction.response.send_message(embed=embed)
        else:
            embed_error = discord.Embed(
                title="Error! 🚫",
                description="❯ You don't have the required permissions to use this command. (`manage_messages`)",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)
    @tag_remove.autocomplete('tag_name')
    async def tag_remove_autocomplete(
        self, 
        interaction: discord.Interaction,
        current: str,
    ) -> typing.List[app_commands.Choice[str]]:
        tags = []
        async with aiomysql.connect(
            host="161.97.78.70",
            port=3306,
            user="u38240_JdAbZAvfxO",
            password="H2wzrrusqEf@Hj7slG1LuKF@",
            db="s38240_database",
            charset='utf8mb4',
            cursorclass=aiomysql.DictCursor
        ) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT tag_name FROM tags WHERE guild_id = %s AND tag_name LIKE %s",
                    (interaction.guild.id, f"%{current}%")
                )
                tags = await cursor.fetchall()
        choices = [
            app_commands.Choice(name=tag['tag_name'], value=tag['tag_name'])
            for tag in tags[:5]
        ]
        return choices
    @app_commands.command(name="view", description="Displays the tag")
    @app_commands.describe(tag_name="the tag name")
    async def tag_view(self, interaction: discord.Interaction, tag_name: str):
        found_tag = []
        async with aiomysql.connect(
            host="161.97.78.70",
            port=3306,
            user="u38240_JdAbZAvfxO",
            password="H2wzrrusqEf@Hj7slG1LuKF@",
            db="s38240_database",
            charset='utf8mb4',
            cursorclass=aiomysql.DictCursor
        ) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT tag_content AS content, is_embed FROM tags WHERE guild_id = %s AND tag_name = %s",
                    (interaction.guild.id, tag_name)
                )
                found_tag = await cursor.fetchone()
        
        if not found_tag:
            embed_error_exis = discord.Embed(
                title="Error! 🚫",
                description=f"No tags found with name: **{tag_name}**",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_exis, ephemeral=True)
            return
        
        content, is_embed = found_tag['content'], found_tag['is_embed']
        if is_embed == "on":
            embed = discord.Embed(
                title="Tag",
                description=f"{content}",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.purple()
            )
            await interaction.response.send_message(embed=embed)
        else:
            allowed_mentions = discord.AllowedMentions.none()
            await interaction.response.send_message(content, allowed_mentions=allowed_mentions)
    @tag_view.autocomplete('tag_name')
    async def tag_view_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> typing.List[app_commands.Choice[str]]:
        tags = []
        async with aiomysql.connect(
            host="161.97.78.70",
            port=3306,
            user="u38240_JdAbZAvfxO",
            password="H2wzrrusqEf@Hj7slG1LuKF@",
            db="s38240_database",
            charset='utf8mb4',
            cursorclass=aiomysql.DictCursor
        ) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    "SELECT tag_name FROM tags WHERE guild_id = %s AND tag_name LIKE %s",
                    (interaction.guild.id, f"%{current}%")
                )
                tags = await cursor.fetchall()
        choices = [
            app_commands.Choice(name=tag['tag_name'], value=tag['tag_name'])
            for tag in tags[:5]
        ]
        return choices
    @app_commands.command(name="list", description="displays all tags")
    async def tag_list(self, interaction: discord.Interaction):
        async with aiomysql.create_pool(
            host="161.97.78.70",
            port=3306,
            user="u38240_JdAbZAvfxO",
            password="H2wzrrusqEf@Hj7slG1LuKF@",
            db="s38240_database",
            charset='utf8mb4',
            cursorclass=aiomysql.DictCursor
        ) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        "SELECT tag_name FROM tags WHERE guild_id = %s",
                        (interaction.guild.id,)
                    )
                    found_tags = await cursor.fetchall()
        if not found_tags:
            embed_error_exis = discord.Embed(
                title="Error! 🚫",
                description="There are no tags available in this server.",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_exis)
            return
        embeds = []
        embed_limit = 10
        for i in range(0, len(found_tags), embed_limit):
            embed = discord.Embed(
                title=f"List of Tags (found: {len(found_tags)} tag(s))",
                description="\n".join(tag["tag_name"] for tag in found_tags[i:i + embed_limit]),
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.purple()
            )
            embed.set_footer(text="Page {}/{}".format((i // embed_limit) + 1, (len(found_tags) - 1) // embed_limit + 1 if len(found_tags) % embed_limit != 0 else len(found_tags) // embed_limit))
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
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_ownership, ephemeral=True)
                    return False
                return True
            async def on_timeout(self) -> None:
                await self.message.edit_original_response(view=button_view_timeout())
        view = ButtonView(interaction, interaction.user, embeds)
        await interaction.response.send_message(embed=embeds[0], view=view)
class afk_group_utillity(commands.GroupCog, group_name="afk", group_description="`afk` commands group"):
    def __init__(self, client):
        super().__init__()
        self.client = client
    @app_commands.command(name="set", description="Set your status to AFK")
    @app_commands.describe(message="Your AFK status")
    async def afk_set(self, interaction: discord.Interaction, message: str):
        conn = await aiomysql.connect(
            host="161.97.78.70",
            port=3306,
            user="u38240_JdAbZAvfxO",
            password="H2wzrrusqEf@Hj7slG1LuKF@",
            db="s38240_database",
            charset='utf8mb4',
            cursorclass=aiomysql.DictCursor
        )
        async with conn.cursor() as cursor:
            await cursor.execute('SELECT message FROM afk WHERE member_id = %s', (interaction.user.id,))
            result = await cursor.fetchone()
            if result:
                embed = discord.Embed(
                    title="Error! 🚫",
                    description=f"Your status is already set to afk.",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            if not result:
                await cursor.execute(
                    'REPLACE INTO afk (member_id, username, message, timestamp) VALUES (%s, %s, %s, %s)',
                    (interaction.user.id, interaction.user, message, datetime.datetime.utcnow().isoformat())
                )
                await conn.commit()
                embed = discord.Embed(
                    title="AFK",
                    description=f"Status changed to `AFK`.",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.purple()
                )
                embed.add_field(name="Message", value=message)
                await interaction.response.send_message(embed=embed)
                conn.close()
    @app_commands.command(name="remove", description="remove your AFK status")
    async def afk_remove(self, interaction: discord.Interaction):
        conn = await aiomysql.connect(
                host="161.97.78.70",
                port=3306,
                user="u38240_JdAbZAvfxO",
                password="H2wzrrusqEf@Hj7slG1LuKF@",
                db="s38240_database",
                charset='utf8mb4',
                cursorclass=aiomysql.DictCursor
            )
        async with conn.cursor() as cursor:
            await cursor.execute('SELECT message FROM afk WHERE member_id = %s', (interaction.user.id,))
            result = await cursor.fetchone()
            if result:
                afk_seconds = await calculate_afk_duration(interaction.user.id)
                await cursor.execute('DELETE FROM afk WHERE member_id = %s', (interaction.user.id,))
                await conn.commit()
                embed = discord.Embed(
                    title="Welcome back!",
                    description=f"Your `AFK` status has been `removed`. AFK message: {result['message']}, AFK time: {humanize.naturaldelta(datetime.timedelta(seconds=afk_seconds))}",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.purple()
                )
                await interaction.response.send_message(embed=embed)
            else:
                embed_error_exis = discord.Embed(
                    title="Error! 🚫",
                    description="❯ your status is not `afk`.",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed_error_exis, ephemeral=True)
async def setup(client):
    await client.add_cog(utility(client))
    await client.add_cog(embed_group_utillity(client))
    await client.add_cog(afk_group_utillity(client))
    await client.add_cog(tag_group_utillity(client))