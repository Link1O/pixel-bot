import discord
from discord import app_commands
from discord.ui import View
from discord.ext import commands
import aiomysql
import requests
import random
import datetime
import humanize
from typing import Literal
from utils.tools import *
married_members = {}
poster = None
KITSU_API_URL_ANIME = "https://kitsu.app/api/edge/anime"
def anime_fetcher(query):
    global poster
    params = {
        "filter[text]": query,
        "page[limit]": 1
    }
    response = requests.get(KITSU_API_URL_ANIME, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['data']:
            anime = data['data'][0]
            title = anime['attributes']['titles']['en_jp']
            synopsis = anime['attributes']['synopsis']
            poster = anime['attributes']['coverImage']['original']
            re_date = anime['attributes']['startDate']
            rating = anime['attributes']['averageRating']
            rating_rank = anime['attributes']['ratingRank']
            type = anime['attributes']['subtype']
            status = anime['attributes']['status']
            ep_count = anime['attributes']['episodeCount']
            ep_length = anime['attributes']['episodeLength']
            age_rating = anime['attributes']['ageRatingGuide']
            return f"❯ <:discotoolsxyzicon24:1173045855390019624> **Title:** {title}\n❯ <:discotoolsxyzicon22:1173045169042493530> **plot:** {synopsis}\n❯ <:discotoolsxyzicon25:1173046091407691836> **release date:** {re_date}\n❯ <:discotoolsxyzicon23:1173046297448685588> **genres:** {type}\n❯ <:discotoolsxyzicon26:1173046391745040445> **status:** {status}\n❯ <:discotoolsxyzicon29:1173047449800167516> **episode count:** {ep_count}\n❯ <:discotoolsxyzicon30:1173047581148979220> **episode length:** {ep_length}\n❯ <:discotoolsxyzicon31:1173047745758625962> **age rating:** {age_rating}\n❯ <:discotoolsxyzicon32:1173047889338048694> **Average Rating:** {rating}\n❯ <:discotoolsxyzicon33:1173048035123658903> **Rating Rank:** {rating_rank}"
        else:
            return "❌ No anime found for that query."
    else:
        return "❌ Error fetching data from Kitsu.io."
KITSU_API_URL_MANGA = "https://kitsu.io/api/edge/manga"
def manga_fetcher(query):
    global poster
    params = {
        "filter[text]": query,
        "page[limit]": 1
    }
    response = requests.get(KITSU_API_URL_MANGA, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['data']:
            manga = data['data'][0]
            title = manga['attributes']['titles']['en_jp']
            synopsis = manga['attributes']['synopsis']
            poster = manga['attributes']['coverImage']['original']
            re_date = manga['attributes']['startDate']
            rating = manga['attributes']['averageRating']
            rating_rank = manga['attributes']['ratingRank']
            type = manga['attributes']['subtype']
            status = manga['attributes']['status']
            chapter_count = manga['attributes']['chapterCount']
            volume_count = manga['attributes']['volumeCount']
            age_rating = manga['attributes']['ageRatingGuide']
            return f"❯ <:discotoolsxyzicon24:1173045855390019624> **Title:** {title}\n❯ <:discotoolsxyzicon22:1173045169042493530> **plot:** {synopsis}\n❯ <:discotoolsxyzicon25:1173046091407691836> **release date:** {re_date}\n❯ <:discotoolsxyzicon23:1173046297448685588> **genres:** {type}\n❯ <:discotoolsxyzicon26:1173046391745040445> **Status:** {status}\n❯ <:discotoolsxyzicon27:1173047324310765648> **Chapter Count:** {chapter_count}\n❯ <:discotoolsxyzicon28:1173047382708064367> **Volume Count:** {volume_count}\n❯ <:discotoolsxyzicon31:1173047745758625962> **Age Rating:** {age_rating}\n❯ <:discotoolsxyzicon32:1173047889338048694> **Average Rating:** {rating}\n❯ <:discotoolsxyzicon33:1173048035123658903> **Rating Rank:** {rating_rank}"
        else:
            return "❌ No manga found for that query."
    else:
        return "❌ Error fetching data from Kitsu.io."
class button_view_timeout(discord.ui.View):
    def __init__(self, timeout=60):
        super().__init__(timeout=timeout)
    @discord.ui.button(label="View timedout", style=discord.ButtonStyle.secondary, disabled=True)
    async def timeout_button(self):
        pass
class fun(commands.Cog):
    def __init__(self, client):
        self.client = client
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    @app_commands.command(name="kill", description="kills the chosen member")
    async def kill(self, interaction: discord.Interaction, member: discord.Member):
        if interaction.user.id is member.id:
            embed_error_author = discord.Embed(
                title="Error! 🚫",
                description="❯ you cannot kill your self",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.purple()
            )
            await interaction.response.send_message(embed=embed_error_author)
            return
        search_term = "anime kill"
        embed = discord.Embed(
            title=f"{interaction.user.display_name} has killed {member.display_name}",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        embed.set_image(url=await fetch_from_tenor(search_term))
        await interaction.response.send_message(embed=embed)
    @kill.error
    async def kill_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
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
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    @app_commands.command(name="punch", description="punches the chosen user")
    async def punch(self, interaction: discord.Interaction, member: discord.Member):
        if interaction.user.id is member.id:
            embed_error_author = discord.Embed(
                title="Error! 🚫",
                description="❯ you cannot punch your self",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.purple()
            )
            await interaction.response.send_message(embed=embed_error_author)
            return
        search_term = "anime punch"
        embed = discord.Embed(
            title=f"{interaction.user.display_name} has punched {member.display_name}",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        embed.set_image(url=await fetch_from_tenor(search_term))
        await interaction.response.send_message(embed=embed)
    @punch.error
    async def punch_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
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
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    @app_commands.command(name="slap", description="slaps the chosen member")
    async def slap(self, interaction: discord.Interaction, member: discord.Member):
        if interaction.user.id is member.id:
            embed_error_author = discord.Embed(
                title="Error! 🚫",
                description="❯ you cannot slap your self",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.purple()
            )
            await interaction.response.send_message(embed=embed_error_author)
            return
        search_term = "anime slap"
        embed = discord.Embed(
            title=f"{interaction.user.display_name} has slapped {member.display_name}",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        embed.set_image(url=await fetch_from_tenor(search_term))
        await interaction.response.send_message(embed=embed)
    @slap.error
    async def slap_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
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
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    @app_commands.command(name="marry", description="Marry the chosen member")
    async def marry(self, interaction: discord.Interaction, member: discord.Member):
        author = interaction.user
        if author.id == member.id:
            embed_error_self = discord.Embed(
                title="Error! 🚫",
                description="You can't marry yourself.",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_self, ephemeral=True)
            return
        if member.bot:
            embed_error_memberbot = discord.Embed(
                title="Error! 🚫",
                description="You can't marry a bot.",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_memberbot, ephemeral = True)
            return
        if author.id in married_members:
            embed_error_exis = discord.Embed(
                title="Error! 🚫",
                description="You are already married. You must divorce first.",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_exis, ephemeral=True)
            return
        if member.id in married_members:
            embed_error_softdec = discord.Embed(
                title="Error! 🚫",
                description="the chosen member is already married.",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_softdec, ephemeral=True)
            return
        if author.id in married_members.values():
            embed_error_mar = discord.Embed(
                title="Error! 🚫",
                description="You have already accepted a marriage proposal. You must divorce first.",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_mar, ephemeral=True)
            return
        embed_success = discord.Embed(
            title="success",
            description="purposed successfully",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed_success, ephemeral=True)
        embed_purposal = discord.Embed(
            title="proposal",
            description=f"{author.mention} wants to marry {member.mention}. React with <:discotoolsxyzicon37:1178763859071344701> to accept or <:discotoolsxyzicon38:1178763916914991164> to decline.",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        purposal_message = await interaction.channel.send(embed=embed_purposal)
        class ButtonView(View):
            def __init__(self, message, author, member, timeout=60):
                super().__init__(timeout=timeout)
                self.message = message
                self.author = author
                self.member = member
            @discord.ui.button(emoji="<:discotoolsxyzicon37:1178763859071344701>", style=discord.ButtonStyle.secondary)
            async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                married_members[author.id] = member.id
                married_members[member.id] = author.id
                embed_purposal = discord.Embed(
                    title="proposal",
                    description=f"{author.mention} wants to marry {member.mention}. React with <:discotoolsxyzicon37:1178763859071344701> to accept or <:discotoolsxyzicon38:1178763916914991164> to decline.",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.green()
                )
                search_term = "anime marry"
                embed = discord.Embed(
                    title=f"{self.author.display_name} has married {member.display_name}",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.purple()
                )
                embed.set_image(url=await fetch_from_tenor(search_term))
                for item in view.children:
                    item.disabled = True
                await self.message.edit(embed=embed_purposal, view=view)
                await interaction.response.send_message(embed=embed)
            @discord.ui.button(emoji="<:discotoolsxyzicon38:1178763916914991164>", style=discord.ButtonStyle.secondary)
            async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                embed_purposal = discord.Embed(
                    title="proposal",
                    description=f"{author.mention} wants to marry {member.mention}. React with <:discotoolsxyzicon37:1178763859071344701> to accept or <:discotoolsxyzicon38:1178763916914991164> to decline.",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.red()
                )
                search_term = "anime reject"
                embed_reject = discord.Embed(
                    title=f"{member.display_name} has rejected {self.author.display_name}",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.purple()
                )
                embed_reject.set_image(url=await fetch_from_tenor(search_term))
                for item in view.children:
                    item.disabled = True
                await self.message.edit(embed=embed_purposal, view=view)
                await interaction.response.send_message(embed=embed_reject)
            async def interaction_check(self, interaction: discord.Interaction):
                if interaction.user.id != self.member.id:
                    embed_ownership = discord.Embed(
                        title="Error! 🚫",
                        description="You cannot interact with this interaction.",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_ownership, ephemeral=True)
                    return False
                return True
            async def on_timeout(self) -> None:
                await self.message.edit(view=button_view_timeout())
        view = ButtonView(purposal_message, author, member)
        await purposal_message.edit(view=view)
    @marry.error
    async def marry_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
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
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    @app_commands.command(name="divorce", description="Divorce your spouse")
    async def divorce(self, interaction: discord.Interaction):
        author = interaction.user
        if author.id not in married_members:
            embed_error = discord.Embed(
                title="Error! 🚫",
                description="You are not married.",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error)
            return
        spouse_id = married_members[author.id]
        spouse = discord.utils.get(self.cliet.get_all_members(), id=spouse_id)
        del married_members[author.id]
        del married_members[spouse_id]
        search_term = "anime divorce"
        embed = discord.Embed(
            title="divorce",
            description=f"you are now divorced from {spouse.mention}",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        embed.set_image(url=await fetch_from_tenor(search_term))
        await interaction.response.send_message(embed=embed)
    @divorce.error
    async def divorce_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
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
    @app_commands.command(name="marriage_status", description="Check marriage status")
    async def marriage_status(self, interaction: discord.Interaction, member: discord.Member = None):
        author = interaction.user
        if not member:
            member = author
        if member.id not in married_members:
            embed_not_married = discord.Embed(
                title="Marriage Status",
                description = f"you are not married" if author.id == member.id else f"{member.mention} is not married.",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.purple()
            )
            await interaction.response.send_message(embed=embed_not_married)
        else:
            spouse_id = married_members[member.id]
            embed_married = discord.Embed(
                title="Marriage Status",
                description=f"you are married to <@{spouse_id}>" if author.id == member.id else f"{member.mention} is married to <@{spouse_id}>.",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.purple()
            )
            await interaction.response.send_message(embed=embed_married)
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    @app_commands.command(name="kiss", description="kisses the chosen user")
    async def kiss(self, interaction: discord.Interaction, member: discord.Member):
        if interaction.user.id is member.id:
            embed_error_author = discord.Embed(
                title="Error! 🚫",
                description="❯ you cannot kiss your self",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.purple()
            )
            await interaction.response.send_message(embed=embed_error_author)
            return
        search_term = "anime kiss"
        embed = discord.Embed(
            title=f"{interaction.user.display_name} has kissed {member.display_name}",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        embed.set_image(url=await fetch_from_tenor(search_term))
        await interaction.response.send_message(embed=embed)
    @kiss.error
    async def kiss_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
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
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    @app_commands.command(name="blush", description="blushs")
    async def blush(self, interaction: discord.Interaction):
        search_term = "anime blush"
        embed = discord.Embed(
            title=f"{interaction.user.display_name} is blushing",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        embed.set_image(url=await fetch_from_tenor(search_term))
        await interaction.response.send_message(embed=embed)
    @blush.error
    async def blush_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
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
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    @app_commands.command(name="waifu", description="displays a waifu image")
    async def waifu(self, interacion: discord.Interaction):
        embed = discord.Embed(
            title="waifu",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        embed.set_image(url=await fetch_waifu())
        await interacion.response.send_message(embed=embed)
    @waifu.error
    async def waifu_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
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
    @app_commands.checks.cooldown(1, 180, key=lambda i: (i.user.id))
    @app_commands.command(name="troll", description="trolls the chosen member using an set of fake moderation commands")
    async def troll(self, interaction: discord.Interaction, act:Literal["ban", "kick", "mute", "warn"], member: discord.Member, reason: str = None):
        if interaction.user is member:
            embed_error_author = discord.Embed(
                title="Error! 🚫",
                description="❯ you cannot troll your self.",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_author, ephemeral=True)
            return
        if member.bot:
            embed_error_bot = discord.Embed(
                title="Error! 🚫",
                description="❯ you cannot troll a bot.",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_bot, ephemeral=True)
            return
        if act.lower() == "ban":
            embed = discord.Embed(
                title="Member banned",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.purple()
            )
            embed.add_field(name="banned", value=f"❯ {member.mention}", inline=False)
            embed.set_footer(text=f"Moderator: {interaction.user.display_name} | this is a joke LOL!")
            if reason:
                embed.add_field(name="reason", value=f"❯ {reason}", inline=False)
            if not reason:
                embed.add_field(name="reason", value=f"❯ None", inline=False)
            await interaction.response.send_message(embed=embed)
            embed_dm = discord.Embed(
                title="you got banned",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.purple()
            )
            embed_dm.add_field(name="server", value=f"❯ {interaction.guild.name}", inline=False)
            embed_dm.add_field(name="Moderator", value=f"❯ {interaction.user.display_name}", inline=False)
            embed_dm.set_footer(text="get trolled XD!")
            if reason:
                embed_dm.add_field(name="reason", value=f"❯ {reason}", inline=False)
            if not reason:
                embed_dm.add_field(name="reason", value=f"❯ None", inline=False)
            try:
                await member.send(embed=embed_dm)
            except discord.Forbidden:
                embed_dm_error = discord.Embed(
                    title="Error! 🚫",
                    description="❯ Failed to send a DM to the member",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.orange()
                )
                await interaction.channel.send(embed=embed_dm_error)
        if act.lower() == "kick":
            embed = discord.Embed(
                title="Member kicked",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.purple()
            )
            embed.add_field(name="kicked", value=f"❯ {member.mention}", inline=False)
            embed.set_footer(text=f"Moderator: {interaction.user.display_name} | this is a joke LOL!")
            if reason:
                embed.add_field(name="reason", value=f"❯ {reason}", inline=False)
            if not reason:
                embed.add_field(name="reason", value=f"❯ None", inline=False)
            await interaction.response.send_message(embed=embed)
            embed_dm = discord.Embed(
                title="you got kicked",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.purple()
            )
            embed_dm.add_field(name="server", value=f"❯ {interaction.guild.name}", inline=False)
            embed_dm.add_field(name="Moderator", value=f"❯ {interaction.user.display_name}", inline=False)
            embed_dm.set_footer(text="get trolled XD!")
            if reason:
                embed_dm.add_field(name="reason", value=f"❯ {reason}", inline=False)
            if not reason:
                embed_dm.add_field(name="reason", value=f"❯ None", inline=False)
            try:
                await member.send(embed=embed_dm)
            except discord.Forbidden:
                embed_dm_error = discord.Embed(
                    title="Error! 🚫",
                    description="❯ Failed to send a DM to the member",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.orange()
                )
                await interaction.channel.send(embed=embed_dm_error)
        if act.lower() == "mute":
            embed = discord.Embed(
                title=f"member muted",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.purple()
            )
            embed.add_field(name="muted", value=f"❯ {member.mention}", inline=False)
            embed.add_field(name="Duration", value=f"❯ 1 hour")
            embed.set_footer(text=f"Moderator: {interaction.user.display_name} | this is a joke LOL!")
            if reason:
                embed.add_field(name="reason", value=f"❯ {reason}", inline=False)
            if not reason:
                embed.add_field(name="reason", value=f"❯ None", inline=False)
            embed_dm = discord.Embed(
                title="you got muted",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.purple()
            )
            embed_dm.add_field(name="server", value=f"❯ {interaction.guild.name}", inline=False)
            embed_dm.add_field(name="Moderator", value=f"❯ {interaction.user.display_name}", inline=False)
            embed_dm.add_field(name="duration", value=f"❯ 1 hour")
            embed_dm.set_footer(text="get trolled XD!")
            if reason:
                embed_dm.add_field(name="reason", value=f"❯ {reason}", inline=False)
            if not reason:
                embed_dm.add_field(name="reason", value=f"❯ None", inline=False)
            await interaction.response.send_message(embed=embed)
            try:
                await member.send(embed=embed_dm)
            except discord.Forbidden:
                embed_dm_error = discord.Embed(
                    title="Error! 🚫",
                    description="❯ Failed to send a DM to the member.",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.orange()
                )
                await interaction.channel.send(embed_dm_error)
        if act.lower() == "mute":
            embed = discord.Embed(
                title="member warned",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.purple()
            )
            embed.add_field(name="warned", value=f"❯ {member.mention}", inline=False)
            embed.set_footer(text=f"Moderator: {interaction.user.display_name} | this is a joke LOL!")
            if reason:
                embed.add_field(name="reason", value=f"❯ {reason}", inline=False)
            if not reason:
                embed.add_field(name="reason", value=f"❯ None", inline=False)
            embed_dm = discord.Embed(
                title="you got warned",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.purple()
            )
            embed_dm.add_field(name="server", value=f"❯ {interaction.guild.name}", inline=False)
            embed_dm.add_field(name="Moderator", value=f"❯ {interaction.user.display_name}", inline=False)
            embed_dm.set_footer(text="get trolled XD!")
            if reason:
                embed_dm.add_field(name="reason", value=f"❯ {reason}", inline=False)
            if not reason:
                embed_dm.add_field(name="reason", value=f"❯ None", inline=False)
            await interaction.response.send_message(embed=embed)    
            try:
                await member.send(embed=embed_dm)
            except discord.Forbidden:
                embed_dm_error = discord.Embed(
                    title="Error! 🚫",
                    description="❯ Failed to send a DM to the member.",
                    color=discord.Color.orange()
                )
                await interaction.channel.send(embed=embed_dm_error)
    @troll.error
    async def troll_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
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
    @app_commands.command(name="anime_search", description="Search and display basic information about the anime")
    async def anime_search(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        anime_info = anime_fetcher(query)
        embed = discord.Embed(
            title=f"🔍 Search Results for the provided search query",
            description=anime_info,
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        embed.set_image(url=poster)
        await interaction.followup.send(embed=embed)
    @anime_search.error
    async def anime_search_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
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
    @app_commands.command(name="manga_search", description="Search and display basic information about manga")
    async def manga_search(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        manga_info = manga_fetcher(query)
        embed = discord.Embed(
            title=f"🔍 Search Results for the provided search query",
            description=manga_info,
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        embed.set_image(url=poster)
        await interaction.followup.send(embed=embed)
    @manga_search.error
    async def manga_search_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
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
    @app_commands.command(name="idea", description="gives a random idea")
    async def idea(self, interaction: discord.Interaction):
        await interaction.response.send_message(await fetch_from_boredapi())
    @idea.error
    async def idea_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
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
class credit_group_fun(commands.GroupCog, group_name='credit', group_description='`credit` commands group'):
    def __init__(self, client):
        super().__init__()
        self.client = client
    @app_commands.command(name="balance", description="to display the credit balance.")
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None):
        if member:
            balance_member_text = "the chosen member balance is: "
        if not member:
            balance_member_text = "your balance is: "
        if not member:
            member = interaction.user
        async with aiomysql.connect(
            db=db,
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            charset=db_charset,
            cursorclass=aiomysql.DictCursor
        ) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT balance FROM economy WHERE user_id = %s", (member.id,))
                result = await cursor.fetchone()
                if not result:
                    await cursor.execute("INSERT INTO economy (user_id, balance) VALUES (%s, %s)", (member.id, 0))
                    await conn.commit()
                    result = (0,)
                balance = result['balance'] if isinstance(result, dict) else result[0]
                embed = discord.Embed(
                    title="balance",
                    description=f"{balance_member_text}{balance} credit's",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.purple()
                )
                await interaction.response.send_message(embed=embed)
    @app_commands.command(name="give", description="to give credit to the chosen member.")
    async def give(self, interaction: discord.Interaction, amount: int, member: discord.Member):
        if interaction.user.id == member.id:
            embed_error_self = discord.Embed(
                title="Error! 🚫",
                description="❯ you cannot send credits to yourself.",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_self, ephemeral = True)
            return
        if member.bot:
            embed_error_bot = discord.Embed(
                title="Error! 🚫",
                description="❯ you cannot send credits to a bot.",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed_error_bot, ephemeral = True)
            return
        async with aiomysql.connect(
            db=db,
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            charset=db_charset,
            cursorclass=aiomysql.DictCursor
        ) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT balance FROM economy WHERE user_id = %s", (interaction.user.id,))
                author_balance = await cursor.fetchone()
                if not author_balance:
                    await cursor.execute("INSERT INTO economy (user_id, balance) VALUES (%s, %s)", (interaction.user.id, 0))
                    await conn.commit()
                author_balance = author_balance['balance'] if author_balance else 0
                if author_balance >= amount:
                    if amount < 100:
                        embed_error_low = discord.Embed(
                            title="Error! 🚫",
                            description="❯ cannot send less then 100 credits.",
                            timestamp=datetime.datetime.utcnow(),
                            color=discord.Color.orange()
                        )
                        await interaction.response.send_message(embed=embed_error_low, ephemeral = True)
                        return
                    await cursor.execute("SELECT * FROM economy WHERE user_id = %s", (member.id,))
                    target_result = await cursor.fetchone()
                    if not target_result:
                        await cursor.execute("INSERT INTO economy (user_id, balance) VALUES (%s, %s)", (member.id, 0))
                        await conn.commit()
                    await cursor.execute("UPDATE economy SET balance = balance - %s WHERE user_id = %s", (amount, interaction.user.id))
                    await cursor.execute("UPDATE economy SET balance = balance + %s WHERE user_id = %s", (amount, member.id))
                    await conn.commit()
                    embed = discord.Embed(
                        title="credit's given",
                        description=f"{amount} credit's has been given to {member.mention}.",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.purple()
                    )
                    await interaction.response.send_message(embed=embed)
                else:
                    embed_error_balance = discord.Embed(
                        title="Error! 🚫",
                        description="❯ low balance.",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=embed_error_balance, ephemeral = True)
    @app_commands.checks.cooldown(1, 36000, key=lambda i: (i.user.id))
    @app_commands.command(name="work", description="to earn credit.")
    async def work(self, interaction: discord.Interaction):
        async with aiomysql.connect(
            db=db,
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            charset=db_charset,
            cursorclass=aiomysql.DictCursor
        ) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT * FROM economy WHERE user_id = %s", (interaction.user.id,))
                result = await cursor.fetchone()
                if not result:
                    await cursor.execute("INSERT INTO economy (user_id, balance) VALUES (%s, %s)", (interaction.user.id, 0))
                    await conn.commit()
                    result = (interaction.user.id, 0)
                if random.random() < 0.05:
                    earnings = random.randint(650, 750)
                    boss_gift = True
                else:
                    earnings = random.randint(250, 350)
                    boss_gift = False
                await cursor.execute("UPDATE economy SET balance = balance + %s WHERE user_id = %s", (earnings, interaction.user.id))
                await conn.commit()
                if boss_gift:
                    embed = discord.Embed(
                        title="Credits Earned",
                        description=f"Lucky you! Your boss was in a good mood and gave you {earnings} credits for your hard work!",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.purple()
                    )
                    await interaction.response.send_message(embed=embed)
                else:
                    embed = discord.Embed(
                        title="Credits Earned",
                        description=f"You earned {earnings} credits!",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.purple()
                    )
                    await interaction.response.send_message(embed=embed)
    @work.error
    async def work_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
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
async def setup(client):
    await client.add_cog(fun(client))
    await client.add_cog(credit_group_fun(client))