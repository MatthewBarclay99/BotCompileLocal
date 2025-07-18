import discord
from discord.ext import commands
import yaml
from discord.ext import tasks as discordTasks
import requests
from datetime import datetime, time, timedelta
from collections import defaultdict
import sqlite3

with open('/data/config.yaml', 'r') as file:
    configFile = yaml.safe_load(file)
TOKEN = configFile['TOKEN'] 
password = configFile['password']
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
          'rewards':[
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
                    'reward_text':"$6 Panda Express plate! Use promo code 'DODGERSWIN'",
                    'reward_tag':'panda'}
                    ]
          }
Ducks = {'ID':"25",
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
def reset_rewardDict():
    global rewardDict
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

async def pwdCheck(ctx, pwd):
    if pwd == "":
        embed = discord.Embed(description = "Password required, please try again with password appended.")
        await ctx.send(embed = embed)
        return False
    elif str(pwd) != str(password):
        embed = discord.Embed(description = "Password incorrect, please try again with password appended.")
        await ctx.send(embed = embed)
        return False
    else: 
        return True


@client.command(
        help="see what rewards have been awarded today."
)
async def chickenToday(ctx, debugDate=None):
    rewards_text = printRewards(debugDate)
    embed = discord.Embed(description = rewards_text)
    await ctx.send(embed = embed)

@client.command(
        help="see what rewards could be awarded today based on games scheduled."
)
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

@client.command(
        help= "takes a time in 24 hour format; sets that time to be when messages will be sent each day. requires admin password as second input."
)
async def setMessageTime(ctx, newTime, pwd=""):
    if await pwdCheck(ctx, pwd):
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
        scheduled_times = generate_times(hours, minutes, local_tz)
        messageDaily.change_interval(time=scheduled_times)
        messageDaily.restart()
        embed = discord.Embed(description = ' -- Time set (will go into effect after the next scheduled message)')
        await ctx.send(embed = embed)
    


@client.command(
        help="time that messages will be set each day."
)
async def viewMessageTime(ctx):
    embed = discord.Embed(description = 'Time set is ' + messageDaily.next_iteration.strftime("%H:%M"))
    await ctx.send(embed = embed)

@client.command(
        help="takes strings, must be a day of the week. Capitalization does not matter but spelling does; prevents message from being sent on those days. requires admin password as second input."
)
async def blockDays(ctx, *days, pwd=""):
    if await pwdCheck(ctx, pwd):
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

@client.command(
        help="takes strings, must be a day of the week. Capitalization does not matter but spelling does; removes those days from the list of blocked days. requires admin password as second input."
)
async def unblockDays(ctx, *days, pwd=""):
    if await pwdCheck(ctx, pwd):
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

@client.command(
        help="returns the days messages will not be sent."
)
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

def sqliteQuery(daysAgo):
    try:
        sqliteConnection = sqlite3.connect('/data/chickenData.db')
        cursor = sqliteConnection.cursor()
        #print("Connected to SQLite")

        sqlite_select_with_param = """SELECT SUM(chicken),
SUM(panda),
SUM(pizza)
FROM (SELECT *
FROM chickenHistory
WHERE date > (SELECT DATETIME('now', '-' || ? || ' day'))) result;"""

        cursor.execute(sqlite_select_with_param, (daysAgo,))
        records = cursor.fetchone()
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to retrieve Python variable from sqlite table", error)
    
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #print("The SQLite connection is closed")
            return records

@client.command(
        help="takes numeric argument for number of days to look back, defaults to 30; runs an SQLite query to see what rewards have been awarded in the past X days."
)
async def chickenHistory(ctx, daysAgo=30):
    if not isinstance(daysAgo, int):
        embed = discord.Embed(description = 'Error: number of days must be an integer')
        await ctx.send(embed = embed)
        return
    records = sqliteQuery(daysAgo)
    historyText= "In the past "+str(daysAgo)+" days, the following rewards have been available:" + "\n" + str(records[0]) + "x Chicken" + "\n" + str(records[1]) + "x Panda" + "\n" + str(records[2]) + "x Pizza" 
    print(historyText)
    embed = discord.Embed(description = historyText)
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


# https://pynative.com/python-sqlite-insert-into-table/
def insertVaribleIntoTable(date, chicken, panda, pizza):
    try:
        sqliteConnection = sqlite3.connect('/data/chickenData.db')
        cursor = sqliteConnection.cursor()
        #print("Connected to SQLite")

        sqlite_insert_with_param = """INSERT INTO chickenHistory
                          (date, chicken, panda, pizza) 
                          VALUES (?, ?, ?, ?);"""

        data_tuple = (date, chicken, panda, pizza)
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        #print("Python Variables inserted successfully into SqliteDb_developers table")

        cursor.close()

    except sqlite3.Error as error:
        print("Failed to insert Python variable into sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #print("The SQLite connection is closed")



def get_league_scores_today(baseURL, date):
    request = requests.get(baseURL+date)
    return request.json().get('events')

def find_team_result(league_results, team_id):
    found = False
    team = ""
    opponent = ""
    for i, event_dict in enumerate(league_results):
        # Check each matchup one by one
        if(event_dict.get('season').get('slug')!="regular-season"):
            #checking if game is played during regular season (all teams should have same status)
            break
        for j, competition_dict in enumerate(event_dict.get('competitions')):
            #check each game one by one
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

def get_API(teamID, sport, debugDate=None):
    global baseURL
    API_URL = baseURL.get(sport)
    if debugDate is not None:
        today=str(debugDate)
    else:
        today = datetime.today().strftime('%Y%m%d')

    league_scores = get_league_scores_today(API_URL, today)
    return find_team_result(league_scores, teamID)

def printRewardsPossible():
    rewardCounter, reward_tags = searchRewardsPossible()
    rewards_text = ("There are " + str(rewardCounter) + " rewards possible today:")
    for key, value in reward_tags.items(): 
        rewards_text = rewards_text + "\n" + str(value) + "x " + key
    return rewards_text

def searchRewards(debugDate=None,popTeam=False):
    global rewardDict
    teams2keep = rewardDict.copy()
    todays_rewards = []
    rewardCounter=0
    reward_tags = defaultdict(int)
    for team in rewardDict:
        teamData, opponentData = get_API(team.get('ID'), team.get('sport'),debugDate)
        if(teamData==""):
            pass
        elif(teamData.get('incomplete')):
            pass
        else:
            for reward_i in team.get('rewards'):
                if(reward_i.get('rewardFUN')(teamData,reward_i.get('minScore'),opponentData)):
                    if(reward_i.get('homeReq') & bool(teamData.get('homeAway')!="home")):
                        pass
                    else:
                        todays_rewards.append(reward_i.get('reward_text'))
                        reward_tags[reward_i.get('reward_tag')]+=1
                        rewardCounter+=1
                        if popTeam:
                            teams2keep.remove(team)
    rewardDict = teams2keep
    return todays_rewards, rewardCounter, reward_tags

def searchRewardsPossible(debugDate=None):
    global rewardDict
    reward_tags = defaultdict(int)
    rewardCounter=0
    for team in rewardDict:
        teamData, opponentData = get_API(team.get('ID'), team.get('sport'), debugDate)
        if(teamData!=""):
            for reward_i in team.get('rewards'):
                if(reward_i.get('homeReq') & bool(teamData.get('homeAway')!="home")):
                    pass
                else:
                    reward_tags[reward_i.get('reward_tag')]+=1
                    rewardCounter+=1
    return rewardCounter, reward_tags
    
def printRewards(debugDate=None):
    rewards_text = ""
    todays_rewards, rewardCounter, dummy = searchRewards(debugDate)
    rewards_text = ("Today you have " + str(rewardCounter) + " rewards available to redeem:")
    for text in todays_rewards: 
        rewards_text = rewards_text + "\n" + text
    return rewards_text
   
async def setStatus(debugDate=None):
    dummy, reward_tags = searchRewardsPossible(debugDate)
    reward_tags=list(reward_tags.keys())
    if(len(reward_tags)==0):
        statusText = "No rewards"
    elif(len(reward_tags)==1):
        statusText = reward_tags[0]
    elif(len(reward_tags)==2):
        statusText = " and ".join(reward_tags)
    else:
        statusText = ", ".join(reward_tags[:-1]) + f", and {reward_tags[-1]}"
    statusText = statusText + " possible today"
    await client.change_presence(activity=discord.CustomActivity(name=statusText))
    


async def printRewardsasync():
    #Start debugging
    #for guild in client.guilds:
    #    for channel in guild.text_channels:
    #        if(channel.name == 'general'):
    #            if(guild.name == 'MattyB\'s server'):
    #                await channel.send(content = 'sending daily message...')
    #End debugging

    rewards_text = ""
    todays_rewards, rewardCounter, reward_tags = searchRewards(popTeam=True)
    for text in todays_rewards: 
        rewards_text = rewards_text + "\n" + text
    if(rewards_text!=""):
        await client.change_presence(activity=discord.CustomActivity(name="Winner winner chicken dinner"))
        insertVaribleIntoTable(datetime.today().strftime('%Y-%m-%d'),
                               reward_tags.get('chicken'),
                               reward_tags.get('panda'),
                               reward_tags.get('pizza'))
        rewards_text = "🚨🚨🚨" +"\n" + str(rewardCounter) + " rewards today:" + "\n" + rewards_text
        embed = discord.Embed(description = rewards_text)
        for guild in client.guilds:
            for channel in guild.text_channels:
                if(channel.name == 'general'):
                    await channel.send(embed = embed, delete_after=86399)
    else:
        await client.change_presence(activity=discord.CustomActivity(name="No rewards today :("))
        

#methods for getting suffix in date, ex "May 10th"
#decides what suffix to use
async def suffix(d):
        return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

#gets date and formats the string
async def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + await suffix(t.day))

#check multiple times from set start to midnight
def generate_times(hours, minutes, tzinfo):
    scheduled_times = []
    start_dt = datetime.now(tzinfo).replace(hour=hours, minute=minutes, second=0, microsecond=0)
    midnight = start_dt.replace(hour=0, minute=0) + timedelta(days=1)
    
    while start_dt < midnight:
        scheduled_times.append(start_dt.timetz())  # timetz includes tzinfo
        start_dt += timedelta(minutes=15)
    
    return scheduled_times

scheduled_times = generate_times(hours, minutes, local_tz)


#loop for sending message
@discordTasks.loop(time=scheduled_times)
async def messageDaily():
    global blacklistedDays
    if datetime.now().strftime('%A'). lower() not in blacklistedDays:
        await printRewardsasync()

#loop for setting possible rewards status after midnight     
@discordTasks.loop(time=time(hour=0,minute=1, tzinfo=local_tz))
async def setStatusDaily():
    await setStatus()
    reset_rewardDict()

#set a status on startup
@setStatusDaily.before_loop
async def startupStatusDaily():
    await setStatus()
    reset_rewardDict()



@client.listen()
async def on_ready():
    if not messageDaily.is_running():
        messageDaily.start()
    if not setStatusDaily.is_running():
        setStatusDaily.start()
    reset_rewardDict()
#run bot using token    
client.run(TOKEN)


