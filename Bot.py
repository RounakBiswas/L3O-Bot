import discord
import os
import aiosqlite
import asyncio
import math
from discord.ext import commands
from keep_alive import keep_alive
import requests
import re
import random
from PIL import Image
from io import BytesIO


intents = discord.Intents.default()
intents.members = True
intents.presences = True
client = commands.Bot(command_prefix = '^' , intents = intents)
client.multiplier = 1

@client.event
async def on_message(message):
  if not message.author.bot:
    cursor = await client.db.execute("INSERT OR IGNORE INTO guildData (guild_id, user_id, exp) VALUES (?,?,?)",(message.guild.id, message.author.id, 1))

    if cursor.rowcount == 0:
      await client.db.execute("UPDATE guildData SET exp=exp + 1 WHERE guild_id = ? AND user_id = ?", (message.guild.id, message.author.id))

      cur = await client.db.execute("SELECT exp FROM guildData WHERE guild_id = ? AND user_id = ?", (message.guild.id, message.author.id))

      data = await cur.fetchone()
      exp = data[0]
      lvl = math.sqrt(exp) / client.multiplier

      if lvl.is_integer():
        await message.channel.send(f"{message.author.name} well done! You are now level: {int(lvl)}.")

    await client.db.commit()
  
  # await client.process_commands(message)

  if "lol" in message.content:  
    await message.add_reaction("<:rounak:805663122098225163>")
  await client.process_commands(message)

  
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

def satisfaction_calculator():
  satisfaction = random.randrange(1,100)
  return satisfaction

@client.event
async def on_ready():
  
    await client.wait_until_ready()
    client.db = await aiosqlite.connect("expData.db")
    await client.db.execute("CREATE TABLE IF NOT EXISTS guildData (guild_id int, user_id int , exp int, PRIMARY KEY (guild_id, user_id))")

    await client.change_presence(status = discord.Status.idle, activity = discord.Game('Helping Servers!'))
    print('Bot is ready')


@client.event
async def on_command_error(ctx,error):
  if isinstance(error, commands.CommandOnCooldown):
    msg = "Still in cooldown, please try again in {:.2f}s".format(error.retry_after)

    await ctx.send(msg)

#CLEAR COMMAND

@client.command(help = "This command clears unwanted messages.")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount : int):
  await ctx.channel.purge(limit = amount)

#KICK COMMAND

@client.command(help = "This command kicks users")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member : discord.Member, *, reason=None):
  guild = ctx.guild
  await member.kick(reason=reason)
  await ctx.send(f'Kicked {member.mention}')
  await member.send(f"You were kicked from {guild.name}")

#BAN COMMAND

@client.command(help = "This command bans users")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member : discord.Member, *, reason=None):
  guild = ctx.guild
  await member.ban(reason=reason)
  await ctx.send(f'Banned {member.name}')
  await member.send(f"You were banned from {guild.name}")

#UNBAN COMMAND

@client.command(help = 'This command unbans the banned users')
async def unban(ctx,*, member,):
  banned_users = await ctx.guild.bans()
  member_name, member_discriminator = member.split('#')

  for ban_entry in banned_users:
    user = ban_entry.user

    if(user.name, user.discriminator) == (member_name, member_discriminator):
      await ctx.guild.unban(user)
      await ctx.send(f'Unbanned {user.name}')
       

  
#FACT COMMAND
@client.command(help = "This command returns a random fact")
async def fact(ctx):
  
  fact = fact_stringer()

  # await ctx.send(fact)


  embed = discord.Embed(title='Fact',description=fact, color = 0xFF5733)

  await ctx.send(embed=embed)

@client.command(help = "This command spams a message")
@commands.cooldown(1,600,commands.BucketType.user)
async def spam(ctx , str, * , amount: int):
  if(amount < 20):
    for i in range(amount):
      await ctx.send(str)
  else:
    await ctx.send("Dont spam")

@client.command(help="This command returns the info of the mentioned user")
async def info(ctx, member:discord.Member):

  embed = discord.Embed(title=f"{member.name}'s Info",description = "", color = 0x66f276)

  embed.add_field(name="Discord ID", value = f"{member.mention}", inline = True)

  embed.add_field(name="Top Role", value=f"{member.top_role}", inline = True)

  embed.add_field(name="Status", value=f"{member.status}", inline=False)

  embed.add_field(name="Activity", value=f"{member.activity}", inline = True)

  await ctx.send(embed=embed)

