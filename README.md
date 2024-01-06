[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![Discord][discord-shield]][discord-url]
[![Docker Pulls][docker-shield]][docker-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/Matt0550/TagEveryoneTelegramBot">
    <img src="src/gui/static/images/logo.png" alt="Logo" width="100" height="100" style="border-radius: 15px;">
  </a>

  <h3 align="center">Tag Everyone Telegram BOT</h3>

  <p align="center">
    A Telegram bot to tag everyone in a group
    <br />
    <br />
    <a href="https://t.me/TagEveryone_TheBot">View Demo</a>
    ·
    <a href="https://github.com/Matt0550/TagEveryoneTelegramBot/issues">Report Bug</a>
    ·
    <a href="https://github.com/Matt0550/TagEveryoneTelegramBot/issues">Request Feature</a>
  </p>
</div>


# Tag Everyone Telegram Bot

This bot allows you to **mention all users in a group**. Users who wish to receive these notifications will have to sign up using the `/in` command.

## Live demo
You can try the bot on Telegram: https://t.me/Tag_Everyone_TheBot

_This instance can be instable._

## Features

- `@everyone` or `@all` trigger `/everyone` command. (like Discord)
- The user decides whether to subscribe to the list with `/in`
- The user decides whether to exit to the list with `/out`
- Telegram WebApp support
- All is saved to SQLite3 database
- Hosted or self-hosted
- Docker support


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
- WebApp

## TO-DO
- [ ] REST API
- [x] WebApp
- [ ] Ignore tag requests if time enlapsed is > 2min
- [ ] Automatically add all members' group to Everyone's list


## Installation - Using Docker Compose (recommended)
```yaml
version: '3'

services:
  tageveryone_telegrambot:
    image: matt0550/tageveryone_telegrambot
    environment:
      - token=BOT_TOKEN
      - owner_id=OWNER_ID
      - enable_webapp_server=True
      - webserver_debug=False
      - report_errors_owner=False
      - secret_key=SECRET_KEY
    volumes:
      - /path/to/database-new.db:/src/db/database-new.db
    ports:
      - 5000:5000
    restart: unless-stopped
```
Run the container with `docker-compose up -d`

## Installation - Using Docker Run
```bash
docker run -d \
  -e token=TG_BOT_TOKEN \
  -e owner_id=TG_OWNER_ID \
  -e enable_webapp_server=True \
  -e webserver_debug=False \
  -e report_errors_owner=False \
  -e secret_key=SECRET_KEY \
  -v /path/to/database-new.db:/src/db/database-new.db \
  -p 5000:5000 \
  --name tageveryone_telegrambot \
  matt0550/tageveryone_telegrambot
```

## Installation - Self-Host or docker build

Clone the project

```bash
  git clone https://github.com/Matt0550/TagEveryoneTelegramBot
```

Go to the project directory

```bash
  cd TagEveryoneTelegramBot-master
```

OPTIONAL: use docker to build the image

```bash
  docker build -t tageveryone_telegrambot .
```
If you don't want to use docker, skip this step.
Else, change the `image` in `docker-compose.yml` with the image name you used.
Run the container with `docker-compose up -d`

Install dependencies

```bash
  pip install -r requirements.txt
```

Start the bot (after setting the environment variables)

```bash
  python ./src/main.py
```

## Installation - Using Replit
> [!IMPORTANT]  
> Outdated. Replit hosting has been disabled for free users.

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

## Help - feedback
You can contact me on:

Discord: https://discord.gg/5WrVyQKWAr

Telegram: https://t.me/Non_Sono_matteo

Mail: <a href="mailto:mail@matt05.it">mail@matt05.it</a>

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Support me

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/matt05)

[![buy-me-a-coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/Matt0550)

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://paypal.me/sillittimatteo)

[contributors-shield]: https://img.shields.io/github/contributors/Matt0550/TagEveryoneTelegramBot.svg?style=for-the-badge
[contributors-url]: https://github.com/Matt0550/TagEveryoneTelegramBot/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Matt0550/TagEveryoneTelegramBot.svg?style=for-the-badge
[forks-url]: https://github.com/Matt0550/TagEveryoneTelegramBot/network/members
[stars-shield]: https://img.shields.io/github/stars/Matt0550/TagEveryoneTelegramBot.svg?style=for-the-badge
[stars-url]: https://github.com/Matt0550/TagEveryoneTelegramBot/stargazers
[issues-shield]: https://img.shields.io/github/issues/Matt0550/TagEveryoneTelegramBot.svg?style=for-the-badge
[issues-url]: https://github.com/Matt0550/TagEveryoneTelegramBot/issues
[license-shield]: https://img.shields.io/github/license/Matt0550/TagEveryoneTelegramBot.svg?style=for-the-badge
[license-url]: https://github.com/Matt0550/TagEveryoneTelegramBot/blob/master/LICENSE
[discord-shield]: https://img.shields.io/discord/828990499507404820?style=for-the-badge
[discord-url]: https://discord.gg/5WrVyQKWAr
[docker-shield]: https://img.shields.io/docker/pulls/matt0550/tageveryone_telegrambot?style=for-the-badge
[docker-url]: https://hub.docker.com/r/matt0550/tageveryone_telegrambot