# Discord Chicken Reward Bot
## Discord bot for sending a daily message of random tasks to a user. Written in python using [discord.py](https://discordpy.readthedocs.io/en/latest/). Uses the framework from [Hunter Sandlin's daily task message bot](https://github.com/HunterSandlin/DiscordDailyMessageBot) from which I adapted the daily messaging and bot setup. Thank you Hunter.

This bot is made to alert residents of the greater LA area of free food promotions based on teams scores or other sports achievements. The bot relies on [ESPN's publicly accessible API](https://gist.github.com/akeaswaran/b48b02f1c94f873c6655e7129910fc3b) to check scores and game status at a certain time each night. To reduce API calls, the bot runs a single score check once per night, defaulted to 10:10pm (Server time zone dependent).

The current promotions loaded to be checked are:
+ Anaheim Angels (Baseball)
     + [Chick-fil-a](https://www.mlb.com/angels/tickets/specials/homestand-partner-offers/chickfila) Free sandwich for scoring 7 or more runs
     + [Mountain Mike's Pizza](https://www.mountainmikespizza.com/wp-content/uploads/2024/04/2024_LAAngels_PromoTriggerLocations.pdf) Free pizza for pitching a shutout
+ LA Dodgers (Baseball)
     + [Panda Express](https://www.facebook.com/photo.php?fbid=1115398119944638&id=100044233819263&set=a.274827704001688) Discounted plate when the Dodgers win @home
+ Anaheim Ducks (Hockey)
     + [Chick-fil-a](https://www.nhl.com/ducks/fans/cfa-5goals-ana) Free sandwich for scoring 5 or more goals (May exclude IE, just LA & OC)
+ LAFC (Soccer)
     + [Chick-fil-a](https://www.cfasocal.com/promotion-details/winning-for-chicken) Free sandwich on LAFC home win


More promotions exist but are either not relevant to me (e.g. free small smoothie with purchase) or cannot be captured by the ESPN API (e.g. Clippers free-throw-based Chick-fil-a promo).

The bot works by adding it to a Discord server you own (or making a new one just for it) and running a python script locally or on a server. You set your defaults in the config file but can then changes options in memory by talking to the bot over the server with commands. 


# Set up
## Easiest: Docker Image
The easiest and fastest way to quickly set up this bot is using my [Docker Image](https://hub.docker.com/repository/docker/mattbarclay99/discordchickenmessagebot/general). Instructions on running a container are widely available including a tutorial from [Docker](https://docker-curriculum.com/).

### 1. Data Volume
On your server, create a directory named data and move your config.yaml (see step 3 below) and the chickenData.db files into it. When setting up the docker image, have a volume point to this data directory.

### 2. Run Docker container

## Manual installation
### 1. Install python3
This bot requies python 3.5.3 or newer. You can see if it is installed by opening a terminal or command prompt and typing 

``python --version`` 

if that does not work, try

``python3 --verion``

If neither of those work you will most likely have to [install python](https://www.python.org/downloads/). If your python is older than version 3.5.3 you will have to update python.

### 2. Install discord.py
Before you can use this bot you have to install discord.py. This bot is writen in discord.py Rewrite so be sure you are not using an older version. For an up to day installation guide, reference the offical [discord.py documentation](https://discordpy.readthedocs.io/en/latest/intro.html).

### 3. Set up bot on Discord
1. To set up the bot on the server, go to https://discord.com/developers/applications
There you will be asked to login to your Discord account. 

2. From there, select **New Application in the top right corner**, give it a name, and click **Create**.

3. On the server, go to the **Bot** tab on the side bar. On that screen click **Add Bot**.

4. You shold now have a bot created, scroll down to the card labeled **Bot Permissions**. The permissions you give is up to you but at a minimum you must include **Send Messages**, **Read Message History**, and **View Channels**. 

5. Scroll back up to the top and click **Copy** under the **Token**. This will copy the bot's token to your clipboard, which you will use in the next step.

It is also on this page where you can name the bot and give it a profile picture.

### 4. Set up Code
1. First [clone](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository) this repository. 

2. Rename `config.yaml.example` to `config.yaml`

3. On the first line of `config.yaml`, replace *YOUR_TOKEN_HERE* with your bot's token. It is important that you do not share this token with anyone or upload it online to ensure safety. Also replace the admin password text with your chosen admin password.

[*Step 4 is optional and can be done after bot is running*] 

4. Set the time in the same file under **messageTime**. It requires a 24-hour clock. If you wated 3:00pm, for example, you would set **hour** to *15* and **minutes** to *0*. Additionally, you can set it to not send messages on certain days by adding the day of the week in the **blacklistedDays** section. These days must be in quotations, seperated by commas, and spelled correctly, however capitalization is optional.

### 5. Run bot
To run the bot, simply run the python script. You can do this this by navigating to the directory in a terminal or command prompt and typying:

```python3 DailyMessageBot.py```

As long as the script is running, the bot will be active. I have deployed my script on a Raspberry Pi Zero 2W and it runs without hitting even 20% of the tiny CPU.

# Command List
You can use these commands to talk to the bot on it's server. All commands are prefaced with "-". 

  **help**   ---------- takes no arguments; responds with list of all commands.

  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ex. ```-help```

  **setMessageTime** ------- takes a time in 24 hour format; sets that time to be when messages will be sent each day. requires admin password as second input.

  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ex. ```-setMessageTime 23:15 password``` 

  **viewMessageTime** ------- takes no arguments; returns time that messages will be set each day.

  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ex. ```-viewMessageTime``` 

  **blockDays** ------- takes strings, must be a day of the week. Capitalization does not matter but spelling does; prevents message from being sent on those days. requires admin password as second input.

  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ex. ```-blockDays Tuesday Friday password``` 

  **unblockDays** ------- takes strings, must be a day of the week. Capitalization does not matter but spelling does; removes those days from the list of blocked days. requires admin password as second input.

  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ex. ```-blockDays Friday password``` 

  **viewBlockedDays** ------- takes no arguments; returns the days messages will not be sent.

  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ex. ```-viewMessageTime``` 

  **chickenToday** ------- takes no argument; runs an API query to see what rewards have been awarded today.

  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ex. ```-chickenToday``` 

  **chickenPossible** ------- takes no argument; runs an API query to see what rewards could be awarded today based on games scheduled.

  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ex. ```-chickenPossible``` 

  **chickenHistory** ------- takes numeric argument for number of days to look back, defaults to 30; runs an SQLite query to see what rewards have been awarded in the past X days.

  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ex. ```-chickenHistory 7``` 
  
  