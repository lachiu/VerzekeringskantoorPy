from discord.ext import commands

async def returnMember(ctx, input):
    member = await commands.MemberConverter().convert(ctx, input)
    return member

def checkReaction(ctx, reaction, user):
    return user == ctx.author and reaction.message.channel == ctx.channel

def checkMessage(ctx, m):
    return m.channel == ctx.channel and m.author == ctx.author

async def addReactions(message, addcross = False):
    await message.add_reaction('👍')
    await message.add_reaction('👎')
    
    if addcross:
        await message.add_reaction('❌')

def checkValue(type, value):
    goodValue = False
    if type == "isNumber" and isinstance(value, int):
        goodValue = True
    
        