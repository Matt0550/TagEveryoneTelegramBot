import datetime

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.decorators.cooldown import cooldown
from bot.decorators.is_owner import is_owner
from bot.utils.errors import reply_generic_error
from services.group_service import GroupService
from services.log_service import LogService
from utils.logger_base import logger
from utils.session_manager import Session, engine

from .status_command import start_time


@is_owner
@cooldown(15)
async def stats(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    session = Session(engine)
    try:
        total_groups = GroupService.get_total_groups(session)
        total_members = GroupService.get_total_users(session)

        now = datetime.datetime.utcnow()
        hourly_logs = LogService.get_logs_since(
            session, now - datetime.timedelta(hours=1)
        )
        daily_logs = LogService.get_logs_since(
            session, now - datetime.timedelta(days=1)
        )
        weekly_logs = LogService.get_logs_since(
            session, now - datetime.timedelta(days=7)
        )

        uptime = datetime.datetime.now() - start_time
        uptime_str = str(uptime).split(".")[0]

        hourly_actions = {}
        daily_actions = {}
        weekly_actions = {}

        for log in hourly_logs:
            action = log.action
            hourly_actions[action] = hourly_actions.get(action, 0) + 1

        for log in daily_logs:
            action = log.action
            daily_actions[action] = daily_actions.get(action, 0) + 1

        for log in weekly_logs:
            action = log.action
            weekly_actions[action] = weekly_actions.get(action, 0) + 1

        def escape_markdown_v2(text):
            if text is None:
                return "Unknown"
            escape_chars = [
                "_",
                "*",
                "[",
                "]",
                "(",
                ")",
                "~",
                "`",
                ">",
                "#",
                "+",
                "-",
                "=",
                "|",
                "{",
                "}",
                ".",
                "!",
            ]
            escaped = str(text)
            for char in escape_chars:
                escaped = escaped.replace(char, f"\\{char}")
            return escaped

        avg_members = round(total_members / total_groups, 2) if total_groups > 0 else 0

        stats_message = "📊 *Bot Statistics*\n\n"
        stats_message += "🏢 *Database Info:*\n"
        stats_message += f"• Active Groups: {total_groups}\n"
        stats_message += f"• Active Members: {total_members}\n"
        stats_message += f"• Avg Members/Group: {avg_members}\n\n"
        stats_message += f"⏰ *Uptime:* {escape_markdown_v2(uptime_str)}\n\n"
        stats_message += "📈 *Activity \\(Last Hour\\):*\n"
        stats_message += f"• Total Events: {len(hourly_logs)}\n"

        if hourly_actions:
            top_hourly = sorted(
                hourly_actions.items(), key=lambda x: x[1], reverse=True
            )[:3]
            for action, count in top_hourly:
                safe_action = escape_markdown_v2(action)
                stats_message += f"• {safe_action}: {count}\n"

        stats_message += "\n📅 *Activity \\(Last 24h\\):*\n"
        stats_message += f"• Total Events: {len(daily_logs)}\n"

        if daily_actions:
            top_daily = sorted(daily_actions.items(), key=lambda x: x[1], reverse=True)[
                :4
            ]
            for action, count in top_daily:
                safe_action = escape_markdown_v2(action)
                stats_message += f"• {safe_action}: {count}\n"

        stats_message += "\n📊 *Activity \\(Last 7 days\\):*\n"
        stats_message += f"• Total Events: {len(weekly_logs)}\n"

        if weekly_actions:
            top_weekly = sorted(
                weekly_actions.items(), key=lambda x: x[1], reverse=True
            )[:4]
            for action, count in top_weekly:
                safe_action = escape_markdown_v2(action)
                stats_message += f"• {safe_action}: {count}\n"

        stats_message += "\n🔗 *Links:*\n"
        stats_message += "• [Buy me a coffee](https://buymeacoffee.com/Matt0550)\n"
        stats_message += (
            "• [Source code](https://github.com/Matt0550/TagEveryoneTelegramBot)"
        )

        try:
            await update.message.reply_text(
                stats_message,
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True,
            )
        except Exception as markdown_error:
            logger.warning(f"MarkdownV2 parsing failed: {markdown_error}")
            await update.message.reply_text(
                "Stats Error: Markdown failed.", disable_web_page_preview=True
            )

        if update.message.chat:
            LogService.add_log(
                session,
                update.message.from_user.id,
                str(update.message.chat.id),
                "stats",
                "Advanced stats sent",
            )

    except Exception as e:
        logger.exception(f"[ERROR] stats: {e}")
        await reply_generic_error(update)
    finally:
        session.close()
