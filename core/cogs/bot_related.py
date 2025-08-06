from typing import Optional
import discord
from discord import app_commands
from discord.ui import View, Button
from discord.ext import commands
import datetime
import humanize
import aiomysql
from startup import startup_time
from utils.tools import *
pixel_art_help_menu = [
    "https://media1.giphy.com/media/ckr4W2ppxPBeIF8dx4/giphy.gif?cid=ecf05e47aq0yh7co5n83nb3qwr4jn4j8j0nmwirw2ud3v8xe&ep=v1_gifs_search&rid=giphy.gif&ct=g",
    "https://media3.giphy.com/media/RgZFvGuI4OxLjuSvRF/giphy.gif?cid=ecf05e47aq0yh7co5n83nb3qwr4jn4j8j0nmwirw2ud3v8xe&ep=v1_gifs_search&rid=giphy.gif&ct=g",
    "https://media3.giphy.com/media/gH1jGsCnQBiFHWMFzh/giphy.gif?cid=ecf05e47h3gb0xp6x80whdrl6a07bhn6av5t70tydmgexxi8&ep=v1_gifs_related&rid=giphy.gif&ct=g",
    "https://media4.giphy.com/media/NKEt9elQ5cR68/giphy.gif?cid=ecf05e474tls03go1x3k64epta36c4yl4y3rop33eksfcust&ep=v1_gifs_related&rid=giphy.gif&ct=g",
    "https://media1.giphy.com/media/9B7XwCQZRQfQs/giphy.gif?cid=ecf05e47y0fyl2eg6nupqpjy52cbuopssf7s47hwb85eaj68&ep=v1_gifs_related&rid=giphy.gif&ct=g"
]
class bot_related(commands.Cog):
    def __init__(self, client):
        super().__init__()
        self.client = client
    @app_commands.command(name="help", description="start here!")
    async def help(self, interaction):
        await interaction.response.defer()
        ws_latency = round(self.client.latency * 1000)
        start_time = datetime.datetime.now()
        async with interaction.channel.typing():
            end_time = datetime.datetime.now()
            rest_latency = (end_time - start_time).microseconds // 1000  
        start_time = datetime.datetime.now()
        conn = await aiomysql.connect(
            db=db,
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            charset=db_charset
        )
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT 1")
            await cursor.fetchall()
            conn.close()
        end_time = datetime.datetime.now()
        mysql_latency = (end_time - start_time).microseconds // 1000
        embed = discord.Embed(
            title="start here!",
            description="❯ select an `option` from the `menu` below to see the current added commands from each category.\n"
                        f"❯ <:discotoolsxyzicon7:1171142320549281844> **bot status:** {bot_status}\n"
                        f"❯ <:discotoolsxyzicon8:1171142621180211390> **host status:** {host_status}\n"
                        f"❯ <:discotoolsxyzicon9:1171143109401378836> **prefix:** /\n"
                        f"❯ <:discotoolsxyzicon10:1171143262258606180> **bot language:** python\n"
                        f"❯ <:discotoolsxyzicon11:1171143385868947487> **bot library:** discord.py\n"
                        f"❯ <:discotoolsxyzicon12:1171143595105996830> **open source status:** closed",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        random_pixelart_gif_url = random.choice(pixel_art_help_menu)
        embed.set_image(url=random_pixelart_gif_url)
        class Select(discord.ui.Select):
            def __init__(self):
                options=[
                    discord.SelectOption(label="utillity",emoji="<:discotoolsxyzicon15:1171140247912984606> ",description="utillity commands!"),
                    discord.SelectOption(label="moderation",emoji="<:discotoolsxyzicon:1171140408189915236>",description="moderation commands!"),
                    discord.SelectOption(label="auto-moderation", emoji="<:discotoolsxyzicon4:1171140962685296761>", description="auto-moderation commands!"),
                    discord.SelectOption(label="fun", emoji="<:discotoolsxyzicon5:1171141127139774474>", description="fun commands!"),
                    discord.SelectOption(label="bot related",emoji="<:discotoolsxyzicon6:1171141962720616529>", description="bot related commands!")
                    ]
                super().__init__(placeholder="Select a command category option",max_values=1,min_values=1,options=options)
            async def callback(self, interaction: discord.Interaction):
                if self.values[0] == "utillity":
                    embed = discord.Embed(
                        title="Here are the available utility commands!",
                        description="```/server_info``` - Shows basic information about the server.\n"
                                    "```/info``` `@member` - Shows basic information about the member.\n"
                                    "```/avatar``` `@member` - Shows the member's profile picture.\n"
                                    "```/roles``` `@member` - Displays the roles of a member.\n"
                                    "```/giveaway``` `prize` `time` - starts an giveaway for a certain duration of time.\n"
                                    "```/set welcomer_channel``` `channel` - sets the welcomer channel setting for the server.\n"
                                    "```/remove welcomer_channel``` - removes the welcomer channel setting for the server.\n"
                                    "```/set farweller_channel``` `channel` - sets the farweller channel setting for the server.\n"
                                    "```/remove_farweller_channel``` - removes the farweller channel setting for the server.\n"
                                    "```/set_suggestions_channel``` `channel` - sets the suggestion channel setting for the server.\n"
                                    "```/remove_suggestions_channel``` `channel` - sets the suggestion channel setting for the server.\n"
                                    "```/suggest``` `suggestion` -  sends a suggestion to the suggestion channel if set.\n"
                                    "```/embed create``` - creates an embed based on the member input.\n"
                                    "```/embed edit``` `embed_id` - edits the bot embed based on the member input.\n"
                                    "```/embed colors``` - shows an list of color pallets (hex colors).\n"
                                    "```/tag add``` `tag_name` `tag_content` `display_as_embed (on/off)` - adds a tag\n"
                                    "```/tag edit``` `tag_name` `new_content` `display_as_embed (on/off)` - edits the chosen tag\n"
                                    "```/tag remove``` `tag_name` - removes the chosen tag\n"
                                    "```/tag view``` `tag_name` - displays the chosen tag\n"
                                    "```/tag list``` - displays all the tags in the server\n"
                                    "```/afk set``` `message` - sets the status to afk.\n"
                                    "```/afk remove``` - removes the afk status.\n"
                                    "```/shorten_url``` `url` - shortens the provided url - cooldown: 10 seconds",
                        color=discord.Color.purple()
                    )
                    await msg.edit(embed=embed)
                elif self.values[0] == "moderation":
                    embed = discord.Embed(
                        title="here is the availble moderation commands!",
                        description="```/purge``` `amount` `channel` `member` - deletes an certain amount of messages based on the user input.\n"
                                    "```/set audit_log_channel``` `channel` - sets the audit log channel for the server.\n"
                                    "```/remove audit_log_channel``` - removes the audit log channel setting for the server.\n"
                                    "```/set mod_log_channel``` `channel` - sets the mod log channel setting for the server.\n"
                                    "```/remove mod_log_channel``` - removes the mod log channel setting for the server.\n"
                                    "```/snipe``` displays the last deleted message.\n"
                                    "```/lock``` `channel` - locks the channel.\n"
                                    "```/unlock``` `channel` `duration` - unlocks the channel.\n"
                                    "```/lock_vc``` `channel` `duration` - locks the voice channel.\n"
                                    "```/unlock_vc``` `channel` `duration` - unlocks the voice channel channel.\n"
                                    "```/kick``` `@member` `reason` - Kicks the specified member.\n"
                                    "```/ban``` `@member` `reason` - Bans the specified member.\n"
                                    "```/unban``` `member id` - unbans the specified member.\n"
                                    "```/mute``` `duration` `reason` - Mutes the specified member for a certain duration of time.\n"
                                    "```/unmute``` `@member` - Unmutes the specified member.\n"
                                    "```/mute_list``` - displays all the muted members.\n"
                                    "```/role``` `role name` `@member` - Assigns a role to a member.\n"
                                    "```/unrole``` `role name` `@member` - unassign a role from a member.\n"
                                    "```/warn``` `@member` `reason` - Warns a member.\n"
                                    "```/warnings``` `@member` - Displays warnings for a member.\n"
                                    "```/unwarn``` `warning id` - removes the warning with the ID provided from the database\n"
                                    "```/clear_warnings``` `@member` - clears all the member warnings.",
                        timestamp=datetime.datetime.utcnow(),            
                        color=discord.Color.purple()
                    )  
                    await msg.edit(embed=embed)
                elif self.values[0] == "auto-moderation":
                    embed = discord.Embed(
                        title="here is the availble auto-moderation commands!",
                        description="```/chat_filter``` `on/off` (the chat filter function is turned off by default) - turns on and off the chat filter feature. (note 💡: enabling this feature will result in filtering the suggestions)\n"
                                    "```/anti_spam``` `on/off` (the anti spam function is turned off by default) - turns on and off the anti spam feature. (note 💡: enabling this feature will result in filtering the suggestions)\n"
                                    "```/anti_link``` `on/off` (the anti link function is turned off by default) - turns on and off the anti link feature. ()",
                        timestamp=datetime.datetime.utcnow(),            
                        color=discord.Color.purple()
                    ) 
                    await msg.edit(embed=embed)
                elif self.values[0] == "fun":
                    embed = discord.Embed(
                        title="here is the availble fun commands!",
                        description="```/kill``` `@member` - kills the chosen member. - cooldown: 5 seconds.\n"
                                    "```/slap``` `@member` - slaps the chosen member. - cooldown: 5 seconds.\n"
                                    "```/marry``` `@member` - marries the chosen member. - cooldown: 5 seconds.\n"
                                    "```/marriage_status``` `@member` - check the marriage status for the chosen member.\n"
                                    "```/divorce``` - divorces your spouse. - cooldown: 5 seconds.\n"
                                    "```/kiss``` `@member` - kisses the chosen member. - cooldown: 5 seconds.\n"
                                    "```/blush``` - to blush. - cooldown: 5 seconds.\n"
                                    "```/troll``` `act` `@member` `reason` - trolls the chosen member based on the inputted act - cooldown: 3 minutes.\n"
                                    "```/bored``` - gives you a random thing to do - cooldown: 5 seconds.\n"
                                    "```/credit balance``` `@member` - checks the credit balance for the chosen user\n"
                                    "```/credit give``` `@member` - gives the credit's.\n"
                                    "```/credit work``` - to earn credit - cooldown: 10 hours.\n"
                                    "```/anime_search``` `query` - provides an basic information about the inputted anime - cooldown: 5 seconds.\n"
                                    "```/manga_search``` `query` - provides an basic information about the inputted manga - cooldown: 5 seconds.",
                        timestamp=datetime.datetime.utcnow(),
                        color=discord.Color.purple()
                    )
                    await msg.edit(embed=embed)
                elif self.values[0] == "bot related":
                    embed = discord.Embed(
                        title="here is the availble bot related commands!",
                        description="```/help``` - to view the bot commands."
                                    "```/documentation``` `the command` - provides an usage explanation for the provided command"
                                    "```/feedback``` `your feedback or suggestion` - sends the provided feedback to the bot owner (this command can only be used every 12 hours to avoid spam messages).\n"
                                    "```/server_count``` Displays the number of servers the bot is in.\n"
                                    "```/server_leaderboard``` Displays a leaderboard of servers by member count.\n"
                                    "```/invite``` For getting the bot invite link.\n"
                                    "```/support``` For getting the bot support server link.\n"
                                    "```/uptime``` - Displays the bot uptime.\n"
                                    "```/ping``` - Shows the bot latency.\n"
                                    "```/terms_of_use``` = to view the bots terms of use.\n"
                                    "```/privacy_policy``` to view the bots privacy policy.",
                        timestamp=datetime.datetime.utcnow(),            
                        color=discord.Color.purple()
                    )
                    await msg.edit(embed=embed)
        class totalView(discord.ui.View):
            def __init__(self, message, author, timeout = 60):
                super().__init__(timeout=timeout)
                self.message = message
                self.author = author
                self.add_item(Select())
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
        button = Button(label=f"Websocket Latency: {ws_latency}ms", style=discord.ButtonStyle.grey, disabled=True)
        button2 = Button(label=f"API latency: {rest_latency}ms", style=discord.ButtonStyle.grey, disabled=True)
        button3 = Button(label=f"MySQL database latency: {mysql_latency}ms", style=discord.ButtonStyle.grey, disabled=True)
        button4 = Button(label=f"shards: {shards}", style=discord.ButtonStyle.grey, disabled=True)
        view = totalView(interaction, interaction.user)
        view.add_item(button)
        view.add_item(button2)
        view.add_item(button3)
        view.add_item(button4)
        msg = await interaction.followup.send(embed=embed, view=view)
    @app_commands.command(name="terms_of_use", description="the bot terms of use")
    async def terms_of_use(self, interaction):
        embed = discord.Embed(
            title="Terms of Use for Pixel",
            description="By using our bot, you agree to the following terms:",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        embed.add_field(
            name="Respectful Interaction",
            value="❯ - Ensure your interactions are respectful and comply with community standards.",
            inline=False
        )
        embed.add_field(
            name="Service Availability",
            value="❯ - While we strive for reliability, there might be occasional service interruptions.",
            inline=False
        )
        embed.add_field(
            name="Use of Content",
            value="❯ - The content provided by Pixel team within the bot should not be used for commercial purposes without permission.",
            inline=False
        )
        embed.add_field(
            name="Limitation of Liability",
            value="❯ - Pixel team is not responsible for any damages resulting from the use of the bot.",
            inline=False
        )
        embed.add_field(
            name="Changes to Terms of Use",
            value="❯ - We reserve the right to update these terms. Your continued use implies acceptance of the updated terms.",
            inline=False
        )
        embed.add_field(
            name="Contact Us",
            value="❯ - Feel free to reach out to us in the official support server if you have any questions.",
            inline=False
        )
        embed.set_footer(text="Pixel Team")

        await interaction.response.send_message(embed=embed)
    @app_commands.command(name="privacy_policy", description="the bots privacy policy")
    async def privacy_policy(self, interaction):
        embed = discord.Embed(
            title="Privacy Policy for pixel",
            description="❯ At pixel team, we take your privacy seriously. This Privacy Policy is designed to help you understand how we collect, use, and safeguard your information. By using our bot and its services, you consent to the practices described in this policy.",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        embed.add_field(
            name="Information We Collect",
            value="pixel may collect and store the following information:\n"
                "❯ - User IDs: We may collect user IDs to provide certain services or to enhance your experience with the bot.\n"
                "❯ - Server IDs: We collect server IDs to offer server-specific features.\n"
                "❯ - Message Data: We may temporarily collect message data to facilitate certain bot features.\n"
                "❯ - Feedback: If you provide feedback or suggestions to the bot, we may store this information for the purpose of improving our services.",
            inline=False
        )
        embed.add_field(
            name="How We Use Your Information",
            value="pixel uses the collected information for the following purposes:\n"
                "❯ - Providing and maintaining bot services.\n"
                "❯ - Understanding and analyzing user interactions.\n"
                "❯ - Improving and enhancing bot functionality.\n"
                "❯ - Responding to user feedback and support requests.",
            inline=False
        )
        embed.add_field(
            name="Information Sharing",
            value="❯ in pixel team we do not share or sell your information to third parties.",
            inline=False
        )
        embed.add_field(
            name="Security",
            value="❯ We take the security of your data seriously and implement measures to protect it. However, no method of data transmission or storage is 100% secure. While we strive to protect your information, we cannot guarantee its absolute security.",
            inline=False
        )
        embed.add_field(
            name="Changes to this Privacy Policy",
            value="❯ We may update our Privacy Policy from time to time. Any changes will be posted on our discord support server. Your continued use of the bot after any changes indicates your acceptance of the revised Privacy Policy.",
            inline=False
        )
        embed.add_field(
            name="Contact Us",
            value="❯ Feel free to reach out to us in the official support server if you have any questions.",
            inline=False
        )
        embed.set_footer(text="pixel team.")
        
        await interaction.response.send_message(embed=embed)       
    @app_commands.checks.cooldown(1, 43200, key=lambda i: (i.user.id))
    @app_commands.command(name="feedback", description="sends an feedback to the bot team")
    async def feedback(self, interaction: discord.Interaction, feedback: str):
        feedback_channel_id = feedback_channel
        feedback_channel = self.client.get_channel(feedback_channel_id)
        author_id = interaction.user.id
        embed = discord.Embed(
            title="Feedback Sent Successfully",
            description="❯ Thanks for providing us with your feedback!",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        embed_channel = discord.Embed(
            title="Feedback",
            description="❯ Feedback received",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        embed_channel.add_field(name="Value", value=f"❯ {feedback}", inline=True)
        embed_channel.add_field(name="Server", value=f"❯ {interaction.guild}", inline=True)
        embed_channel.add_field(name="Sender", value=f"❯ <@{author_id}>[`{author_id}`]", inline=False)
        await feedback_channel.send(embed=embed_channel)
        await interaction.response.send_message(embed=embed)
    @feedback.error
    async def feedback_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
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
    @app_commands.command(name="invite", description="to invite the bot")
    async def invite(self, interaction):
        embed = discord.Embed(
            title="invite",
            description="❯ click the button below to invite the bot.",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        button = Button(label="link", style=discord.ButtonStyle.link, url='https://discord.com/api/oauth2/authorize?client_id=1155901354032758947&permissions=8&scope=bot')
        view = View()
        view.add_item(button)
        await interaction.response.send_message(embed=embed, view=view)
    @app_commands.command(name="support", description="to enter the support server")
    async def support(self, interaction): 
        embed = discord.Embed(
            title="invite",
            description="❯ click the button below to enter the support server.",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        button = Button(label="link", style=discord.ButtonStyle.link, url='https://discord.gg/aFf7TdJdFV')
        view = View()
        view.add_item(button)
        await interaction.response.send_message(embed=embed, view=view)
    @app_commands.command(name="ping", description="Shows the bot latency")
    async def ping(self, interaction = discord.Interaction):
        ws_latency = round(self.client.latency * 1000)
        start_time = datetime.datetime.now()
        async with interaction.channel.typing():
            end_time = datetime.datetime.now()
            api_latency = (end_time - start_time).microseconds // 1000
        start_time = datetime.datetime.now()
        conn = await aiomysql.connect(
            db=db,
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            charset=db_charset
        )
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT 1")
            await cursor.fetchall()
            conn.close()
        end_time = datetime.datetime.now()
        mysql_latency = (end_time - start_time).microseconds // 1000
        embed = discord.Embed(
            title="Pong! 🏓",
            description="❯ Latency Information",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        embed.add_field(name="Websocket Latency", value=f"❯ {ws_latency}ms", inline=True)
        embed.add_field(name="API Latency", value=f"❯ {api_latency}ms", inline=True)
        embed.add_field(name="MySQL database latency", value=f"{mysql_latency}ms", inline=False)
        await interaction.response.send_message(embed=embed)
    @app_commands.command(name="uptime", description="shows the bot uptime")
    async def uptime(self, interaction):
        current_time = datetime.datetime.now()
        uptime_duration = current_time - startup_time
        days, seconds = uptime_duration.days, uptime_duration.seconds
        hours, minutes = divmod(seconds, 3600)
        minutes, seconds = divmod(minutes, 60)
        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
        embed = discord.Embed(
            title="Bot Uptime",
            description=f"❯ The bot has been online for: {uptime_str}",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed)
    @app_commands.command(name="server_leaderboard", description="Displays a leaderboard of servers by member count.") 
    async def server_leaderboard(self, interaction):
        server_list = sorted(self.client.guilds, key=lambda x: len(x.members), reverse=True)
        leaderboard = []
        for index, server in enumerate(server_list[:10]):
            leaderboard.append(f"{index + 1}. {server.name} - {len(server.members)} members")
        leaderboard_text = "\n".join(leaderboard)
        embed = discord.Embed(
            title="Servers Leaderboard (by member count)",
            description=f"```\n{leaderboard_text}\n```",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed)   
    @app_commands.command(name="server_count", description="displays how much servers the bot is in")
    async def server_count(self, interacion):
        server_count = len(self.client.guilds)
        embed = discord.Embed(
            title="Server Count",
            description=f"❯ I am currently in {server_count} servers.",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.purple()
        )
        await interacion.response.send_message(embed=embed)
async def setup(client):
    await client.add_cog(bot_related(client))