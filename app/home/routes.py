# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from app.home import blueprint
from flask import render_template, redirect, url_for, request, flash, send_file
from flask_login import login_required, current_user
from app import login_manager
from jinja2 import TemplateNotFound

import json

from app.base.forms import AddNewIPphaseone, AddNewIPphasetwo, AddNewInterface
from backend.dbhelper import DBHelper
from backend.snmphelper import SNMPhelper
from backend.selfmonitoringhelper import SelfMonitoring

dbhelp = DBHelper()
snmphelp = SNMPhelper()
smhelp = SelfMonitoring()

alarm_notification = dbhelp.show_notification()
counter = len(alarm_notification)
client = dbhelp.show_client_data()
all_sensor = dbhelp.counter_sensor()

@blueprint.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    selfmon = smhelp.get_pc_stats()
    #if not current_user.is_authenticated:
    #return redirect(url_for('base_blueprint.login'))
    phaseoneform = AddNewIPphaseone(request.form)
    if 'addnewipphaseone' in request.form:

        # read form data
        ip = request.form['ip']

        if dbhelp.check_ip(ip) == "False":
            return redirect(url_for('home_blueprint.addnewipphasetwo', ip=ip, alarm = alarm_notification, counter= counter))
        else:
            client = dbhelp.show_client_data()
            return render_template('index.html', msg='IP is already on the database.', form=phaseoneform, client= client, alarm = alarm_notification, counter= counter, all_sensor= all_sensor, selfmon = selfmon)
    
    client = dbhelp.show_client_data()
        # Something (user or pass) is not ok
    return render_template('index.html', form =phaseoneform, client = client, alarm = alarm_notification, counter= counter, all_sensor= all_sensor, selfmon = selfmon)

@blueprint.route('/addnewipnext/<ip>', methods=['GET', 'POST'])
@login_required
def addnewipphasetwo(ip):
    phasetwoform = AddNewIPphasetwo(request.form)

    if 'addnewipphasetwo' in request.form:

        # read form data
        ip = request.form['ip']
        while dbhelp.check_ip(ip) == "True":
            return render_template('addnewparentnext.html', msg='IP is already on the database.', form=phasetwoform, alarm = alarm_notification, counter= counter)
        name = request.form['name']
        sysdescr = request.form['sysdescr']
        syslocation = request.form['syslocation']
        snmp_ver = request.form['snmp_ver']
        community_string = request.form['community_string']


        dbhelp.add_parent(name, ip, snmp_ver, community_string, sysdescr, syslocation)
        dbhelp.add_sqf_client( name, ip)
        flash('IP has successfully been added.')
        return redirect(url_for('home_blueprint.index'))

    name = snmphelp.get_sysname(ip)
    if name[0] == 'error':
        sysname = ""
    else:
        sysname = name[1]
    descr = snmphelp.get_sysdescr(ip)
    if descr[0] == 'error':
        sysdescr = ""
    else: 
        sysdescr = descr[1]
    location = snmphelp.get_syslocation(ip)
    if location[0] == 'error':
        syslocation = ""
    else:
        syslocation = location[1]

    return render_template('addnewparentnext.html', form=phasetwoform, ipv=ip, sysnamev=sysname, sysdescrv=sysdescr, syslocationv=syslocation, alarm = alarm_notification, counter= counter)


@blueprint.route('/device/<device_id>', methods=['GET', 'POST'])
@login_required
def device_template(device_id):  
    selfmon = smhelp.get_pc_stats()  
    data_by_id = dbhelp.filter_client_data_by_id(device_id)
    lastrow_log = dbhelp.get_lastrow_logs(device_id)

    uptime_sparkline = dbhelp.show_uptime_sparkline( device_id)
    traffic_sparkline_23 = dbhelp.show_traffic_sparkline( device_id, 23)
    traffic_sparkline_24 = dbhelp.show_traffic_sparkline( device_id, 24)
    ping_sparkline = dbhelp.show_ping_sparkline(device_id)
    sqf_sparkline = dbhelp.show_sqf_sparkline(device_id)
    #if not current_user.is_authenticated:
    #    return redirect(url_for('base_blueprint.login'))

    try:
        data_by_id = dbhelp.filter_client_data_by_id(device_id)
        lastrow_log = dbhelp.get_lastrow_logs(device_id)
        interfaceform = AddNewInterface(request.form)
        if 'addnewinterface' in request.form:
            interface = request.form['interface']
            while dbhelp.check_int(data_by_id[2], interface) == "True":
                
                return render_template('device.html', msg='Interface is already on the database.', form=interfaceform, logs = lastrow_log, by_id= data_by_id, uptime_sparkline= uptime_sparkline, traffic_sparkline_23=traffic_sparkline_23, traffic_sparkline_24 = traffic_sparkline_24, ping_sparkline=ping_sparkline, sqf_sparkline=sqf_sparkline, client = client, alarm = alarm_notification, counter= counter, selfmon = selfmon)

            name = data_by_id[1]
            host = data_by_id[2]
            dbhelp.add_int(name, host, interface)
            flash('Interface has successfully been added.')
            return redirect(url_for('home_blueprint.index'))               
        
        return render_template('device.html', form=interfaceform, by_id=data_by_id, logs = lastrow_log, uptime_sparkline= uptime_sparkline, traffic_sparkline_23=traffic_sparkline_23, traffic_sparkline_24 = traffic_sparkline_24, ping_sparkline=ping_sparkline, sqf_sparkline=sqf_sparkline,  client = client, alarm = alarm_notification, counter= counter, selfmon = selfmon)

    except TemplateNotFound:
        return render_template('page-404.html'), 404
    
    except:
        return render_template('page-500.html'), 500


