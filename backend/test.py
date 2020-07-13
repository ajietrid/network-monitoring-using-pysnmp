from dbhelper import DBHelper
from monitoringhelper import Monitoringhelper
from snmphelper import SNMPhelper
from emailhelper import EmailHelper
from pinghelper import PingHelper
import time as timex
import datetime
import pytz
import math
import multiprocessing as mp
from selfmonitoringhelper import SelfMonitoring

db = DBHelper()
snmp = SNMPhelper()
email = EmailHelper()
ping = PingHelper()
timezone = pytz.timezone("Asia/Jakarta")



def snmp_uptime(host):
    uptime = snmp.get_uptime(host)
    return [datetime.datetime.now(tz=timezone), host, uptime]

def snmp_traffic(hosts):
    host = hosts[0]
    interface = 23
    traffic = snmp.get_traffic(host, interface)
    return [datetime.datetime.now(tz=timezone), host, interface, traffic]

def pingtest(host):
    pingresult = ping.ping(host)
    return[datetime.datetime.now(tz=timezone), host, pingresult]

def snmp_sqf(host):
    sqf_value = snmp.get_sqf(host)
    return [datetime.datetime.now(tz=timezone), host, sqf_value]

"""result = db.show_uptime('118.97.24.170')
print(result)
result =type(result)
print(result)"""

"""result = db.show_notification()
counter = len(result)
print(result)
"""
"""result = db.show_client_data()
print(result)
print(result[0][1])"""

"""result= db.filter_client_data_by_id(1)
print(result[2])"""

"""result = snmp.get_number_of_interface('36.91.116.162')
print(result)"""

"""
client = db.show_client_data()
hosts = db.get_allhost()

last_up = []
for host in hosts:
	row = db.get_lastrow( host, 'uptime')
	if row == []:
		pass
	else:
		last_up.append([row[2], row[4]])
print(last_up)"""

"""
processes = 40
traffic_ints = db.get_alltrafficint()
pool = mp.Pool(processes)
results = pool.map(snmp_traffic, traffic_ints)
pool.close()
for result in results:
	ts = result[0]
	print(ts)
	host = result[1]
	print(hosts)
	interface = result[2]
	print(interface)
	traffic = result[3]
	print(traffic)

result = snmp.get_traffic('36.91.183.50', 1)
print(result)"""

"""processes = 40
hosts = db.get_allhost()
pool = mp.Pool(processes)
results = pool.map(pingtest, hosts)
pool.close()
for result in results:
	host = result[1]
	pingresult = result[2]
	print(type(pingresult))
	print(pingresult)
	ts = result[0]"""

db = DBHelper()



"""
procs = []
	sensors = [monitoring.update_uptime(processes=40), monitoring.update_traffic(processes=40), monitoring.update_ping(processes=40), monitoring.update_sqf(processes=40)]
	for sensor in sensors:
		proc = multiprocessing.Process(target= run_sensor, args= (sensor,))
		procs.append(proc)
		proc.start()

	for proc in procs:
		proc.join()
		"""

"""hosts = db.get_allhost()
clients = db.get_alltrafficint()

for host in hosts:
	name = db.get_name(host)
	lastrow = db.get_lastrow(host, 'traffic', 24)
	if lastrow[10] == 'down':
		db.add_notification('traffic', lastrow[1], name, host, 24, lastrow[14], lastrow[10])"""


#get_alltrafficint(self):
#add_notification(self, parameter, ts, name, ip, interface, message, status):

sm = SelfMonitoring()


mon = sm.get_pc_stats()
print(mon)

print(db.get_currenttimestamp())
			


