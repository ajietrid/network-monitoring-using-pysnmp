from dbhelper import DBHelper
from snmphelper import SNMPhelper
from emailhelper import EmailHelper
from pinghelper import PingHelper
import multiprocessing as mp
import datetime
import pytz

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
    interface = hosts[1]
    traffic = snmp.get_traffic(host, interface)
    return [datetime.datetime.now(tz=timezone), host, interface, traffic]

def pingtest(host):
    pingresult = ping.ping(host)
    return[datetime.datetime.now(tz=timezone), host, pingresult]

def snmp_sqf(host):
    sqf_value = snmp.get_sqf(host)
    return [datetime.datetime.now(tz=timezone), host, sqf_value]

class Monitoringhelper:

    def update_uptime(self, processes):
        hosts = db.get_allhost()
        pool = mp.Pool(processes)
        results = pool.map(snmp_uptime, hosts)
        pool.close()
        for result in results:
            ts = result[0]
            host = result[1]
            uptime = result[2]
            lastrow = db.get_lastrow(host, 'uptime', 0)
            name = db.get_name(host)
            if lastrow == []:
                message = 'Initialization client'
                if uptime[0] == 'down':
                    db.initialization_uptime(ts, host, uptime, message)
                    name = db.get_name(host)
                    db.add_notification('uptime', ts, name, host, 0, uptime[1], 'down')
                else:
                    db.initialization_uptime(ts, host, uptime, message)
            else:
                diff = ts-lastrow[1]
                diffseconds = diff.total_seconds()
                cur_availability = db.get_diffandavailability(host, 'uptime', 0)
                if uptime[0] == 'down':
                    upsec = cur_availability[0]*cur_availability[1]/100 
                    totalsec = cur_availability[0]+diffseconds
                    availability = upsec/totalsec*100
                    downtime = diffseconds + lastrow[6]
                    message = uptime[1]
                    db.add_uptime(ts, host, 0, availability, downtime, message)
                    db.add_log(ts, name, host, 'uptime', 'Down', message, 0)
                    if lastrow[4] == 'up':
                        name = db.get_name(host)
                        db.add_notification('uptime', ts, name, host, 0, uptime[1], 'down')
                else:
                    upsec = (cur_availability[0]*cur_availability[1]/100)+diffseconds
                    totalsec = cur_availability[0]+diffseconds
                    availability = round(upsec/totalsec*100, 3)
                    downtime = 0
                    message = snmp.get_uptime_str(uptime[1])
                    db.add_uptime(ts, host, uptime[1], availability, downtime, message)
                    db.add_log(ts, name, host, 'uptime', 'Up', message, 0)
                    if lastrow[4] == 'down':
                        db.delete_data('uptime', host, 0)
            db.update_status_uptime(host)

    def update_traffic(self, processes):
        traffic_ints = db.get_alltrafficint()
        pool = mp.Pool(processes)
        results = pool.map(snmp_traffic, traffic_ints)
        pool.close()
        for result in results:
            ts = result[0]
            host = result[1]
            interface = result[2]
            if interface == 23:
                name_int = 'ether0'
            elif interface == 24:
                name_int = 'sat'
            else:
                name_int = interface
            traffic = result[3]
            lastrow = db.get_lastrow(host, 'traffic', interface)
            name = db.get_name(host)
            if lastrow == []:
                message = 'Initialization client'
                if traffic[0] == 'down':
                    db.initialization_traffic(ts, host, interface, 'down', 0, 0, message)
                    db.update_statustraffic(host, interface, 'down', 0)
                    name = db.get_name(host)
                    db.add_notification('traffic', ts, name, host, interface, traffic[1], 'down')
                else:
                    volumeinraw = traffic[1]
                    volumeoutraw = traffic[2]
                    db.initialization_traffic(ts, host, interface, 'up', volumeinraw, volumeoutraw, message)
                    db.update_statustraffic(host, interface, 'up', 100)
            else:
                diff = ts-lastrow[1]
                diffseconds = diff.total_seconds()
                cur_availability = db.get_diffandavailability(host, 'traffic', interface)
                lastvolumeinraw = lastrow[12]
                lastvolumeoutraw = lastrow[13]
                lasttimestamp = lastrow[1]
                if traffic[0] == 'down':
                    upsec = cur_availability[0]*cur_availability[1]/100
                    totalsec = cur_availability[0]+diffseconds
                    availability = round(upsec/totalsec*100, 3)

                    volumeinraw = lastvolumeinraw
                    volumeoutraw = lastvolumeoutraw
                    message = traffic[1] + " from " + name_int + " interface"
                    db.add_traffic(ts, host, interface, 0, 0, 0, 0, 0, 0, 'down', availability, volumeinraw, volumeoutraw, message)
                    db.add_log(ts, name, host, 'traffic', 'Down', message, interface)
                    db.update_statustraffic(host, interface, 'down', availability)
                    if lastrow[10] == 'up':
                        name = db.get_name(host)
                        db.add_notification('traffic', ts, name, host, interface, message, 'down')
                else:
                    upsec = (cur_availability[0]*cur_availability[1]/100)+diffseconds
                    totalsec = cur_availability[0]+diffseconds
                    availability = upsec/totalsec*100

                    interval = ts-lasttimestamp
                    intervalsec = interval.total_seconds()

                    if traffic[1]<lastvolumeinraw:
                        volumein = traffic[1]/1000
                    else:
                        volumein = (traffic[1]-lastvolumeinraw)/1000

                    if traffic[2]<lastvolumeoutraw:
                        volumeout = traffic[2]/1000
                    else:
                        volumeout = (traffic[2]-lastvolumeoutraw)/1000

                    speedin = volumein/intervalsec*8
                    speedout = volumeout/intervalsec*8

                    volumetotal = volumein+volumeout
                    speedtotal = speedin+speedout

                    volumeinraw = traffic[1]
                    volumeoutraw = traffic[2]
                    message= str(int(speedtotal)) + ' kbps '+ str(int(intervalsec)) + ' seconds ago' + " from " + name_int + " interface"
                    db.add_traffic(ts, host, interface, volumetotal, speedtotal, volumein, speedin, volumeout, speedout, 'up', availability, volumeinraw, volumeoutraw, message)
                    db.add_log(ts, name, host, 'traffic', 'Up', message, interface)
                    db.update_statustraffic(host, interface, 'up', availability)
                    if lastrow[10] == 'down':
                        db.delete_data('traffic', host, interface)

    def update_ping(self, processes):
        hosts = db.get_allhost()
        pool = mp.Pool(processes)
        results = pool.map(pingtest, hosts)
        pool.close()
        for result in results:
            host = result[1]
            pingresult = result[2]
            ts = result[0]
            lastrow = db.get_lastrow(host, 'ping', 0)
            name = db.get_name(host)
            if lastrow == []:
                message = 'Initialization client'
                if pingresult == 'Request timed out':
                    db.initialization_ping(ts, host, pingresult, message)
                    name = db.get_name(host)
                    db.add_notification('ping', ts, name, host, 0, pingresult, 'down')
                else:
                    db.initialization_ping(ts, host, pingresult,message)
            else:
                diff = ts-lastrow[1]
                diffseconds = diff.total_seconds()
                cur_availability = db.get_diffandavailability(host, 'ping', 0)
                if pingresult == 'Request timed out':
                    upsec = cur_availability[0]*cur_availability[1]/100
                    totalsec = cur_availability[0]+diffseconds
                    availability = upsec/totalsec*100
                    message = pingresult
                    db.add_ping(ts, host, 0, 0, 0, 0, "down", availability, message)
                    db.add_log(ts, name, host, 'ping', 'Down', message, 0)
                    if lastrow[7] == 'up':
                        name = db.get_name(host)
                        db.add_notification('ping', ts, name, host, 0, pingresult, 'down')
                else:
                    upsec = (cur_availability[0]*cur_availability[1]/100)+diffseconds
                    totalsec = cur_availability[0]+diffseconds
                    availability = round(upsec/totalsec*100, 3)
                    message = str(int(pingresult[0])) + ' ms'
                    db.add_ping(ts, host, int(pingresult[0]), int(pingresult[1]), int(pingresult[2]), int(pingresult[3]), "up", availability, message)
                    db.add_log(ts, name, host, 'ping', 'Up', message, 0)
                    if lastrow[7] == 'down':
                        db.delete_data('ping', host, 0)

    def update_sqf(self, processes):
        hosts = db.get_allsqfclient()
        pool = mp.Pool(processes)
        results = pool.map(snmp_sqf, hosts)
        pool.close()
        for result in results:
            host = result[1]
            sqf_value = result[2]
            ts = result[0]
            lastrow = db.get_lastrow(host, 'sqf', 0)
            name = db.get_name(host)
            if lastrow == []:
                message = 'Initialization client'
                if sqf_value[0] == 'down':
                    db.initialization_sqf(ts, host, sqf_value, message)
                    db.update_statssqf(host, 0, "down", 0)
                    name = db.get_name(host)
                    db.add_notification('sqf', ts, name, host, 0, sqf_value[1] , 'down')
                else:
                    db.initialization_sqf(ts, host, sqf_value, message)
                    db.update_statssqf(host, sqf_value[1], "up", 100)
            else:
                diff = ts-lastrow[1]
                diffseconds = diff.total_seconds()
                cur_availability = db.get_diffandavailability(host, 'sqf', 0)
                if sqf_value[0] == 'down':
                    upsec = cur_availability[0]*cur_availability[1]/100
                    totalsec = cur_availability[0]+diffseconds
                    availability = upsec/totalsec*100
                    message = sqf_value[1]
                    db.add_sqf(ts, host, 0, availability, message)
                    db.update_statssqf(host, 0, "down", availability)
                    db.add_log(ts, name, host, 'sqf', 'Down', message, 0)
                    if lastrow[4] == 'up':
                        name = db.get_name(host)
                        db.add_notification('sqf', ts, name, host, 0, message , 'down')
                else:
                    upsec = (cur_availability[0]*cur_availability[1]/100)+diffseconds
                    totalsec = cur_availability[0]+diffseconds
                    availability = round(upsec/totalsec*100, 3)
                    message = str(sqf_value[1])  
                    db.add_sqf(ts, host, sqf_value[1], availability, message)
                    db.update_statssqf(host, sqf_value[1], "up", availability)
                    db.add_log(ts, name, host, 'sqf', 'Up', message, 0)
                    if lastrow[4] == 'down':
                        db.delete_data('sqf', host, 0)

    def notification(self):
        ts1 = db.get_currenttimestamp()
        host = db.get_allhost()
        traffic_ints = db.get_alltrafficint()
        sqf_clients = db.get_allsqfclient()

        uptimes = db.get_uptimereport(len(host))
        traffics = db.get_trafficreport(len(traffic_ints))
        pings = db.get_pingreport(len(host))
        sqfs = db.get_sqfreport(len(sqf_clients))

        uptimereport = []
        trafficreport = []
        pingreport = []
        sqfreport = []

        for uptime in uptimes:
            if uptime[4]=='down':
                name = db.get_name(uptime[2])
                uptimereport.append([uptime[1], name, uptime[2], 'down'])

        for traffic in traffics:
            if traffic[10]=='down':
                name = db.get_name(traffic[2])
                trafficreport.append([traffic[1], name, traffic[2], traffic[3], 'down'])

        for pingx in pings:
            if pingx[7]=='down':
                name = db.get_name(pingx[2])
                pingreport.append([pingx[1], name, pingx[2], 'down'])

        for sqf in sqfs:
            if sqf[4]=='down':
                name = db.get_name(sqf[2])
                sqfreport.append([sqf[1], name, sqf[2], 'down'])

        email.send_email(len(uptimereport), len(trafficreport), len(pingreport), len(sqfreport))
        ts2 = db.get_currenttimestamp()
        duration = ts2-ts1
        print("Update notification duration: "+str(duration.total_seconds())+" seconds for "+str(len(traffics)+len(uptimes)+len(pings)+len(sqfs))+" sensors.")

