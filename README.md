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

## Public bot on Telegram
You can use the public bot on Telegram: [TagEveryone_TheBot](https://t.me/Tag_Everyone_TheBot)

> [!NOTE]
> The public bot is hosted on my server, so it may be slow or not available. You can host the bot yourself or use the Docker image. Consider supporting me on [Ko-fi](https://ko-fi.com/matt05) or [Buy me a coffee](https://www.buymeacoffee.com/Matt0550) to keep the bot online.

## Usage

1. Add the bot to your group
2. Give the bot the permission to read messages and send messages (**admin**)
3. Use the `/in` command to add yourself to the list
4. Use the `/everyone` command to mention all users in the list


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


## TO-DO
- [ ] REST API
- [x] WebApp
- [ ] Ignore tag requests if time enlapsed is > 2min
- [ ] Automatically add all members' group to Everyone's list
- [ ] Welcome message when the bot is added to a group

# Self-hosting
## Environment variables
| Variable | Description | Default |
|----------|-------------|---------|
| token | Telegram Bot Token | - |
| owner_id | Telegram User ID | - |
| enable_webapp_server | Enable the WebApp server | True |
| webserver_debug | Enable Flask debug | False |
| report_errors_owner | Report errors to the owner | False |
| secret_key | Flask secret key. Generate a random | - |
| APP_HOST | Flask host | localhost/0.0.0.0 |
| APP_PORT | Flask port | 5000 |

## Installation - Using Docker
### Build the image
```bash
docker build -t tageveryone_telegrambot .
```
### Run the container with docker-compose
Create a `docker-compose.yml` file with the following content:

```yaml
version: '3'

services:
  tageveryone_telegrambot:
    image: matt0550/tageveryone_telegrambot # or the image name you used
    user: 1001:1001
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

### Run the container with docker run
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

## Installation - Without Docker

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

Set the environment variables copying the `.env.example` file to `.env` and filling the values

```bash
  cp .env.example .env
```

Start the bot (after setting the environment variables)

```bash
  python ./src/main.py
```

## Set up the WebApp
If you want to enable the WebApp, you have to set the `enable_webapp_server` environment variable to `True`.

The WebApp is available at `http://<ip>:<port>` by default.

To show the WebApp on the Telegram bot, you have to setup a reverse proxy to the WebApp. You can use Nginx or Caddy. Then configure the webapp URL in the bot settings in the Telegram BotFather.


## Help - feedback
You can contact me on:

Discord: https://matt05.it/discord

Telegram: https://matt05.it/telegram

Mail: <a href="mailto:mail@matteosillitti.com">mail@matteosillitti.com</a>

# Contributors

<!-- Copy-paste in your Readme.md file -->

<a href = "https://github.com/Matt0550/TagEveryoneTelegramBot/graphs/contributors">
  <img src = "https://contrib.rocks/image?repo=Matt0550/TagEveryoneTelegramBot"/>
</a>


# License

[MIT](https://choosealicense.com/licenses/mit/)

# Support me

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