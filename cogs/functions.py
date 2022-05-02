from discord.ext import commands

async def returnMember(ctx, input):
    member = await commands.MemberConverter().convert(ctx, input)
    return member

async def addReactions(message, list):
    try:
        for item in list:
            await message.add_reaction(item)
    except:
        pass

def checkValue(type, value):
    goodValue = False
    if type == "isNumber" and isinstance(value, int):
        goodValue = True
    
    return goodValue