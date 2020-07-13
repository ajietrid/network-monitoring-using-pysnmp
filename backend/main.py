from monitoringhelper import Monitoringhelper
from dbhelper import DBHelper
import schedule
#import multiprocessing
import time as timex
#import test1, test2, test3, test4

monitoring = Monitoringhelper()
db = DBHelper()


def runmonitoring():
    try:
        start_time = timex.time()
        monitoring.update_uptime(processes=40)
        monitoring.update_traffic(processes=40)
        monitoring.update_ping(processes=40)
        monitoring.update_sqf(processes=40)
        monitoring.notification()
        elapsed_time = timex.time()-start_time
        print("Elapsed time: "+str(elapsed_time))
        db.close_conn()
    except:
        return "error"

for h in range(0, 24, 1):
    if h > 9:
        hour = str(h)
    else:
        hour = "0"+str(h)
    for m in range(0, 56, 5):
        if m > 9:
            mins = ":"+str(m)
        else:
            mins = ":0"+str(m)
        schedule.every().day.at(hour+mins).do(runmonitoring)


while True:
    # Checks whether a scheduled task
    # is pending to run or not
    schedule.run_pending()
    timex.sleep(1)