from discord.ext import commands
from cogs import EXTENSIONS


class SetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author)

    @commands.command()
    async def load(self, ctx, extension):
        await self.bot.load_extension(f'cogs.{extension}')
        await ctx.send(f'{extension} loaded!')

    @commands.command()
    async def unload(self, ctx, extension):
        await self.bot.unload_extension(f'cogs.{extension}')
        await ctx.send(f'{extension} unloaded!')

    @commands.command()
    async def reload(self, ctx, extension):
        try:
            await self.bot.reload_extension(f'cogs.{extension}')
        except commands.ExtensionNotLoaded:
            await self.load(ctx, extension)
            return
        await ctx.send(f'{extension} reloaded!')

    @commands.command()
    async def sync_tree(self, ctx):
        await self.bot.tree.sync()
        print('Sync successful')


class CustomBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def setup_hook(self):
        await self.add_cog(SetupCog(self))
        for extension in EXTENSIONS:
            if not extension.startswith('_'):  # If it starts with an underscore, don't load it by default
                await self.load_extension(f'cogs.{extension}')
