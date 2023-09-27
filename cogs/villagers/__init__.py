from .villagers import Villagers


async def setup(bot):
    await bot.add_cog(Villagers(bot))
