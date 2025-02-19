# Tag Everyone Telegram Bot

![Forks][forks-shield] ![Stars][stars-shield] ![Issues][issues-shield] ![License][license-shield] ![Discord][discord-shield] ![Docker Pulls][docker-shield]

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

## Overview

**Tag Everyone Telegram Bot** allows you to quickly mention all users in a Telegram group. Users can join or leave the list of mentioned users through simple commands, providing an efficient way to notify everyone in a group.

You can view the live demo and interact with the bot using [this link](https://t.me/TagEveryone_TheBot).

### Features

- Trigger mentions using `/everyone` or `@everyone` (similar to Discord).
- Users can subscribe to or unsubscribe from the notification list using `/in` and `/out`.
- Full compatibility with Telegram WebApp.
- SQLite3 database support for persistent data storage.
- Option to host the bot on your own server or use the provided Docker image.

---

## Commands

- `/in` - Add yourself to the list of users to be mentioned.
- `/out` - Remove yourself from the mention list.
- `/everyone` or `@everyone` - Mention all users in the list.
- `/all` - Same as `/everyone`, mention all users.
- `/help` - Show available commands.
- `/status` - Check bot status and uptime.
- `/stats` - View bot statistics (NEW).
- `/announce text` - Broadcast a message to all groups (NEW).
- `/list` - Show the list of users without mentioning them.

---

## Public Bot Access

You can try the public bot here: [TagEveryone_TheBot](https://t.me/Tag_Everyone_TheBot).

> **Note**  
> The public bot is hosted on a personal server and might experience downtime. You are welcome to host it yourself using Docker or other methods. If you'd like to support the bot's upkeep, you can do so via [Ko-fi](https://ko-fi.com/matt05) or [Buy Me A Coffee](https://www.buymeacoffee.com/Matt0550).

---

## Self-Hosting Guide

To set up and host the bot on your own server, follow these instructions.

### Environment Variables

Ensure to configure the following environment variables before running the bot:

| Variable               | Description                                | Default      |
|------------------------|--------------------------------------------|--------------|
| `token`                | Telegram Bot Token                         | -            |
| `owner_id`             | Telegram User ID (Bot owner)               | -            |
| `enable_webapp_server` | Enable WebApp server                       | `True`       |
| `webserver_debug`      | Enable Flask debug mode                    | `False`      |
| `report_errors_owner`  | Report errors to the bot owner             | `False`      |
| `secret_key`           | Flask secret key (generate a random key)   | -            |
| `APP_HOST`             | Flask host address                         | `localhost`  |
| `APP_PORT`             | Flask port                                 | `5000`       |

---

### Docker Installation

#### Build Docker Image

```bash
docker build -t tageveryone_telegrambot .
```

#### Run with Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3'

services:
  tageveryone_telegrambot:
    image: matt0550/tageveryone_telegrambot
    user: 1001:1001
    environment:
      - token=BOT_TOKEN
      - owner_id=OWNER_ID
      - enable_webapp_server=True
      - webserver_debug=False
      - report_errors_owner=False
      - secret_key=SECRET_KEY
    volumes:
      - /path/to/database.db:/src/db/database.db
    ports:
      - 5000:5000
    restart: unless-stopped
```

Run the container:

```bash
docker-compose up -d
```

#### Run with Docker CLI

```bash
docker run -d \
  -e token=TG_BOT_TOKEN \
  -e owner_id=TG_OWNER_ID \
  -e enable_webapp_server=True \
  -e webserver_debug=False \
  -e report_errors_owner=False \
  -e secret_key=SECRET_KEY \
  -v /path/to/database.db:/src/db/database.db \
  -p 5000:5000 \
  --name tageveryone_telegrambot \
  matt0550/tageveryone_telegrambot
```

---

### Installation Without Docker

1. **Clone the repository:**

```bash
git clone https://github.com/Matt0550/TagEveryoneTelegramBot
cd TagEveryoneTelegramBot
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**

Copy the `.env.example` file to `.env` and modify the values:

```bash
cp .env.example .env
```

4. **Run the bot:**

```bash
python ./src/main.py
```

---

## WebApp Setup

To enable the WebApp, set `enable_webapp_server=True` in the environment variables.

You can configure a reverse proxy (using Nginx or Caddy) to access the WebApp via a public URL. Update the WebApp URL in the bot settings on Telegram's BotFather.

---

## Help and Feedback

If you need assistance or want to provide feedback, you can reach out via:

- [Discord](https://matt05.it/discord)
- [Telegram](https://matt05.it/telegram)
- [Email](mailto:mail@matteosillitti.com)

---

## Contributors

<a href="https://github.com/Matt0550/TagEveryoneTelegramBot/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Matt0550/TagEveryoneTelegramBot"/>
</a>

---

## License

This project is licensed under the MIT License. See [LICENSE](https://github.com/Matt0550/TagEveryoneTelegramBot/blob/master/LICENSE) for more information.

---

## Support the Project

If you'd like to support the project, consider donating via:

[![Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/matt05)  
[![Buy Me A Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/Matt0550)  
[![PayPal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://paypal.me/sillittimatteo)

[forks-shield]: https://img.shields.io/github/forks/Matt0550/TagEveryoneTelegramBot.svg?style=for-the-badge
[stars-shield]: https://img.shields.io/github/stars/Matt0550/TagEveryoneTelegramBot.svg?style=for-the-badge
[issues-shield]: https://img.shields.io/github/issues/Matt0550/TagEveryoneTelegramBot.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/Matt0550/TagEveryoneTelegramBot.svg?style=for-the-badge
[discord-shield]: https://img.shields.io/discord/828990499507404820?style=for-the-badge
[docker-shield]: https://img.shields.io/docker/pulls/matt0550/tageveryone_telegrambot?style=for-the-badge
