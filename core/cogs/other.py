import discord
from discord.ext import commands
from typing import Literal, Optional
import ast
import os
import datetime
from utils.tools import insert_returns, whitelist
image_url = str
class other(commands.Cog):
    def __init__(self, client):
        super().__init__()
        self.client = client
    @commands.command()
    @commands.guild_only()
    async def debug(self, ctx: commands.Context):
        embed = discord.Embed(
            title="debug command",
            description=f"❯ This command is used to debug the bot and check if everything is working fine. {whitelist}",
            timestamp=datetime.datetime.utcnow(),
            color=discord.Color.green()
        )
        await ctx.reply(embed=embed)
    @commands.command()
    @commands.guild_only()
    async def sync(self, ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        if ctx.author.id in whitelist:
            if not guilds:
                if spec == "~":
                    synced = await ctx.bot.tree.sync(guild=ctx.guild)
                elif spec == "*":
                    ctx.bot.tree.copy_global_to(guild=ctx.guild)
                    synced = await ctx.bot.tree.sync(guild=ctx.guild)
                elif spec == "^":
                    ctx.bot.tree.clear_commands(guild=ctx.guild)
                    await ctx.bot.tree.sync(guild=ctx.guild)
                    synced = []
                else:
                    synced = await ctx.bot.tree.sync()
                embed = discord.Embed(
                    title="synced successfully!",
                    description=f"❯ Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.purple()
                )
                await ctx.reply(embed=embed)
                return
            ret = 0
            for guild in guilds:
                try:
                    await ctx.bot.tree.sync(guild=guild)
                except discord.HTTPException:
                    pass
                else:
                    ret += 1
            embed = discord.Embed(
                title="synced successfully!",
                description=f"❯ Synced the tree to {ret}/{len(guilds)}.",
                timestamp=datetime.datetime.utcnow(),
                color=discord.Color.purple()
            )
            await ctx.reply(embed=embed)
        else:
            pass
    @commands.command(name='load_extension', aliases=['load'])
    async def load_extension(self, ctx: commands.Context, extension_name: str):
        if ctx.author.id in whitelist:
            extension_name = extension_name.lower()
            try:
                self.client.load_extension(extension_name)
                embed = discord.Embed(
                    title="Extension loaded successfully!",
                    description=f"❯ Extension: `{extension_name}` has been loaded.",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.purple()
                )
                await ctx.reply(embed=embed)
            except commands.ExtensionAlreadyLoaded:
                embed_error_already_loaded = discord.Embed(
                    title="Error! 🚫",
                    description=f"❯ Extension: `{extension_name}` is already loaded.",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.orange()
                )
                await ctx.reply(embed=embed_error_already_loaded)
            except commands.ExtensionNotFound:
                embed_error_not_found = discord.Embed(
                    title="Error! 🚫",
                    description=f"❯ Extension: `{extension_name}` not found.",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.orange()
                )
                await ctx.reply(embed=embed_error_not_found)
        else:
            pass
    @commands.command(name='unload_extension', aliases=['unload'])
    async def unload_extension(self, ctx: commands.Context, extension_name: str):
        if ctx.author.id in whitelist:
            extension_name = extension_name.lower()
            try:
                self.client.unload_extension(extension_name)
                embed = discord.Embed(
                    title="Extension unloaded successfully!",
                    description=f"❯ Extension: `{extension_name}` has been unloaded.",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.purple()
                )
                await ctx.reply(embed=embed)
            except commands.ExtensionNotLoaded:
                embed_error_not_loaded = discord.Embed(
                    title="Error! 🚫",
                    description=f"❯ Extension: `{extension_name}` is not loaded.",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.orange()
                )
                await ctx.reply(embed=embed_error_not_loaded)
            except commands.ExtensionNotFound:
                embed_error_not_found = discord.Embed(
                    title="Error! 🚫",
                    description=f"❯ Extension: `{extension_name}` not found.",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.orange()
                )
                await ctx.reply(embed=embed_error_not_found)
        else:
            pass
    @commands.command(name='reload_extension', aliases=['reload'])
    async def reload_extension(self, ctx: commands.Context, extension_name: str):
        if ctx.author.id in whitelist:
            extension_name = extension_name.lower()
            try:
                await self.client.reload_extension(extension_name)
                embed = discord.Embed(
                    title="extension reloaded successfully!",
                    description=f"❯ extension: `{extension_name}` has been reloaded.",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.purple()
                )
                await ctx.reply(embed=embed)
            except commands.ExtensionNotLoaded:
                embed_error_already_loaded = discord.Embed(
                    title="Error! 🚫",
                    description=f"❯ Extension: `{extension_name}` is not loaded.",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.orange()
                )
                await ctx.reply(embed=embed_error_already_loaded)
            except commands.ExtensionNotFound:
                embed_error_exis = discord.Embed(
                    title="Error! 🚫",
                    description=f"❯ extension: `{extension_name}` not found.",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.orange()
                )
                await ctx.reply(embed=embed_error_exis)
            except commands.ExtensionFailed:
                embed_error_fail = discord.Embed(
                    title="Error! 🚫",
                    description=f"❯ failed to reload extension: `{extension_name}`.",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.orange()
                )
                await ctx.reply(embed=embed_error_fail)
        else:
            pass
    @commands.command(name="reload_all_extensions", aliases=['reload_all'])
    async def reload_all_extensions(self, ctx: commands.Context):
        if ctx.author.id in whitelist:
            try:
                for filename in os.listdir(f'{global_path}/core/cogs'):
                    if filename.endswith('.py') and not filename.startswith('startup'):
                        await self.client.reload_extension(filename[:-3])
                        embed = discord.Embed(
                            title="extension reloaded successfully!",
                            description=f"❯ extension: `{filename}` has been reloaded.",
                            timestamp=datetime.datetime.utcnow(),
                            color=discord.Color.purple()
                        )
                        await ctx.reply(embed=embed)
            except commands.ExtensionNotLoaded:
                embed_error_already_loaded = discord.Embed(
                    title="Error! 🚫",
                    description=f"❯ Extension: `{filename}` is not loaded.",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.orange()
                )
                await ctx.reply(embed=embed_error_already_loaded)
            except commands.ExtensionFailed:
                embed_error_fail = discord.Embed(
                    title="Error! 🚫",
                    description=f"❯ failed to reload extension: `{filename}`.",
                    timestamp=datetime.datetime.utcnow(),
                    color=discord.Color.orange()
                )
                await ctx.reply(embed=embed_error_fail)
        else:
            pass
    @commands.command(name="eval_code")
    async def eval_code(ctx, *, cmd):
        if ctx.author.id in whitelist:
            fn_name = "_eval_expr"
            cmd = cmd.strip("` ")
            cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
            body = f"async def {fn_name}():\n{cmd}"
            parsed = ast.parse(body)
            body = parsed.body[0].body
            insert_returns(body)
            env = {
                'bot': ctx.bot,
                'discord': discord,
                'commands': commands,
                'ctx': ctx,
                'import': __import__
            }
            exec(compile(parsed, filename="<ast>", mode="exec"), env)
            try:
                (await eval(f"{fn_name}()", env))
            except Exception as e:
                await ctx.send(e)
        else:
            pass
    @eval_code.error
    async def error(ctx,error):
        if isinstance(error , commands.MissingRequiredArgument):
            if ctx.author.id == 771556723105202236:
                embed = discord.Embed(title="Result" , description="undefinded")
                await ctx.reply(embed=embed)
async def setup(client):
    await client.add_cog(other(client))