import psycopg2
import time
import datetime


class DBHelper:
    def __init__(self):
        self.conn = psycopg2.connect("host='localhost' dbname='suksesnms' user='ajietrid' password='postgres_NMS'")
        self.cur = self.conn.cursor()
    
    def close_conn(self):
        self.conn.close()

    # Get Data: ----------
    def get_currenttimestamp(self):
        stmt = "SELECT current_timestamp"
        self.cur.execute(stmt,)
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            data = row[0]
        return data

    def get_allhost(self):
        stmt = "SELECT ip FROM parent_ip"
        self.cur.execute(stmt,)
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            data.append(row[0])
        return data

    def get_alltrafficint(self):
        stmt = "SELECT ip, interface FROM traffic_int"
        self.cur.execute(stmt,)
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            data.append([row[0], row[1]])
        return data

    def get_allsqfclient(self):
        stmt = "SELECT ip FROM sqf_client"
        self.cur.execute(stmt,)
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            data.append(row[0])
        return data

    def get_name(self, host):
        stmt = "SELECT name from parent_ip WHERE ip = %(host)s"
        self.cur.execute(stmt, {'host': host})
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            data.append(row[0])
        return data[0]

    #Initialization Data for New Database:----------
    def initialization_uptime(self, ts, host, uptime, message):
        if uptime[0] != 'down':
            stmt = "INSERT INTO uptime(created_at, ip, sysuptime, status, availability, downtime, message) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            self.cur.execute(stmt, (ts, host, int(uptime[1]), 'up', 100, 0, message))
            self.conn.commit()
        else:
            stmt = "INSERT INTO uptime(created_at, ip, sysuptime, status, availability, downtime, message) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            self.cur.execute(stmt, (ts, host, 0, 'down', 0, 0, message))
            self.conn.commit()

    def initialization_traffic(self, ts, host, interface, status, volumeinraw, volumeoutraw, message):
        if status == 'down':
            stmt = "INSERT INTO traffic(created_at, ip, interface, status, availability, volume_in_raw, volume_out_raw, message) VALUES (%s,%s,%s,%s,%s,%s,%s, %s)"
            args = (ts, host, interface, 'down', 0, volumeinraw, volumeoutraw, message)
            self.cur.execute(stmt, args)
            self.conn.commit()
        else:
            stmt = "INSERT INTO traffic(created_at, ip, interface, status, availability, volume_in_raw, volume_out_raw, message) VALUES (%s,%s,%s,%s,%s,%s,%s, %s)"
            args = (ts, host, interface, 'up', 100, volumeinraw, volumeoutraw, message)
            self.cur.execute(stmt, args)
            self.conn.commit()

    def initialization_ping(self, ts, host, pingresult, message):
        if pingresult != 'Request timed out':
            stmt = "INSERT INTO ping(created_at, ip, pingtime, pingmin, pingmax, packetloss, status, availability, message) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            self.cur.execute(stmt, (ts, host, int(pingresult[0]), int(pingresult[1]), int(pingresult[2]), int(pingresult[3]), 'up', 100, message))
            self.conn.commit()
        else:
            stmt = "INSERT INTO ping(created_at, ip, pingtime, pingmin, pingmax, packetloss, status, availability, message) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            self.cur.execute(stmt, (ts, host, 0, 0, 0, 0, 'down', 0, message))
            self.conn.commit()

    def initialization_sqf(self, ts, host, sqf_value, message):
        if sqf_value[0] != 'down':
            stmt = "INSERT INTO sqf(created_at, ip, sqf_value, status, availability, message) VALUES (%s, %s, %s, %s, %s, %s)"
            self.cur.execute(stmt, (ts, host, int(sqf_value[1]), 'up', 100, message))
            self.conn.commit()
        else:
            stmt = "INSERT INTO sqf(created_at, ip, sqf_value, status, availability, message) VALUES (%s, %s, %s, %s, %s, %s)"
            self.cur.execute(stmt, (ts, host, 0,  'down', 0, message))
            self.conn.commit()

    # Delete Data: ----------
    def delete_data(self, parameter, host, interface):
        if parameter == 'traffic':
            stmt = 'DELETE FROM notification WHERE ip = %(host)s AND parameter = %(parameter)s  AND interface = %(interface)s'
            self.cur.execute(stmt, {'host': host, 'parameter': parameter, 'interface': interface})
            self.conn.commit()
        else:
            stmt = 'DELETE FROM notification WHERE ip = %(host)s AND parameter = %(parameter)s'
            self.cur.execute(stmt, {'host': host, 'parameter': parameter})
            self.conn.commit()

    # -------------------------------------------------
    
    """def update_sysdescr(self, sys_descr, host):
        stmt = "UPDATE parent_ip SET sysdescr = %s WHERE ip = %s"
        self.cur.execute(stmt, (sys_descr, host))
        self.conn.commit()

    def update_client_name(self, sys_name, host):
        stmt1 = "UPDATE parent_ip SET name = %s WHERE ip = %s"
        self.cur.execute(stmt1, (sys_name, host))
        stmt2 = "UPDATE traffic_int SET name = %s WHERE ip = %s"
        self.cur.execute(stmt2, (sys_name, host))
        self.conn.commit()"""


    # Update status:
    def update_status_uptime(self, host):
        stmt = "SELECT status FROM uptime WHERE ip = %(host)s ORDER BY id DESC LIMIT 1"
        self.cur.execute(stmt, {'host': host})
        data = self.cur.fetchone()
        stmt = "UPDATE parent_ip SET status_uptime = %s WHERE ip = %s"
        self.cur.execute(stmt, (data, host))
        self.conn.commit()

    def update_statustraffic(self, host, interface, status, availability):
        stmt = "UPDATE traffic_int SET cur_status = %(status)s, availability = %(availability)s WHERE ip = %(host)s AND interface = %(interface)s"
        self.cur.execute(stmt, {'host': host, 'interface': interface, 'status': status, 'availability': availability})
        self.conn.commit()

    def update_statssqf(self, host, value, status, availability):
        if status == "down":
            stmt = "UPDATE sqf_client SET cur_value = %(value)s, cur_status = %(status)s, availability = %(availability)s WHERE ip = %(host)s"
            self.cur.execute(stmt, {'host': host, 'value': value, 'status': status, 'availability': availability})
            self.conn.commit()
        else:
            stmt = "UPDATE sqf_client SET cur_value = %(value)s, cur_status = %(status)s, availability = %(availability)s WHERE ip = %(host)s"
            self.cur.execute(stmt, {'host': host, 'value': value, 'status': status, 'availability': availability})
            self.conn.commit()

    # Add Data: ----------
    def add_uptime(self, ts, host, uptime, availability, downtime, message):
        if uptime != 0:
            stmt = "INSERT INTO uptime (created_at, ip, sysuptime, status, availability, downtime, message) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            self.cur.execute(stmt, (ts, host, int(uptime), 'up', availability, downtime, message))
            self.conn.commit()
        else:
            stmt = "INSERT INTO uptime(created_at, ip, sysuptime, status, availability, downtime, message) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            self.cur.execute(stmt, (ts, host, 0, 'down', availability, downtime, message))
            self.conn.commit()
    
    def add_traffic(self, ts, host, interface, volumetotal, speedtotal, volumein, speedin, volumeout, speedout, status, availability, volumeinraw, volumeoutraw, message):
        if status == 'down':
            stmt = "INSERT INTO traffic(created_at, ip, interface, volume_total, speed_total, volume_in, speed_in, volume_out, speed_out, status, availability, volume_in_raw, volume_out_raw, message) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)"
            args = (ts, host, interface, volumetotal, speedtotal, volumein, speedin, volumeout, speedout, 'down', availability, volumeinraw, volumeoutraw, message)
            self.cur.execute(stmt, args)
            self.conn.commit()
        else:
            stmt = "INSERT INTO traffic(created_at, ip, interface, volume_total, speed_total, volume_in, speed_in, volume_out, speed_out, status, availability, volume_in_raw, volume_out_raw, message) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)"
            args = (ts, host, interface, volumetotal, speedtotal, volumein, speedin, volumeout, speedout, 'up', availability, volumeinraw, volumeoutraw, message)
            self.cur.execute(stmt, args)
            self.conn.commit()

    def add_ping(self, ts, host, pingtime, pingmin, pingmax, packetloss, status, availability, message):
        if status == "down":
            stmt = "INSERT INTO ping(created_at, ip, pingtime, pingmin, pingmax, packetloss, status, availability, message) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            self.cur.execute(stmt, (ts, host, pingtime, pingmin, pingmax, packetloss, 'down', availability , message))
            self.conn.commit()
        else:
            stmt = "INSERT INTO ping(created_at, ip, pingtime, pingmin, pingmax, packetloss, status, availability, message) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            self.cur.execute(stmt, (ts, host, pingtime, pingmin, pingmax, packetloss, 'up', availability , message))
            self.conn.commit()

    def add_sqf(self, ts, host, sqf_value, availability, message):
        if sqf_value != 0:
            stmt = "INSERT INTO sqf(created_at, ip, sqf_value, status, availability, message) VALUES (%s, %s, %s, %s, %s, %s)"
            self.cur.execute(stmt, (ts, host, int(sqf_value), 'up', availability, message))
            self.conn.commit()
        else:
            stmt = "INSERT INTO sqf(created_at, ip, sqf_value, status, availability, message) VALUES (%s, %s, %s, %s, %s, %s)"
            self.cur.execute(stmt, (ts, host, 0, 'down', availability, message))
            self.conn.commit()

    def add_log(self, ts, name, ip, parameter, status, message, interface):
        if parameter == 'uptime':
            stmt = "INSERT INTO logs(created_at, name, ip, parameter, status, message) VALUES (%s,%s,%s,%s,%s,%s)"
            args = (ts, name, ip, 'Uptime', status, message)
            self.cur.execute(stmt, args)
            self.conn.commit()
        elif parameter == 'traffic':
            stmt = "INSERT INTO logs(created_at, name, ip, parameter, status, message, interface) VALUES (%s,%s,%s,%s,%s,%s, %s)"
            args = (ts, name, ip, 'Traffic', status, message, interface)
            self.cur.execute(stmt, args)
            self.conn.commit()
        elif parameter == 'sqf':
            stmt = "INSERT INTO logs(created_at, name, ip, parameter, status, message) VALUES (%s,%s,%s,%s,%s,%s)"
            args = (ts, name, ip, 'Signal Quality Factor', status, message)
            self.cur.execute(stmt, args)
            self.conn.commit()
        elif parameter == 'ping':
            stmt = "INSERT INTO logs(created_at, name, ip, parameter, status, message) VALUES (%s,%s,%s,%s,%s,%s)"
            args = (ts, name, ip, 'Ping', status, message)
            self.cur.execute(stmt, args)
            self.conn.commit()

    # Add down sensor
    def add_notification(self, parameter, ts, name, ip, interface, message, status):
        if parameter == 'uptime':
            stmt = "INSERT INTO notification(parameter, created_at, name, ip, message, status) VALUES (%s,%s,%s,%s,%s,%s)"
            args = ('uptime', ts, name, ip, message, status)
            self.cur.execute(stmt, args)
            self.conn.commit()
        elif parameter == 'traffic':
            stmt = "INSERT INTO notification(parameter, created_at, name, ip, interface, message, status) VALUES (%s,%s,%s,%s,%s,%s,%s)"
            args = ('traffic', ts, name, ip, interface, message, status)
            self.cur.execute(stmt, args)
            self.conn.commit()
        elif parameter == 'sqf':
            stmt = "INSERT INTO notification(parameter, created_at, name, ip, message, status) VALUES (%s,%s,%s,%s,%s,%s)"
            args = ('sqf', ts, name, ip, message, status)
            self.cur.execute(stmt, args)
            self.conn.commit()
        elif parameter == 'ping':
            stmt = "INSERT INTO notification(parameter, created_at, name, ip, message, status) VALUES (%s,%s,%s,%s,%s,%s)"
            args = ('ping', ts, name, ip, message, status)
            self.cur.execute(stmt, args)
            self.conn.commit()

    # Get the first data and the last data from database, and availability data
    def get_diffandavailability(self, host, table, interface):
        if table=="traffic":
            stmt = "SELECT created_at FROM "+table+" WHERE ip = %(host)s AND interface = %(interface)s ORDER BY id ASC LIMIT 1"
            self.cur.execute(stmt, {'host': host, 'interface': interface})
        else:
            stmt = "SELECT created_at FROM "+table+" WHERE ip = %(host)s ORDER BY id ASC LIMIT 1"
            self.cur.execute(stmt, {'host': host})
        firstvalue = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            firstvalue.append(row[0])

        if table=="traffic":
            stmt = "SELECT created_at, availability FROM "+table+" WHERE ip = %(host)s AND interface = %(interface)s ORDER BY id DESC LIMIT 1"
            self.cur.execute(stmt, {'host': host, 'interface': interface})
        else:
            stmt = "SELECT created_at, availability FROM "+table+" WHERE ip = %(host)s ORDER BY id DESC LIMIT 1"
            self.cur.execute(stmt, {'host': host})
        lastvalue = []
        availability = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            lastvalue.append(row[0])
            availability.append(row[1])
        delta = lastvalue[0]-firstvalue[0]
        return [delta.total_seconds(), availability[0]]

    #Get all row the last data in database
    def get_lastrow(self, host, table, interface):
        if table == 'traffic':
            stmt = "SELECT * FROM "+table+" WHERE ip = %(host)s AND interface = %(interface)s ORDER BY id DESC LIMIT 1"
            self.cur.execute(stmt, {'host': host, 'interface': interface})
        elif table == 'uptime':
            stmt = "SELECT * FROM "+table+" WHERE ip = %(host)s ORDER BY id DESC LIMIT 1"
            self.cur.execute(stmt, {'host': host})
        elif table == 'ping':
            stmt = "SELECT * FROM "+table+" WHERE ip = %(host)s ORDER BY id DESC LIMIT 1"
            self.cur.execute(stmt, {'host': host})
        elif table == 'sqf':
            stmt = "SELECT * FROM "+table+" WHERE ip = %(host)s ORDER BY id DESC LIMIT 1"
            self.cur.execute(stmt, {'host': host})
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            for i in range(0, len(row)):
                data.append(row[i])
        return data

    """def get_uptimeavailability(self, host):
        stmt = "(SELECT created_at, status, availability FROM uptime WHERE ip = %(host)s ORDER BY id ASC LIMIT 1) UNION ALL (SELECT created_at, status, availability FROM uptime WHERE ip = %(host)s ORDER BY id DESC LIMIT 1)"
        self.cur.execute(stmt, {'host': host})
        data = []
        while True:
            row = self.cur.fetchone()

            if row == None:
                break

            data.append(row[0],row[1],row[2])
        return data"""

    # Get report data: ----------
    def get_uptimereport(self, length):
        stmt = "SELECT * from uptime ORDER BY id DESC LIMIT "+str(length)
        self.cur.execute(stmt,)
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            data.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]])
        return data

    def get_trafficreport(self, length):
        stmt = "SELECT * from traffic ORDER BY id DESC LIMIT "+str(length)
        self.cur.execute(stmt,)
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            data.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14]])
        return data

    def get_pingreport(self, length):
        stmt = "SELECT * from ping ORDER BY id DESC LIMIT "+str(length)
        self.cur.execute(stmt,)
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            data.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]])
        return data

    def get_sqfreport(self, length):
        stmt = "SELECT * from sqf ORDER BY id DESC LIMIT "+str(length)
        self.cur.execute(stmt,)
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            data.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6]])
        return data
    
    # List Function for Frontend:
    def check_ip(self, host):
        stmt = "SELECT * FROM parent_ip WHERE ip = %(host)s"
        self.cur.execute(stmt, {'host': host})
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            data.append(row)

        if not data:
            return "False"
        else:
            return "True"

    def check_int(self, host, interface):
        stmt = "SELECT * FROM traffic_int WHERE ip = %(host)s AND interface = %(interface)s"
        self.cur.execute(stmt, {'host': host, 'interface': interface })
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            data.append(row)

        if not data:
            return "False"
        else:
            return "True"

    def add_parent(self, name, host, snmp_ver, community_string, sysdescr, syslocation):
        stmt = "INSERT INTO parent_ip(name, ip, snmp_ver, community_string, sysdescr, syslocation) VALUES (%s,%s,%s,%s,%s,%s)"
        self.cur.execute(stmt, (name, host, snmp_ver, community_string, sysdescr, syslocation,))
        self.conn.commit()

    def add_sqf_client(self, name, host):
        stmt = "INSERT INTO sqf_client(name, ip) VALUES (%s,%s)"
        self.cur.execute(stmt, (name, host))
        self.conn.commit()

    def add_int(self, name, host, interface):
        stmt = "INSERT INTO traffic_int (name, ip, interface) VALUES (%s, %s, %s)"
        self.cur.execute(stmt, (name, host, interface))
        self.conn.commit()

    def show_client_data(self):
        stmt = "SELECT name, ip, syslocation, status_uptime, id FROM parent_ip ORDER BY id ASC"
        self.cur.execute(stmt,)
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            data.append([row[0], row[1], row[2], row[3], row[4]])
        return data

    def show_notification(self):
        stmt = "SELECT * FROM notification ORDER BY created_at DESC"
        self.cur.execute(stmt, )
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            data.append([row[0], row[1], row[2].strftime('%Y %B %d - %H:%M:%S') , row[3], row[4], row[5], row[6], row[7]])
        return data

    def filter_client_data_by_id(self, device_id):
        stmt = "SELECT id, name, ip FROM parent_ip WHERE id = %(device_id)s"
        self.cur.execute(stmt, {'device_id': device_id})
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            data.append([row[0], row[1], row[2]])
        return data[0]

    def get_lastrow_logs(self, device_id):
        host = self.filter_client_data_by_id(device_id)
        counter = 0

        stmt = "SELECT COUNT(*) FROM parent_ip WHERE ip = %(host[2])s"
        self.cur.execute(stmt, {'host[2]': host[2]})
        data = self.cur.fetchone()[0]
        counter = counter + data + 2

        stmt = "SELECT COUNT(*) FROM traffic_int WHERE ip = %(host[2])s"
        self.cur.execute(stmt, {'host[2]': host[2]})
        data = self.cur.fetchone()[0]
        counter = counter + data

        stmt = "SELECT * from logs WHERE ip = %(host[2])s ORDER BY created_at DESC LIMIT "+str(counter)
        self.cur.execute(stmt, {'host[2]': host[2]})
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            data.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]])
        
        return data

    def show_uptime(self, device_id):
        host = self.filter_client_data_by_id(device_id)

        stmt = "SELECT * FROM uptime WHERE ip = %(host[2])s ORDER BY created_at DESC"
        self.cur.execute(stmt, {'host[2]': host[2]})
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            data.append([row[0], row[1].strftime('%Y %B %d - %H:%M:%S'), row[2], row[3], row[4], row[5], row[6], row[7]])
        return data

    def show_traffic(self, device_id, interface):
        host = self.filter_client_data_by_id(device_id)

        stmt = "SELECT * FROM traffic WHERE ip = %(host[2])s AND interface = %(interface)s ORDER BY created_at DESC"
        self.cur.execute(stmt, {'host[2]': host[2], 'interface': interface})
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            data.append([row[0], row[1].strftime('%Y %B %d - %H:%M:%S'), row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14]])
        return data

    def show_ping(self, device_id):
        host = self.filter_client_data_by_id(device_id)

        stmt = "SELECT * FROM ping WHERE ip = %(host[2])s ORDER BY created_at DESC"
        self.cur.execute(stmt, {'host[2]': host[2]})
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            data.append([row[0], row[1].strftime('%Y %B %d - %H:%M:%S'), row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]])
        return data

    def show_sqf(self, device_id):
        host = self.filter_client_data_by_id(device_id)

        stmt = "SELECT * FROM sqf WHERE ip = %(host[2])s ORDER BY created_at DESC"
        self.cur.execute(stmt, {'host[2]': host[2]})
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            data.append([row[0], row[1].strftime('%Y %B %d - %H:%M:%S'), row[2], row[3], row[4], row[5], row[6]])
        return data

    def show_log(self):
        stmt = "SELECT * FROM logs ORDER BY created_at DESC"
        self.cur.execute(stmt, )
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            data.append([row[0], row[1].strftime('%Y %B %d - %H:%M:%S'), row[2], row[3], row[4], row[5], row[6], row[7]])
        return data

    def show_uptime_graph(self, device_id):
        host = self.filter_client_data_by_id(device_id)
        stmt = "SELECT created_at, sysuptime FROM uptime WHERE ip = %(host[2])s ORDER BY created_at DESC"
        self.cur.execute(stmt, {'host[2]': host[2]})
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            temp = {"x": 1000*time.mktime(row[0].timetuple()), "y": row[1]*10}
            data.append(temp)
        return data

    def show_traffictot_graph(self, device_id, interface):
        host = self.filter_client_data_by_id(device_id)
        stmt = "SELECT created_at, speed_total FROM traffic WHERE ip = %(host[2])s AND interface = %(interface)s ORDER BY created_at DESC"
        self.cur.execute(stmt, {'host[2]': host[2], 'interface': interface})
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None or row[1] == None:
                break
            temp = {"x": 1000*time.mktime(row[0].timetuple()), "y": row[1]}
            data.append(temp)
        return data

    def show_trafficin_graph(self, device_id, interface):
        host = self.filter_client_data_by_id(device_id)
        stmt = "SELECT created_at, speed_in FROM traffic WHERE ip = %(host[2])s AND interface = %(interface)s ORDER BY created_at DESC"
        self.cur.execute(stmt, {'host[2]': host[2], 'interface': interface})
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None or row[1] == None:
                break
            temp = {"x": 1000*time.mktime(row[0].timetuple()), "y": row[1]}
            data.append(temp)
        return data

    def show_trafficout_graph(self, device_id, interface):
        host = self.filter_client_data_by_id(device_id)
        stmt = "SELECT created_at, speed_out FROM traffic WHERE ip = %(host[2])s AND interface = %(interface)s ORDER BY created_at DESC"
        self.cur.execute(stmt, {'host[2]': host[2], 'interface': interface})
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None or row[1] == None:
                break
            temp = {"x": 1000*time.mktime(row[0].timetuple()), "y": row[1]}
            data.append(temp)
        return data

    def show_pingtime_graph(self, device_id):
        host = self.filter_client_data_by_id(device_id)
        stmt = "SELECT created_at, pingtime FROM ping WHERE ip = %(host[2])s ORDER BY created_at DESC"
        self.cur.execute(stmt, {'host[2]': host[2]})
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None or row[1] == None:
                break
            temp = {"x": 1000*time.mktime(row[0].timetuple()), "y": row[1]}
            data.append(temp)
        return data

    def show_pingmax_graph(self, device_id):
        host = self.filter_client_data_by_id(device_id)
        stmt = "SELECT created_at, pingmax FROM ping WHERE ip = %(host[2])s ORDER BY created_at DESC"
        self.cur.execute(stmt, {'host[2]': host[2]})
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None or row[1] == None:
                break
            temp = {"x": 1000*time.mktime(row[0].timetuple()), "y": row[1]}
            data.append(temp)
        return data

    def show_pingmin_graph(self, device_id):
        host = self.filter_client_data_by_id(device_id)
        stmt = "SELECT created_at, pingmin FROM ping WHERE ip = %(host[2])s ORDER BY created_at DESC"
        self.cur.execute(stmt, {'host[2]': host[2]})
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None or row[1] == None:
                break
            temp = {"x": 1000*time.mktime(row[0].timetuple()), "y": row[1]}
            data.append(temp)
        return data

    def show_sqf_graph(self, device_id):
        host = self.filter_client_data_by_id(device_id)
        stmt = "SELECT created_at, sqf_value FROM sqf WHERE ip = %(host[2])s ORDER BY created_at DESC"
        self.cur.execute(stmt, {'host[2]': host[2]})
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            temp = {"x": 1000*time.mktime(row[0].timetuple()), "y": row[1]}
            data.append(temp)
        return data

    def counter_sensor(self):
        counter= 0
        stmt = "SELECT COUNT(*) FROM parent_ip"
        self.cur.execute(stmt, )
        data = self.cur.fetchone()[0]
        counter = counter + (data * 3)

        stmt = "SELECT COUNT(*) FROM traffic_int"
        self.cur.execute(stmt,)
        data = self.cur.fetchone()[0]
        counter = counter + data
        
        return counter

    def show_uptime_sparkline(self, device_id):
        host = self.filter_client_data_by_id(device_id)
        stmt = "SELECT sysuptime FROM uptime WHERE ip = %(host[2])s ORDER BY created_at ASC"
        self.cur.execute(stmt, {'host[2]': host[2]})
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            data.append(row[0]/100)
        return data

    def show_traffic_sparkline(self, device_id, interface):
        host = self.filter_client_data_by_id(device_id)
        stmt = "SELECT speed_total FROM traffic WHERE ip = %(host[2])s AND interface = %(interface)s ORDER BY created_at ASC"
        self.cur.execute(stmt, {'host[2]': host[2], 'interface': interface})
        data = []
        row = self.cur.fetchone()
        if row == (None,):
            pass
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            data.append(row[0])
        return data

    def show_ping_sparkline(self, device_id):
        host = self.filter_client_data_by_id(device_id)
        stmt = "SELECT pingtime FROM ping WHERE ip = %(host[2])s ORDER BY created_at ASC"
        self.cur.execute(stmt, {'host[2]': host[2]})
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            data.append(row[0])
        return data

    def show_sqf_sparkline(self, device_id):
        host = self.filter_client_data_by_id(device_id)
        stmt = "SELECT sqf_value FROM sqf WHERE ip = %(host[2])s ORDER BY created_at ASC"
        self.cur.execute(stmt, {'host[2]': host[2]})
        data = []
        while True:
            row = self.cur.fetchone()
            if row == None:
                break
            data.append(row[0])
        return data

    def export(self, table, host, filename, interface=0):
        directory = "'/tmp/"+filename+".csv'"
        if table == 'uptime':
            query = "SELECT id, created_at, sysuptime, availability, message FROM "+table+" where ip = %(host)s"
            stmt = "COPY ("+query+") TO "+directory+" DELIMITER ',' CSV HEADER"
            self.cur.execute(stmt, {'host': host})
        elif table == 'traffic':
            query = "SELECT id, created_at, interface, volume_total, speed_total,volume_in, speed_in, volume_out, speed_out, availability, message FROM "+table+" where ip = %(host)s AND interface = %(interface)s"
            stmt = "COPY ("+query+") TO "+directory+" DELIMITER ',' CSV HEADER"
            self.cur.execute(stmt, {'host': host, 'interface': interface})
        elif table == "ping":
            query = "SELECT id, created_at, pingtime, pingmin, pingmax, packetloss, availability, message FROM "+table+" where ip = %(host)s"
            stmt = "COPY ("+query+") TO "+directory+" DELIMITER ',' CSV HEADER"
            self.cur.execute(stmt, {'host': host})
        elif table == "sqf":
            query = "SELECT id, created_at, sqf_value, availability, message FROM "+table+" where ip = %(host)s"
            stmt = "COPY ("+query+") TO "+directory+" DELIMITER ',' CSV HEADER"
            self.cur.execute(stmt, {'host': host})


