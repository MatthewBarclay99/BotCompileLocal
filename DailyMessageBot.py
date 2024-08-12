import discord
from discord.ext import commands
import yaml
from discord.ext import tasks as discordTasks
import requests
from datetime import datetime, time
from collections import defaultdict
import os

with open('config.yaml', 'r') as file:
    configFile = yaml.safe_load(file)
TOKEN = os.environ['TOKEN'] 
#tasks = configFile['tasks']
#connect to discord 
client = discord.Client(intents = discord.Intents.all())
#set command prefix
client = commands.Bot(command_prefix='-', intents = discord.Intents.all())
#users that will receive messages
#users = []
#numTasks = 2
hours = configFile['messageTime']['hour']
minutes = configFile['messageTime']['minutes']
blacklistedDays = [item.lower() for item in configFile['blacklistedDays']]
local_tz = datetime.now().astimezone().tzinfo

def scoreAtLeast(teamData,score, dummy):
    return int(teamData.get('score'))>=score

def winGame(teamData,dummy, dummy2):
    return bool(teamData.get('winner'))

def shutout(dummy, dummy2, oppData):
    return int(oppData.get('score'))==0

def save(teamData,dummy,dummy2):
    return int(teamData.get('statistics')[3].get('displayValue'))==1

baseURL = {'baseball':"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates=",
           'hockey':"https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard?dates=",
           'soccer':"https://site.api.espn.com/apis/site/v2/sports/soccer/usa.1/scoreboard?dates="}
cfa_text = "Free Chic-fil-a sandwich! Open the app before midnight."

Angels = {'ID':"3",
          'sport':"baseball",
          'rewards':[{'rewardFUN':scoreAtLeast,
                    'minScore':7,
                    'homeReq':True,
                    'reward_text':cfa_text,
                    'reward_tag':'chicken'},
                    {'rewardFUN':shutout,
                    'homeReq':False,
                    'reward_text':"Free 6in pizza from Mountain Mike's (w/ purchase)",
                    'reward_tag':'pizza'}
                    ]
          }
Dodgers = {'ID':"19",
           'sport':"baseball",
           'rewards':[{'rewardFUN':winGame,
                    'homeReq':True,
                    'reward_text':"$5 Panda Express plate! Use promo code 'DODGERSWIN'",
                    'reward_tag':'panda'}
                    ]
          }
Ducks =   {'ID':"25",
           'sport':"hockey",
         'rewards':[{'rewardFUN':scoreAtLeast,
                    'minScore':5,
                    'homeReq':True,
                    'reward_text':cfa_text,
                    'reward_tag':'chicken'}
                    ]
         }
LAFC = {'ID':"18966",
        'sport':"soccer",
        'rewards':[{'rewardFUN':winGame,
                    'homeReq':True,
                    'reward_text':cfa_text,
                    'reward_tag':'chicken'}
                    ]
        }
rewardDict = [Angels,Dodgers,Ducks,LAFC]

#--------Handles Events---------
@client.event
async def on_ready():
    print("Bot is ready.")    


#---------Handles Commands---------
# @client.command()
# async def ping(ctx):
#     embed = discord.Embed(description = "pong")
#     await ctx.send(embed = embed)

# @client.command()
# async def echo(ctx, *args):
#     output = ''
#     for word in args:
#         output += word + ' '
#     embed = discord.Embed(description = output)
#     await ctx.send(embed = embed)


@client.command()
async def chickenToday(ctx):
    rewards_text = printRewards()
    embed = discord.Embed(description = rewards_text)
    await ctx.send(embed = embed)

@client.command()
async def chickenPossible(ctx):
    rewards_text = printRewardsPossible()
    embed = discord.Embed(description = rewards_text)
    await ctx.send(embed = embed)

# @client.command()
# async def addUser(ctx, *newUsers):
#     if len(newUsers) == 0:
#         embed = discord.Embed(description = " -- Error: no users selects.")
#         await ctx.send(embed = embed)
#         return
#     for user in newUsers:
#         #remove extra parts of id, comes as <@!555>
#         user = user.replace("<@!","F")
#         user = user.replace(">","")
#         #get the user from the server and add to users array
#         user = ctx.message.guild.get_member(int(user))
#         users.append(user)
#     reply = " -- User added." if len(newUsers) == 1 else " -- Users added."
#     embed = discord.Embed(description = reply)
#     await ctx.send(embed = embed)