@client.command(help = "This command changes the nickname of the mentioned user")
@commands.has_permissions(manage_nicknames=True)
async def nick(ctx, member:discord.Member, *, nickname: str):
  await member.edit(nick=nickname)
  await ctx.send(f"Name was changed to {member.mention}")

@client.command(help = "mentions two users in front of this command")
@commands.cooldown(1,60,commands.BucketType.user)
async def fuck(ctx, member1:discord.Member, member2:discord.Member):
  satis = satisfaction_calculator()
  await ctx.send(f"{member1.mention} fucked {member2.mention} and {member2.mention} was {satis}% satisfied")

@client.command(help = "This command returns a image of the user as a wanted poster")
async def wanted(ctx, user:discord.Member = None):
  if user == None:
    user = ctx.author

  wanted = Image.open("wanted.jpg")

  asset = user.avatar_url_as(size = 128)

  data = BytesIO(await asset.read())
  pfp = Image.open(data)

  pfp = pfp.resize((477,521))

  wanted.paste(pfp, (209,435))

  wanted.save("profile.jpg")

  await ctx.send(file = discord.File("profile.jpg"))

@client.command(help = "Check your level using this")
async def stats(ctx, member: discord.Member):


    # get user exp
  async with client.db.execute("SELECT exp FROM guildData WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, member.id)) as cursor:
        data = await cursor.fetchone()
        exp = data[0]

        # calculate rank
  async with client.db.execute("SELECT exp FROM guildData WHERE guild_id = ?", (ctx.guild.id,)) as cursor:
        rank = 1
        async for value in cursor:
            if exp < value[0]:
                rank += 1

  lvl = int(math.sqrt(exp)//client.multiplier)

  current_lvl_exp = (client.multiplier*(lvl))**4
  next_lvl_exp = (client.multiplier*((lvl+1)))**4

  lvl_percentage = ((exp-current_lvl_exp) / (next_lvl_exp-current_lvl_exp)) * 100

  embed = discord.Embed(title=f"Stats for {member.name}", colour=discord.Colour.gold())
  embed.add_field(name="Level", value=str(lvl))
  embed.add_field(name="Exp", value=f"{exp}/{next_lvl_exp}")
  embed.add_field(name="Rank", value=f"{rank}/{ctx.guild.member_count}")
  embed.add_field(name="Level Progress", value=f"{round(lvl_percentage, 2)}%")

  await ctx.send(embed=embed)

@client.command(help = "Shows the leaderboards for the current server of the xp")
async def leaderboard(ctx): 
    buttons = {}
    for i in range(1, 6):
        buttons[f"{i}\N{COMBINING ENCLOSING KEYCAP}"] = i # only show first 5 pages

    previous_page = 0
    current = 1
    index = 1
    entries_per_page = 10

    embed = discord.Embed(title=f"Leaderboard Page {current}", description="", colour=discord.Colour.gold())
    msg = await ctx.send(embed=embed)

    for button in buttons:
        await msg.add_reaction(button)

    while True:
        if current != previous_page:
            embed.title = f"Leaderboard Page {current}"
            embed.description = ""

            async with client.db.execute(f"SELECT user_id, exp FROM guildData WHERE guild_id = ? ORDER BY exp DESC LIMIT ? OFFSET ? ", (ctx.guild.id, entries_per_page, entries_per_page*(current-1),)) as cursor:
                index = entries_per_page*(current-1)

                async for entry in cursor:
                    index += 1
                    member_id, exp = entry
                    member = ctx.guild.get_member(member_id)
                    embed.description += f"{index}) {member.mention} : {exp}\n"

                await msg.edit(embed=embed)

        try:
            reaction, user = await client.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in buttons, timeout=60.0)

        except asyncio.TimeoutError:
            return await msg.clear_reactions()

        else:
            previous_page = current
            await msg.remove_reaction(reaction.emoji, ctx.author)
            current = buttons[reaction.emoji]


@client.command()
async def prefix(ctx , prefix: str):
  await ctx.send("Hello")  

keep_alive()
client.run(os.getenv('token'))
asyncio.run(client.db.close())
