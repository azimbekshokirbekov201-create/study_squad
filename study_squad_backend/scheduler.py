import logging

from apscheduler.schedulers.background import BackgroundScheduler

from database import SessionLocal
from services.weekly_coin_service import process_all_users_weekly

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def _run_weekly_coin_job():
    db = SessionLocal()
    try:
        results = process_all_users_weekly(db)
        logger.info(f"Weekly coin job: {len(results)} ta hafta yakunlandi va coin berildi")
    finally:
        db.close()


def start_scheduler():
    # Har kuni yarim tunda tekshiradi - qaysi foydalanuvchilarning haftasi tugagan
    scheduler.add_job(_run_weekly_coin_job, "cron", hour=0, minute=0, id="weekly_coin_job")
    scheduler.start()
