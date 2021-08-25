import discord
import os
from discord.ext import commands
from discord.utils import get
from asyncio import TimeoutError
from keep_alive import keep_alive
import requests
import re
import random

intents = discord.Intents.default()
intents.members = True
intents.presences = True
client = commands.Bot(command_prefix = '^' , intents = intents)

# strings = ["Please vote for me at "]


def fact_stringer():
  url = "https://facts-by-api-ninjas.p.rapidapi.com/v1/facts"

  headers = {
    'x-rapidapi-host': "facts-by-api-ninjas.p.rapidapi.com",
    'x-rapidapi-key': "2987afc434msh7189050cea91ed1p17b589jsnd20984a50779"
    }

  response = requests.request("GET", url, headers=headers)

  # json_data = json.loads(response.text)

  unfinal_fact_text = re.sub("[{}']", "", response.text)

  idk_fact_text = unfinal_fact_text.replace("[", "")

  final_fact_text = idk_fact_text.replace("]", "")

  return final_fact_text

@client.event
async def on_ready():
    await client.change_presence(status = discord.Status.idle, activity = discord.Game('Helping Servers!'))
    print('Bot is ready')


@client.event
async def on_message(msg):
  
  if "lol" in msg.content:
    await msg.add_reaction("<:rounak:805663122098225163>")
  await client.process_commands(msg)

@client.event
async def on_command_error(ctx,error):
  if isinstance(error, commands.CommandOnCooldown):
    msg = "Still in cooldown, please try again in {:.2f}s".format(error.retry_after)

    await ctx.send(msg)

#CLEAR COMMAND

@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount : int):
  await ctx.channel.purge(limit = amount)

#KICK COMMAND

@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member : discord.Member, *, reason=None):
  guild = ctx.guild
  await member.kick(reason=reason)
  await ctx.send(f'Kicked {member.mention}')
  await member.send(f"You were kicked from {guild.name}")

#BAN COMMAND

@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member : discord.Member, *, reason=None):
  guild = ctx.guild
  await member.ban(reason=reason)
  await ctx.send(f'Banned {member.name}')
  await member.send(f"You were banned from {guild.name}")

#UNBAN COMMAND

@client.command()
async def unban(ctx,*, member):
  banned_users = await ctx.guild.bans()
  member_name, member_discriminator = member.split('#')

  for ban_entry in banned_users:
    user = ban_entry.user

    if(user.name, user.discriminator) == (member_name, member_discriminator):
      await ctx.guild.unban(user)
      await ctx.send(f'Unbanned {user.name}')
      
#MUTE COMMAND

# @client.command()
# # @commands.has_permissions(kick_members=)
# async def mute(ctx, member:discord.Member, * , reason=None):
#   guild = ctx.guild
#   mutedRole = discord.utils.get(guild.roles, name='muted')

#   if not mutedRole:
#     mutedRole = await guild.create_role(name='muted')

#     for channel in guild.channels:
#       await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history = False, read_message = False)

#   await member.add_roles(mutedRole, reason=reason)
#   await ctx.send(f'Muted {member.mention} for reason {reason}')
#   await member.send(f"You were muted in the server {guild.name} for {reason}")

#HELP COMMANDS
      
@client.command()
async def functions(ctx):
  embed = discord.Embed(title = 'Commands',
  description = 'All the Commands', color = 0xFF5733)

  embed.add_field(name = 'Commands', value='^kick , ^ban , ^clear , ^unban , ^functions , ^fact , ^spam, ^info , ^nick', inline = False)

  await ctx.send(embed = embed)
  return
  
#FACT COMMAND
@client.command()
async def fact(ctx):
  
  fact = fact_stringer()

  # await ctx.send(fact)


  embed = discord.Embed(title='Fact',description=fact, color = 0xFF5733)

  await ctx.send(embed=embed)

@client.command()
@commands.cooldown(1,600,commands.BucketType.user)
async def spam(ctx , str, * , amount: int):
  if(amount < 20):
    for i in range(amount):
      await ctx.send(str)
  else:
    await ctx.send("Dont spam")

@client.command()
async def info(ctx, member:discord.Member):

  embed = discord.Embed(title=f"{member.name}'s Info",description = "", color = 0x66f276)

  embed.add_field(name="Discord ID", value = f"{member.mention}", inline = True)

  embed.add_field(name="Top Role", value=f"{member.top_role}", inline = True)

  embed.add_field(name="Status", value=f"{member.status}", inline=False)

  embed.add_field(name="Activity", value=f"{member.activity}", inline = True)

  await ctx.send(embed=embed)

@client.command()
@commands.has_permissions(manage_nicknames=True)
async def nick(ctx, member:discord.Member, *, nickname: str):
  await member.edit(nick=nickname)
  await ctx.send(f"Name was changed to {member.mention}")

#ADD ROLE COMMAND

# @client.command()
# async def joke(ctx):
#   joke = joke_stringer()

#   print(joke)

  # embed = discord.Embed(title='Joke',description=joke, color = 0xD160E3)

  # await ctx.send(embed=embed)


#BUTTON 
# @client.command()
# async def button(ctx):
#   m = await ctx.send(
#     "Buttonghghg",
#     components=[[Button(style=1, label="HI"),Button(style=1,label="HI")]]
#   )

#   def check(res):
#     return ctx.author == res.user and res.channel==ctx.channel

#   try:
#     res = await client.wait_for('button_click', check=check, timeout = 5)

#     input = res.component.label

#   except TimeoutError:
#     await m.edit(
#       components=[]
#     )
  

keep_alive()
client.run(os.getenv('token'))
