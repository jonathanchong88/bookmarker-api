# import time
import atexit
import os
from flask import current_app
from src.ustil import solve, allowed_file, basedir
from apscheduler.schedulers.background import BackgroundScheduler


# def print_date_time():
#     print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))


def delete_upload_dir():
    
    folder = os.path.join(basedir, 'static/uploads')
    # print(folder)

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            print('finish')
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


scheduler = BackgroundScheduler()
# scheduler.add_job(func=print_date_time, trigger="interval", seconds=10)
# Runs from Monday to Friday at 5:30 (am) until 2014-05-30 00:00:00
scheduler.add_job(func=delete_upload_dir, trigger='cron',
              hour=5, minute=14)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())
