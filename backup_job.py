import vars
import shutil
import arrow
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os, subprocess
from dombot.monsters import r

DOMBOT_BACKUP_CHANNEL = -1001463171286
job_scheduler = AsyncIOScheduler()

async def create_and_send_backup():
    db_list = [
        "./dombot/rss/databases/sqlite/equipments.db",
        "./dombot/rss/databases/sqlite/filters.db",
        "./dombot/rss/databases/sqlite/monsters.db",
        "./dombot/rss/databases/sqlite/triggers.db",
        "./dombot/rss/databases/sqlite/timezones.db",
        "./dombot/rss/databases/sqlite/regions.db",
        "./dombot/rss/databases/sqlite/reminders/jobs.db",
        "./dombot/rss/databases/sqlite/reminders/reminders.db",
        "./dombot/typo_tales/dragon_egg/dragon_egg.db",
        "/var/lib/redis/dump.rdb"
    ]

    # Copy the database so it can be contained in backup
    r.save()
    bkp_dir = "backup"
    os.makedirs(bkp_dir, exist_ok=True)
    os.system(f"pg_dump -U dom -f {bkp_dir}/pepe.bkp dom -Fc")

    for db in db_list:
        shutil.copy(db, bkp_dir)

    current_time = arrow.now().format("DD_MM_YYYY-HH_mm_ss")
    zip_file_name = f"backup_{current_time}"
    zip_file_path = shutil.make_archive(zip_file_name, "zip", f"{bkp_dir}")
    await vars.bot.send_file(DOMBOT_BACKUP_CHANNEL, file=f"{zip_file_path}")

    if os.path.exists(zip_file_path):
        try:
            os.remove(zip_file_path)
            shutil.rmtree(bkp_dir)
            print(f"{current_time} Backup sent.")
        except Exception as e:
            print("Failed remove: ", e)

async def rdb_backup():
    r.bgsave()

def get_job_sched():
    global job_scheduler
    return job_scheduler

async def quest(arg):
    await vars.bot.send_message(vars.BOT_TESTING, arg)

def sched_cw_jbs(job_sched):
    # quest
    job_sched.add_job(quest, args=["qst"], trigger='cron', hour=9, minute=0, misfire_grace_time=None)
    job_sched.add_job(quest, args=["qst"], trigger='cron', hour=21, minute=30, misfire_grace_time=None)

    # arena
    job_sched.add_job(quest, args=["arn"], trigger='cron', hour=13, minute=46, misfire_grace_time=None)

def create_backup_job():
    from user_bot.vpb_reminder import remind_vpb
    from user_bot.glory_reminder import remind_glory
    global job_scheduler
    job_scheduler.configure(timezone="Asia/Kolkata")
    job_scheduler.start()
    job_scheduler.add_job(create_and_send_backup, 'cron', hour='20', minute='00')
    job_scheduler.add_job(rdb_backup, 'cron', hour="*", minute="40", misfire_grace_time=None)
    job_scheduler.add_job(remind_vpb, 'cron', hour=21, minute=0, misfire_grace_time=None)
    #job_scheduler.add_job(remind_glory, 'cron', hour=12, minute=45, misfire_grace_time=None)
    #job_scheduler.add_job(remind_glory, 'cron', hour=20, minute=45, misfire_grace_time=None)
    #job_scheduler.add_job(remind_glory, 'cron', hour=4, minute=45, misfire_grace_time=None)
    #sched_cw_jbs(job_scheduler)
