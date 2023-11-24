<img src="./gui/static/images/logo.png" width="100" style="border-radius: 15px; display: block; margin-left: auto; margin-right: auto; margin-bottom: 20px">


[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![GitHub issues](https://img.shields.io/github/issues/Matt0550/TagEveryoneTelegramBot)](https://github.com/Matt0550/TagEveryoneTelegramBot/issues)
[![Discord](https://img.shields.io/discord/828990499507404820)](https://discord.gg/5WrVyQKWAr)

# Tag Everyone Telegram Bot

This bot allows you to **mention all users in a group**. Users who wish to receive these notifications will have to sign up using the `/in` command

## Live demo
You can try the bot on Telegram: https://t.me/Tag_Everyone_TheBot

_This instance can be instable._

## Features

- `@everyone` or `@all` trigger `/everyone` command. (like Discord)
- The user decides whether to subscribe to the list with `/in`
- The user decides whether to exit to the list with `/out`
- All is saved to SQLite3 database
- Hosted or self-hosted


## Commands
- `/in` - Add yourself to the Everyone's list
- `/out` - Remove yourself from the Everyone's list
- `/everyone` - Send a message to all in the list
- `/all` - Send a message to all in the list
- `/help` - Show help message
- `/status` - Show the bot status and uptime
- `/stats` - NEW, Show the bot stats
- `/announce text` - NEW, Send a message to all groups
- `/list` - Show the Everyone's list without mention

Instead of the command `/everyone` or `/all`, you can use `@everyone` or `@all`

## Changelog
#### VERSION 1.3
- Redesigned database
- New commands
- Optimizations

## TO-DO
- [ ] REST API
- [ ] GUI
- [ ] Ignore tag requests if time enlapsed is > 2min
- [ ] Automatically add all members' group to Everyone's list

## Help - feedback
You can contact me on:

Discord: https://discord.gg/5WrVyQKWAr

Telegram: https://t.me/Non_Sono_matteo

Mail: <a href="mailto:mail@matt05.it">mail@matt05.it</a>

## Installation - Self-Host

Clone the project

```bash
  git clone https://github.com/Matt0550/TagEveryoneTelegramBot
```

Go to the project directory

```bash
  cd TagEveryoneTelegramBot-master
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Start the bot

```bash
  python main.py
```

## Installation - Using Docker

Install [Docker](https://www.docker.com)

Clone the project
```bash
  git clone https://github.com/Matt0550/TagEveryoneTelegramBot
```

Set `bot token` and `owner id` in docker-compose.yml

Now, open project folder in terminal and run
```bash
  docker-compose up -d
```


## Installation - Using Replit

Go to [replit.com](https://replit.com) and create new Python project

Clone the project to local directory
```bash
  git clone https://github.com/Matt0550/TagEveryoneTelegramBot
```

Move all file to replit project.

Now, click `Show hidden files` from the menu and open `.replit`

Set to `false` the `guessImports` option.

From the package manager, install `python-telegram-bot` and `flask`

From the *secrets manager* create new secrets with bot token

Open `main.py` and uncomment this line:
```python
import os
from keep_alive import keep_alive
...
...
keep_alive() # Replit hosting
```

Change the bot token with this:
```python
os.environ['token']
```

Now if you want 24/7 hosting, go to [Uptimerobot](https://uptimerobot.com/) and create a new monitor with the URL provided by Replit.
## License

[MIT](https://choosealicense.com/licenses/mit/)
