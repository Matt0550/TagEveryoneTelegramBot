import asyncio
import json

from telegram import Update
from telegram.ext import ContextTypes

from bot.decorators.cooldown import cooldown
from bot.decorators.is_owner import is_owner
from bot.utils.errors import reply_generic_error
from celery_workers.tasks.send_announce_batch import send_announce_batch
from models_all.announce_job_group import AnnounceJobGroup
from models_all.async_job import AsyncJob, JobStatus, JobType
from services.group_service import GroupService
from services.log_service import LogService
from utils.logger_base import logger
from utils.session_manager import Session, engine

# Number of groups to process per Celery batch
ANNOUNCE_BATCH_SIZE = 5

# Seconds between batch dispatches (stagger to avoid rate limits)
ANNOUNCE_BATCH_STAGGER_SECONDS = 2


@is_owner
@cooldown(15)
async def announce(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    session = Session(engine)
    try:
        message = update.message.text.replace("/announce ", "")
        if not message or message == "" or message == "/announce":
            await update.message.reply_text("You must specify a message")
            return

        groups = GroupService.get_all_groups(session)
        if not groups:
            await update.message.reply_text("No groups found in the database.")
            return

        # Create the async job
        job = AsyncJob(
            job_type=JobType.ANNOUNCE,
            status=JobStatus.PENDING,
            total_items=len(groups),
            started_by=update.message.from_user.id,
            metadata_json=json.dumps(
                {
                    "message": message,
                    "chat_id": update.message.chat.id,
                }
            ),
        )
        session.add(job)
        session.commit()
        session.refresh(job)

        # Create announce_job_groups rows for each group
        announce_group_ids = []
        for group in groups:
            ajg = AnnounceJobGroup(
                job_id=job.id,
                group_telegram_id=group.telegram_id,
                group_name=group.group_name,
            )
            session.add(ajg)
            session.commit()
            session.refresh(ajg)
            announce_group_ids.append(ajg.id)

        # Chunk into batches and dispatch Celery tasks with stagger
        batches = [
            announce_group_ids[i : i + ANNOUNCE_BATCH_SIZE]
            for i in range(0, len(announce_group_ids), ANNOUNCE_BATCH_SIZE)
        ]

        for batch_index, batch in enumerate(batches):
            countdown = batch_index * ANNOUNCE_BATCH_STAGGER_SECONDS
            send_announce_batch.apply_async(
                kwargs={
                    "job_id": job.id,
                    "group_ids": batch,
                    "message": message,
                },
                countdown=countdown,
            )

        await update.message.reply_text(
            f"📢 Announce job started!\n\n"
            f"• Job ID: <b>{job.id}</b>\n"
            f"• Sending to <b>{len(groups)}</b> groups\n"
            f"• Split into <b>{len(batches)}</b> batches "
            f"(staggered {ANNOUNCE_BATCH_STAGGER_SECONDS}s apart)\n\n"
            f"Messages will be delivered in the background. "
            f"Use /announce_status {job.id} to check progress.",
            parse_mode="HTML",
        )

        LogService.add_log(
            session,
            update.message.from_user.id,
            str(update.message.chat.id),
            "announce",
            f"Announce job {job.id} started: {len(groups)} groups, "
            f"{len(batches)} batches",
        )

    except Exception as e:
        logger.error(f"[ERROR] announce: {e}", exc_info=True)
        await reply_generic_error(update)
    finally:
        session.close()


@is_owner
async def announce_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check the status of an announce job by ID."""
    session = Session(engine)
    try:
        args = context.args
        if not args:
            await update.message.reply_text("Usage: /announce_status <job_id>")
            return

        try:
            job_id = int(args[0])
        except ValueError:
            await update.message.reply_text("Invalid job ID. Must be a number.")
            return

        job = session.get(AsyncJob, job_id)
        if not job or job.job_type != JobType.ANNOUNCE:
            await update.message.reply_text(f"Announce job {job_id} not found.")
            return

        # Build status message
        status_emoji = {
            JobStatus.PENDING: "⏳",
            JobStatus.IN_PROGRESS: "🔄",
            JobStatus.COMPLETED: "✅",
            JobStatus.FAILED: "❌",
        }
        emoji = status_emoji.get(job.status, "❓")

        progress = job.completed_items + job.failed_items
        percentage = (
            round(progress / job.total_items * 100, 1) if job.total_items > 0 else 0
        )

        status_text = (
            f"{emoji} <b>Announce Job #{job.id}</b>\n\n"
            f"• Status: <b>{job.status}</b>\n"
            f"• Progress: <b>{progress}/{job.total_items}</b> ({percentage}%)\n"
            f"• Sent: <b>{job.completed_items}</b>\n"
            f"• Failed: <b>{job.failed_items}</b>\n"
            f"• Started: {job.created_at.strftime('%Y-%m-%d %H:%M:%S') if job.created_at else 'N/A'}\n"
        )

        if job.completed_at:
            status_text += (
                f"• Completed: {job.completed_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            )

        if job.error_message:
            status_text += f"\n⚠️ Error: {job.error_message}\n"

        await update.message.reply_text(status_text, parse_mode="HTML")

    except Exception as e:
        logger.error(f"[ERROR] announce_status: {e}", exc_info=True)
        await reply_generic_error(update)
    finally:
        session.close()


@is_owner
@cooldown(15)
async def checkGroups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = Session(engine)
    try:
        groups = GroupService.get_all_groups(session)
        working_groups = []
        failed_groups = []
        for group in groups:
            try:
                _chat = await context.bot.get_chat(group.telegram_id)
                working_groups.append(group.telegram_id)
            except Exception:
                failed_groups.append(group.telegram_id)
                GroupService.delete_group(session, group.telegram_id)
            await asyncio.sleep(0.1)

        await update.message.reply_text(
            f"Check completed.\nWorking groups: {len(working_groups)}\nFailed groups (removed): {len(failed_groups)}"
        )
    finally:
        session.close()
