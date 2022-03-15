from discord.ext import commands

class events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

async def setup(bot):
    await bot.add_cog(events(bot))