@blueprint.route('/device/<device_id>/uptime')
@login_required
def uptime_template(device_id):
    selfmon = smhelp.get_pc_stats()
    data_by_id = dbhelp.filter_client_data_by_id(device_id)
    uptime = dbhelp.show_uptime(device_id)
    uptime_graph = dbhelp.show_uptime_graph(device_id)
    host = data_by_id[2]
    ts = dbhelp.get_currenttimestamp()

    #if not current_user.is_authenticated:
    #    return redirect(url_for('base_blueprint.login'))

    try:

        return render_template('uptime.html',uptime= uptime, uptime_graph= uptime_graph, client = client, alarm = alarm_notification, counter= counter, selfmon = selfmon, host=host, ts=ts, by_id= data_by_id)

    except TemplateNotFound:
        return render_template('page-404.html'), 404
    
    except:
        return render_template('page-500.html'), 500


@blueprint.route('/device/<device_id>/traffic/<interface>')
@login_required
def traffic_template(device_id, interface):
    selfmon = smhelp.get_pc_stats()
    data_by_id = dbhelp.filter_client_data_by_id(device_id)
    traffic = dbhelp.show_traffic(device_id, interface)
    traffic_tot = dbhelp.show_traffictot_graph(device_id, interface)
    traffic_in = dbhelp.show_trafficin_graph(device_id, interface)
    traffic_out = dbhelp.show_trafficout_graph(device_id, interface)
    host = data_by_id[2]
    ts = dbhelp.get_currenttimestamp()
    interface = interface
    #if not current_user.is_authenticated:
    #    return redirect(url_for('base_blueprint.login'))
    try:

        return render_template('traffic.html',traffic= traffic, traffic_tot=traffic_tot, traffic_in=traffic_in, traffic_out=traffic_out, client = client, alarm = alarm_notification, counter= counter, selfmon = selfmon, host=host, ts=ts, interface=interface, by_id= data_by_id)

    except TemplateNotFound:
        return render_template('page-404.html'), 404
    
    except:
        return render_template('page-500.html'), 500

@blueprint.route('/device/<device_id>/ping')
@login_required
def ping_template(device_id):
    selfmon = smhelp.get_pc_stats()
    data_by_id = dbhelp.filter_client_data_by_id(device_id)
    ping = dbhelp.show_ping(device_id)
    pingtime = dbhelp.show_pingtime_graph(device_id)
    pingmax = dbhelp.show_pingmax_graph(device_id)
    pingmin = dbhelp.show_pingmin_graph(device_id)
    host = data_by_id[2]
    ts = dbhelp.get_currenttimestamp()

    #if not current_user.is_authenticated:
    #    return redirect(url_for('base_blueprint.login'))

    try:

        return render_template('ping.html',ping= ping, pingtime=pingtime, pingmax=pingmax, pingmin=pingmin, client = client, alarm = alarm_notification, counter= counter, selfmon = selfmon, host=host, ts=ts, by_id= data_by_id)

    except TemplateNotFound:
        return render_template('page-404.html'), 404
    
    except:
        return render_template('page-500.html'), 500

@blueprint.route('/device/<device_id>/sqf')
@login_required
def sqf_template(device_id):
    selfmon = smhelp.get_pc_stats()
    data_by_id = dbhelp.filter_client_data_by_id(device_id)
    sqf = dbhelp.show_sqf(device_id)
    sqf_graph = dbhelp.show_sqf_graph(device_id)
    host = data_by_id[2]
    ts = dbhelp.get_currenttimestamp()

    #if not current_user.is_authenticated:
    #    return redirect(url_for('base_blueprint.login'))

    try:
        return render_template('sqf.html',sqf= sqf, sqf_graph=sqf_graph, client = client, alarm = alarm_notification, counter= counter, selfmon = selfmon, host=host, ts=ts, by_id= data_by_id)

    except TemplateNotFound:
        return render_template('page-404.html'), 404
    
    except:
        return render_template('page-500.html'), 500

@blueprint.route('/download/<table>/<host>/<ts>/<interface>')
@login_required
def download_template(table, host, ts, interface):
    filename = table + "_" + host + "_" + str(ts) + "_" + str(interface)
    path = "/tmp/"+filename+".csv"
    dbhelp.export(table, host, filename, interface=0)
    
    return send_file(path, as_attachment=True)
    #if not current_user.is_authenticated:
    #    return redirect(url_for('base_blueprint.login'))
    

@blueprint.route('/<template>')
@login_required
def route_template(template):
    selfmon = smhelp.get_pc_stats()
    logs = dbhelp.show_log()
    #if not current_user.is_authenticated:
    #    return redirect(url_for('base_blueprint.login'))
    try:
        return render_template(template + '.html', client= client, logs= logs, counter=counter, alarm=alarm_notification, selfmon = selfmon)
    except TemplateNotFound:
        return render_template('page-404.html'), 404 
    except:
        return render_template('page-500.html'), 500