# @client.command()
# async def testTasks(ctx):
#     #if there are no users you cannot send tasks
#     if len(users) == 0:
#         embed = discord.Embed(description = " -- There are no users added.")
#         await ctx.send(embed = embed)
#         return
#     await dmTasks()
#     embed = discord.Embed(description = " -- DM's sent.")
#     await ctx.send(embed = embed)


# #sends each task in a list
# @client.command()
# async def viewTasks(ctx):
#     embed = discord.Embed(title = "All tasks")
#     #each list of items (each 'items' is an int from config)
#     for items in tasks:
#         allTasks = ''
#         #access each item in the array associated with that int if there are any there
#         if len(tasks[items]) > 0:
#             for eachOptions in tasks[items]:
#                 # add each option to string if they exist
#                 allTasks += '\t' + eachOptions + '\n'
#             embed.add_field(name=str(items), value=allTasks, inline=False)
#     await ctx.send(embed = embed)
    
    
# @client.command()
# async def setNumTasks(ctx, num):
#     global numTasks
#     numTasks = int(num)
#     embed = discord.Embed(description = " -- " +str(num) + " tasks will be send instead now.")
#     await ctx.send(embed = embed)

# @client.command()
# async def getUsers(ctx):
#     allUsers = ''
#     if len(users) == 0:
#         embed = discord.Embed(description = " -- There are currently no users.")
#         await ctx.send(embed = embed)
#         return
#     for user in users:
#         #remove extra parts of id, comes as <@!555>
#         allUsers += str(user) + "\n"
#     embed = discord.Embed(description = allUsers)
#     await ctx.send(embed = embed)

# @client.command()
# async def removeUser(ctx, *removeUsers):
#     if len(removeUsers) == 0:
#         embed = discord.Embed(description = " -- Error: no users selects.")
#         await ctx.send(embed = embed)
#         return
#     for user in removeUsers:
#         #remove extra parts of id, comes as <@!555>
#         user = user.replace("<@!","")
#         user = user.replace(">","")
#         #get the user from the server and remove from users array
#         user = ctx.message.guild.get_member(int(user))
#         users.remove(user)
#     reply = " -- User removed." if len(removeUsers) == 1 else " -- Users removed."
#     embed = discord.Embed(description = reply)
#     await ctx.send(embed = embed)

# @client.command()
# async def addTask(ctx, weight, newTask):
#     #validate input
#     if not weight.isnumeric:
#         embed = discord.Embed(description = "Error: first value must be an integer (qutations are not allowed)")
#         await ctx.send(embed = embed)
#         return
#     #see if the weight exists then add accordingly
#     global tasks
#     if int(weight) in tasks:
#         tasks[int(weight)].append(newTask)
#     else:
#         tasks[int(weight)] = [newTask]
#     embed = discord.Embed(description = "-- Task added.")
#     await ctx.send(embed = embed)

# @client.command()
# async def removeTask(ctx, removeTask):
#     #validate input
#     if (type(removeTask) != str):
#         embed = discord.Embed(description = 'Error: second value must be an string (ex. "Read book").')
#         await ctx.send(embed = embed)
#         return
#     global tasks
#     for weight in tasks:
#         if removeTask in tasks[weight]:
#             tasks[weight].remove(removeTask)
#             embed = discord.Embed(description = '-- Removed item from ' + str(weight) + ' weight class.')
#             await ctx.send(embed = embed)
#             return
#     embed = discord.Embed(description = 'Error: task does not exists')
#     await ctx.send(embed = embed)

@client.command()
async def setMessageTime(ctx, newTime):
    if not ":" in newTime:
        embed = discord.Embed(description = 'Error: time must be in hour:minutes and 24 hour format (ex. 20:35).')
        await ctx.send(embed = embed)
        return
    newHour = int(newTime.split(':')[0])
    newMinutes = int(newTime.split(':')[1])
    if newHour > 23 or newHour < 0:
        embed = discord.Embed(description = 'Error: invalid hour. Must be from 0 to 23')
        await ctx.send(embed = embed)
        return
    if newMinutes > 59 or newMinutes < 0:
        embed = discord.Embed(description = 'Error: invalid minutes. Must be from 0 to 59')
        await ctx.send(embed = embed)
        return
    global hours, minutes, configFile
    hours = newHour
    minutes = newMinutes
    configFile['messageTime']['hour'] = hours
    configFile['messageTime']['minutes'] = minutes
    with open('config.yaml', 'w') as file:
        yaml.dump(configFile, file, default_flow_style=False)
    messageDaily.change_interval(time=time(hour=hours,minute=minutes, tzinfo=local_tz))
    messageDaily.restart()
    embed = discord.Embed(description = ' -- Time set (will go into effect after the next scheduled message)')
    await ctx.send(embed = embed)
    


