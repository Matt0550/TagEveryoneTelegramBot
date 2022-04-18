[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![GitHub issues](https://img.shields.io/github/issues/Matt0550/TagEveryoneTelegramBot)](https://github.com/Matt0550/TagEveryoneTelegramBot/issues)
[![GitHub repo size](https://img.shields.io/github/repo-size/Matt0550/TagEveryoneTelegramBot)](https://github.com/Matt0550/TagEveryoneTelegramBot/)
[![GitHub release (latest by date)](https://img.shields.io/github/downloads/Matt0550/TagEveryoneTelegramBot/total)](https://github.com/Matt0550/TagEveryoneTelegramBot/releases)
[![Discord](https://img.shields.io/discord/828990499507404820)](https://discord.gg/5WrVyQKWAr)

[![GitHub followers](https://img.shields.io/github/followers/Matt0550?style=social)](https://github.com/Matt0550?tab=followers)
[![GitHub watchers](https://img.shields.io/github/watchers/Matt0550/TagEveryoneTelegramBot?style=social)](https://github.com/Matt0550/TagEveryoneTelegramBot/watchers)
[![GitHub Repo stars](https://img.shields.io/github/stars/Matt0550/TagEveryoneTelegramBot?style=social)](https://github.com/Matt0550/TagEveryoneTelegramBot/stargazers)
# Tag Everyone Telegram Bot

This bot allows you to mention all users in a group. Users who wish to receive these notifications will have to sign up using the `/in` command
## Features

- `@everyone` or `@all` trigger `/everyone` command. (like Discord)
- The user decides whether to subscribe to the list with `/in`
- The user decides whether to exit to the list with `/out`
- All is saved to SQLite3 database.
- Hosted or self-hosted


## Commands
- `/in` - Add yourself to the Everyone's list
- `/out` - Remove yourself from the Everyone's list
- `/everyone` - Send a message to all in the list
- `/all` - Send a message to all in the list
- `/help` - Show help message

Instead of the command `/everyone` or `/all`, you can use `@everyone` or `@all`
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