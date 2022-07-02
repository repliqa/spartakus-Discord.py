from discord.ext.commands import Bot
import discord
from discord import Embed
import random, os, json
from discord.ext.commands import CommandNotFound
from server import keep_alive
from googleapiclient.discovery import build
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import uuid

sns.set_style("whitegrid")
sns.set_palette("mako")

if not os.path.exists("Images"):
  os.mkdir("Images")
  
def getstacksearchresults(query):
  resource = build("customsearch", "v1", developerKey=os.environ["api_key"]).cse()
  out = resource.list(q=query, cx=os.environ['cse_key']).execute()
  items = out['items']
  embed = Embed(title=f"Results for \"{query}\"")
  for i in range(4):
    try:
      embed.add_field(name=items[i]['title'], value=items[i]['link'])
    except Exception:
      pass
  return embed

def get_problem(problems):
  randint = random.randint(0, len(problems))
  problem = problems[randint]
  title = problem[2]
  problem = problems[randint]
  link = f"https://codeforces.com/problemset/problem/{problem[0]}/{problem[1]}"
  return title, link

with open("problems.json", "r") as f:
  problems = json.loads(json.load(f))

client = Bot(command_prefix=">")
client.remove_command("help")

@client.command()
async def help(ctx):
  embed = Embed(title="spartaKus - BETA", description="A Discord bot made to assist programmers. Creator of the bot: https://prmethus.github.io")
  embed.add_field(name=">help", value="Show the supported commands and bot info.")
  embed.add_field(name=">stacksearch", value="Get solution to your problem from StachOverflow. Uses Google Custom Search API. \nExample: >stacksearch OSError Python")
  embed.add_field(name=">algorithm", value="Uses Codeforces API to get Algorithmtic questions. Example: >algorithm medium\nSupported Difficulties: [easy, medium, hard]")
  await ctx.send(content=ctx.author.mention, embed=embed)

@client.command()
async def algorithm(ctx, difficulty="easy"):
  difficulty = difficulty.strip().lower()

  if not difficulty in difficulties:
    await ctx.send(f"{ctx.author.mention} ERROR: Difficulty set to unknown value. The difficulties of the problems are: easy, medium, hard")
  else:
    title, link = get_problem(problems[difficulty])
    embed = Embed(title=title)
    embed.add_field(name="Difficulty", value=difficulty.capitalize())
    embed.add_field(name="URL", value=link)
    await ctx.send(content=ctx.author.mention, embed=embed)

@client.command()
async def stacksearch(ctx, *args):
  query = " ".join(args)
  embed = getstacksearchresults(query)
  await ctx.send(content=ctx.author.mention, embed=embed)

@client.command()
async def barplot(ctx, *args):
  try:
    dt = {}
    for arg in args:
      val = arg.split("=")
      dt[val[0]] = dt[val[1]]
    df = pd.DataFrame(dt)
    ax = sns.barplot(x=df.columns.tolist(), y=df.iloc[0])
    ax.bar_label(ax.containers[0])
    image_name = f"image{uuid.uuid1()}.png"
    image_path = os.path.join("Images", image_name)
    plt.savefig(image_path)
    image_file = discord.File(image_path, filename="barplot.png")
    await ctx.send(content=ctx.author.mention, file=image_file)
    os.remove(image_file)
  except Exception as e:
    print(e)
    await ctx.send("ERROR: An exception occured.\nIs the data you entered valid?")
  
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        pass

@client.event
async def on_ready():
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='>help'))

keep_alive()
client.run(os.environ["TOKEN"])