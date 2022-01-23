from discord.ext import commands

class events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        channel = guild.get_channel(862584503050567681)
        dir_role = guild.get_role(862078187521179678)
        man_role = guild.get_role(862077781180940328)
        if channel is not None:
            await channel.send(f'Welkom {member.mention}, de {dir_role.mention} of {man_role.mention} zal je zo spoedig mogelijk de rollen geven.')

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author == self.bot:
            return

        if ctx.content.startswith('hello'):
            await ctx.channel.send(f'Hello {ctx.author.mention}!')

def setup(bot):
    bot.add_cog(events(bot))