@client.command()
async def viewMessageTime(ctx):
    embed = discord.Embed(description = 'Time set is ' + messageDaily.next_iteration.strftime("%H:%M"))
    await ctx.send(embed = embed)

@client.command()
async def blockDays(ctx, *days):
    global blacklistedDays
    days = list(days)
    if len(days) < 1:
        embed = discord.Embed(description = "Error: no days were provided")
        await ctx.send(embed = embed)
        return
    possibleDays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    for day in days:
        if not day.lower() in possibleDays:
            embed = discord.Embed(description = "Error: " + str(day) + " is not a valid day. Nothing added.")
            await ctx.send(embed = embed)
            return
        if day.lower() in blacklistedDays:
            embed = discord.Embed(description = str(day) + " is already black listed. It will be ignored")
            await ctx.send(embed = embed)
            days.remove(day.lower())
            
    if len(days) < 1:
        embed = discord.Embed(description = "Nothing else to do.")
        await ctx.send(embed = embed)

    for item in days:
        blacklistedDays.append(item)
    message = " -- Days added to blacklist" if len(days) > 1 else " -- Day added to blacklist."
    embed = discord.Embed(description = message)
    await ctx.send(embed = embed)

@client.command()
async def unblockDays(ctx, *days):
    global blacklistedDays
    days = list(days)
    if len(days) < 1:
        embed = discord.Embed(description = "Error: no days were provided")
        await ctx.send(embed = embed)
        return
    possibleDays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    for day in days:
        if not day.lower() in possibleDays:
            embed = discord.Embed(description = "Error: " + str(day) + " is not a valid day. Nothing added.")
            await ctx.send(embed = embed)
            return
        if not day.lower() in blacklistedDays:
            embed = discord.Embed(description = str(day) + " is not black listed. It will be ignored")
            await ctx.send(embed = embed)
            days.remove(day.lower())
            
    if len(days) < 1:
        embed = discord.Embed(description = "Nothing else to do.")
        await ctx.send(embed = embed)

    for item in days:
        blacklistedDays.remove(item.lower())
    message = " -- Days removed from blacklist" if len(days) > 1 else " -- Day removed from blacklist."
    embed = discord.Embed(description = message)
    await ctx.send(embed = embed)

@client.command()
async def viewBlockedDays(ctx):
    global blacklistedDays
    message = "Days blocked:"
    i = len(blacklistedDays)
    for day in blacklistedDays:
        message += " " + day.capitalize()
        message += "," if i > 1 else "."
        i -= 1
    embed = discord.Embed(description = message)
    await ctx.send(embed = embed)


#---------General Functions---------
# #randomly selects 'numTasks' number of tasks from yaml file, weighted
# async def getRandomTasks():
#     hat = []
#     #each list of items (each 'items' is an int from config)
#     for items in tasks:
#         #access each item in the array associated with that int
#         for eachOptions in tasks[items]:
#             # add it to hat[] x = that int times
#             for _ in range(items):
#                 hat.append(eachOptions)
#     #randomly get distinct values from hat, numTasks is how many
#     picks = []
#     while (len(picks) < numTasks):
#         ranChoice = random.choice(hat)
#         if ranChoice not in picks:
#             picks.append(ranChoice)
#     return picks

# async def dmTasks():
#     todaysTasks = await getRandomTasks()
#     todaysDate = await custom_strftime('%A, %B {S}.', dt.now())
#     todaysMessage = "\n\nGoodmorning! Today is " + todaysDate + "\n" + "Here are your tasks for today!\n"
#     itemCount = 1
#     embed = discord.Embed(
#         title = 'Tasks for ' + todaysDate,
#         description = todaysMessage,
#         color = 1752220
#     )
#     # add feild for each task
#     for items in todaysTasks:
#         embed.add_field(name="Task " + str(itemCount) + " ", value=items, inline=False)
#         itemCount += 1
#     #send message to each user  
#     for user in users:
#         await user.create_dm()
#         await user.dm_channel.send(embed=embed)



