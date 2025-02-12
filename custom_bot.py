from discord.ext import commands
import asyncpg
from cogs import EXTENSIONS
from helpers import get_pg_login, get_extension


class SetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author)

    @commands.command()
    async def load(self, ctx, extension):
        extension = get_extension(extension)  # Formats text in case of shorthand or returns None if not found
        if not extension:
            raise commands.ExtensionNotFound(extension)
        await self.bot.load_extension(f'cogs.{extension}')
        await ctx.message.delete()
        await ctx.send(f'{extension} loaded!', delete_after=5)

    @commands.command()
    async def unload(self, ctx, extension):
        extension = get_extension(extension)  # Formats text in case of shorthand or returns None if not found
        if not extension:
            raise commands.ExtensionNotFound(extension)
        await self.bot.unload_extension(f'cogs.{extension}')
        await ctx.message.delete()
        await ctx.send(f'{extension} unloaded!', delete_after=5)

    @commands.command()
    async def reload(self, ctx, extension):
        extension = get_extension(extension)  # Formats text in case of shorthand or returns None if not found
        if not extension:
            raise commands.ExtensionNotFound(extension)
        try:
            await self.bot.reload_extension(f'cogs.{extension}')
            await ctx.message.delete()
            await ctx.send(f'{extension} reloaded!', delete_after=5)
        except commands.ExtensionNotLoaded:
            await self.bot.load_extension(f'cogs.{extension}')
            await ctx.message.delete()
            await ctx.send(f'{extension} loaded!', delete_after=5)

    @commands.command()
    async def sync_tree(self, ctx):
        await self.bot.tree.sync()
        await ctx.send('Sync successful')

    @commands.command()
    async def testo(self, ctx):
        print(EXTENSIONS)


class CustomBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pg_pool = None

    async def setup_hook(self):
        # Connect to database
        pg_login = get_pg_login()
        self.pg_pool = await asyncpg.create_pool(**pg_login)
        print('Connection Pool created')

        # Load setup cog & all extensions
        await self.add_cog(SetupCog(self))
        for extension in EXTENSIONS:
            if not extension.startswith('_'):  # If it starts with an underscore, don't load it by default
                await self.load_extension(f'cogs.{extension}')

    async def close(self):
        await super().close()
        await self.pg_pool.close()
        print('Connection Pool closed')
        print('Bot shutdown')