"""
    def update_client_data(self):
        hosts = db.get_allhost()
        for host in hosts:
            descr = str(snmp.get_sysdescr(host))
            name = str(snmp.get_sysname(host))
            name = name.upper()
            name = name.replace ("_", " ")
            db.update_sysdescr(descr, host)
            db.update_client_name(name, host)
        db.close_conn()

    def update_uptime(self):
        hosts = db.get_allhost()
        for host in hosts:
            uptime = snmp.get_uptime(host)
            ts = db.get_currenttimestamp()
            lastrow = db.get_lastrow(host, 'uptime')
           
            if lastrow == []:
                if uptime == '0':
                    availability = 0
                    downtime = 300
                    db.add_uptime(ts, host, uptime, availability, downtime)
                    name = db.get_name(host)
                    db.add_notification('uptime', ts, name, host, 'unread', 'down')
                else:
                    availability = 100
                    downtime = 0
                    db.add_uptime(ts, host, uptime, availability, downtime)
            else:
                diff = ts-lastrow[1]
                diffseconds = diff.total_seconds()
                cur_availability = db.get_diffandavailability(host, 'uptime')
                
                if uptime == 'down':
                    upsec = cur_availability[0]*cur_availability[1]/100
                    totalsec = cur_availability[0]+diffseconds
                    availability = upsec/totalsec*100
                    downtime = diff + lastrow[6]
                    db.add_uptime(ts, host, uptime, availability, downtime)
                    name = db.get_name(host)
                    db.add_notification('uptime', ts, name, host, 'unread', 'down')
                else:
                    upsec = (cur_availability[0]*cur_availability[1]/100)+diffseconds
                    totalsec = cur_availability[0]+diffseconds
                    availability = upsec/totalsec*100
                    downtime = 0
                    db.add_uptime(ts, host, uptime, availability, downtime)
                    if lastrow[4] == 'down':
                        db.delete_data(host, 'notification')
                    else:
                        pass
        db.update_status_uptime()

    def update_traffic(self):
        traffic_ints = db.get_alltrafficint()
        for traffic_int in traffic_ints:
            host = traffic_int[0]
            interface = traffic_int[1]
            traffic = snmp.get_traffic(host, interface)
            ts = db.get_currenttimestamp()
            lastrow = db.get_lastrowtraffic(host, 'traffic', interface)

            
            diff = ts-lastrow[1]
            diffseconds = diff.total_seconds()
            cur_availability = db.get_diffandavailability_int(host, 'traffic', traffic_int)            
            lastvolumeinraw = lastrow[12]
            lastvolumeoutraw = lastrow[13]
            lasttimestamp = lastrow[1]
            if traffic == 'down':
                upsec = cur_availability[0]*cur_availability[1]/100
                totalsec = cur_availability[0]+diffseconds
                availability = upsec/totalsec*100

                volumeinraw = lastvolumeinraw
                volumeoutraw = lastvolumeoutraw

                db.add_traffic(ts, host, interface, 0, 0, 0, 0, 0, 0, 'down', availability, volumeinraw, volumeoutraw)
                name = db.get_name(host)
                db.add_notification('traffic', ts, name, host, 'unread', 'down', traffic_int)
            else:
                upsec = (cur_availability[0]*cur_availability[1]/100)+diffseconds
                totalsec = cur_availability[0]+diffseconds
                availability = upsec/totalsec*100

                interval = ts-lasttimestamp
                intervalsec = interval.total_seconds()

                if traffic[0]<lastvolumeinraw:
                    volumein = traffic[0]
                else:
                    volumein = (traffic[0]-lastvolumeinraw)/1000

                if traffic[1]<lastvolumeoutraw:
                    volumeout = traffic[1]
                else:

                    volumeout = (traffic[1]-lastvolumeoutraw)/1000

                speedin = volumein/intervalsec*8
                speedout = volumeout/intervalsec*8

                volumetotal = volumein+volumeout
                speedtotal = speedin+speedout

                volumeinraw = traffic[0]
                volumeoutraw = traffic[1]

                db.add_traffic(ts, host, interface, volumetotal, speedtotal, volumein, speedin, volumeout, speedout, 'up', availability, volumeinraw, volumeoutraw)
                if lastrow[11] == 'down':
                    db.delete_data_int(host, 'notification', interface)
                else:
                    pass
        db.update_status_traffic()
"""
"""
    def notification(self):
        host = db.get_allhost()
        traffic_ints = db.get_alltrafficint()
        uptimes = db.get_uptimereport(len(host))
        #print(uptimes)
        traffics = db.get_trafficreport(len(traffic_ints))
        #print(traffics)

        uptimereport = []
        trafficreport = []

        for uptime in uptimes:
            if uptime[4]=='down':
                name = db.get_name(uptime[2])
                db.add_notification('uptime', uptime[1], name, uptime[2], 'unread', 'down')
                uptimereport.append([uptime[1], name, uptime[2], 'down'])

        for traffic in traffics:
            if traffic[10]=='down':
                name = db.get_name(traffic[2])
                db.add_notification('traffic', traffic[1], name, traffic[2], 'unread', 'down', traffic[3])
                trafficreport.append([traffic[1], name, traffic[2], traffic[3], 'down'])
"""