def get_league_scores_today(baseURL, date):
    request = requests.get(baseURL+date)
    return request.json().get('events')

def find_team_result(league_results, team_id):
    found = False
    team = ""
    opponent = ""
    for i, event_dict in enumerate(league_results):
        for j, competition_dict in enumerate(event_dict.get('competitions')):
            for k, competitors_dict in enumerate(competition_dict.get('competitors')):
                if(competitors_dict.get('id')==team_id):
                    found=True
                    team=competitors_dict
                else:
                    opponent=competitors_dict
            if found:
                if not competition_dict.get('status').get('type').get('completed'):
                    team['incomplete'] = True
                    opponent['incomplete'] = True
                break
        if found:
            break
    return team, opponent

def get_API(teamID, sport):
    API_URL = baseURL.get(sport)
    today = datetime.today().strftime('%Y%m%d')
    league_scores = get_league_scores_today(API_URL, today)
    return find_team_result(league_scores, teamID)

def printRewardsPossible():
    rewards_text = ""
    todays_rewards = defaultdict(int)
    rewardCounter=0
    for team in rewardDict:
        teamData, opponentData = get_API(team.get('ID'), team.get('sport'))
        if(teamData!=""):
            for reward_i in team.get('rewards'):
                if(reward_i.get('homeReq') & bool(teamData.get('homeAway')!="home")):
                    break
                todays_rewards[reward_i.get('reward_tag')]+=1
                rewardCounter+=1
    rewards_text = ("There are " + str(rewardCounter) + " rewards possible today:")
    for key, value in todays_rewards.items(): 
        rewards_text = rewards_text + "\n" + str(value) + "x " + key
    return rewards_text


def printRewards():
    rewards_text = ""
    todays_rewards = []
    rewardCounter=0
    for team in rewardDict:
        teamData, opponentData = get_API(team.get('ID'), team.get('sport'))
        if(teamData==""):
            break
        elif(teamData.get('incomplete')):
            break
        else:
            for reward_i in team.get('rewards'):
                if(reward_i.get('rewardFUN')(teamData,reward_i.get('minScore'),opponentData)):
                    if(reward_i.get('homeReq') & bool(teamData.get('homeAway')!="home")):
                        break
                    todays_rewards.append(reward_i.get('reward_text'))
                    rewardCounter+=1
    rewards_text = ("Today you have " + str(rewardCounter) + " rewards available to redeem:")
    for text in todays_rewards: 
        rewards_text = rewards_text + "\n" + text
    return rewards_text
   

async def printRewardsasync():
    print('sending daily message...')
    rewards_text = ""
    todays_rewards = []
    rewardCounter=0
    for team in rewardDict:
        teamData, opponentData = get_API(team.get('ID'), team.get('sport'))
        if(teamData==""):
            break
        elif(teamData.get('incomplete')):
            break
        else:
            for reward_i in team.get('rewards'):
                if(reward_i.get('rewardFUN')(teamData,reward_i.get('minScore'),opponentData)):
                    if(reward_i.get('homeReq') & bool(teamData.get('homeAway')!="home")):
                        break
                    todays_rewards.append(reward_i.get('reward_text'))
                    rewardCounter+=1
    for text in todays_rewards: 
        rewards_text = rewards_text + "\n" + text
    if(rewards_text!=""):
        rewards_text = "🚨🚨🚨" +"\n" + str(rewardCounter) + " rewards today:" + "\n" + rewards_text
        embed = discord.Embed(description = rewards_text)
        #channel = discord.utils.get(client.get_all_channels(), name='general')
        #await channel.send(embed = embed)
        for guild in client.guilds:
            for channel in guild.channels:
                if(channel.name == 'general'):
                    await channel.send(embed = embed)

#methods for getting suffix in date, ex "May 10th"
#decides what suffix to use
async def suffix(d):
        return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

#gets date and formats the string
async def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + await suffix(t.day))

#loop for sending message
@discordTasks.loop(time=time(hour=hours,minute=minutes, tzinfo=local_tz))
async def messageDaily():
    global blacklistedDays
    if datetime.now().strftime('%A'). lower() not in blacklistedDays:
        await printRewardsasync()
        

#TODO: save to config file
#TODO: better help function

@client.listen()
async def on_ready():
    messageDaily.start()
#run bot using token    
client.run(TOKEN)


