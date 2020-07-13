from pysnmp.hlapi import *
from pysnmp import hlapi
import math

class SNMPhelper:
  def get_uptime(self, host, port=161):
    try:
      errorIndication, errorStatus, errorIndex, varBinds = next(getCmd(SnmpEngine(), CommunityData('public', mpModel=0),UdpTransportTarget((host, port),retries=5),ContextData(),ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysUpTime', 0)))
            )
      if errorIndication:
        return ['down', str(errorIndication)]
      elif errorStatus:
        return ['down', str(('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?')))]
      else:
        for varBind in varBinds:
          for x in varBind:
            a = (' = '.join([x.prettyPrint() for x in varBind]))
        return ['up', int(x)]
    except:
      return ['down', 'timeout']

  def get_uptimev2(self, host):
    uptime = self.get_uptime(host)
    return [time.time(), host, uptime]

  def get_uptime_str(self, uptime):
    raw = uptime/100/60/60/24
    day = math.floor(raw)
    hour = (raw - day) * 24
    minute = (hour - math.floor(hour)) * 60
    second = (minute - math.floor(minute)) * 60
    
    data = str(int(math.floor(uptime/100/60/60/24))) + "d " + str(int(math.floor(hour))) + "h " +  str(int(math.floor(minute))) + "m " + str(int(math.floor(second))) + "s"
    return data

  def get_sysdescr(self, host, port=161):
    try:
      errorIndication, errorStatus, errorIndex, varBinds = next(getCmd(SnmpEngine(),CommunityData('public', mpModel=0), UdpTransportTarget((host, port),retries=5), ContextData(),ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)))
      )
      if errorIndication:
        return ['error', str(errorIndication)]
      elif errorStatus:
        return ['error', str(('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?')))]
      else:
        for varBind in varBinds:
          for x in varBind:
            a = (' = '.join([x.prettyPrint() for x in varBind]))
        return ['success', x]
    except:
      return ['error', 'timeout']

  def get_syslocation(self, host, port=161):
    try:
      errorIndication, errorStatus, errorIndex, varBinds = next(getCmd(SnmpEngine(),CommunityData('public', mpModel=0),UdpTransportTarget((host, port),retries=5),ContextData(),ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysLocation', 0)))
      )
      if errorIndication:
        return ['error', str(errorIndication)]
      elif errorStatus:
        return ['error', str(('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?')))]
      else:
        for varBind in varBinds:
          for x in varBind:
            a = (' = '.join([x.prettyPrint() for x in varBind]))
        return ['success', x]
    except:
      return ['error', 'timeout']

  def get_sysname(self, host, port=161):
    try:
      errorIndication, errorStatus, errorIndex, varBinds = next(getCmd(SnmpEngine(),CommunityData('public', mpModel=0),UdpTransportTarget((host, port),retries=5),ContextData(),ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysName', 0)))
      )
      if errorIndication:
        return ['error', str(errorIndication)]
      elif errorStatus:
        return ['error', str(('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?')))]
      else:
        for varBind in varBinds:
          for x in varBind:
            a = (' = '.join([x.prettyPrint() for x in varBind]))
        return ['success', x]
    except:
      return ['error', 'timeout']

  def get_traffic(self, host, interface, port=161):
    try:
      errorIndication, errorStatus, errorIndex, varBinds = next(getCmd(SnmpEngine(),CommunityData('public', mpModel=0), UdpTransportTarget((host, port),retries=5),ContextData(), ObjectType(ObjectIdentity('.1.3.6.1.2.1.2.2.1.10.'+str(interface))), ObjectType(ObjectIdentity('.1.3.6.1.2.1.2.2.1.16.'+str(interface))))
      )
      if errorIndication:
        return ['down', str(errorIndication)]
      elif errorStatus:
        return ['down', str(('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?')))]
      else:
        return ['up', int(varBinds[0][1]), int(varBinds[1][1])]
    except:
      return ['down', 'timeout']

  def get_sqf(self, host, port=161, oid='1.3.6.1.4.1.303.3.3.45.12.10.1.15.0'):
    try:
      errorIndication, errorStatus, errorIndex, varBinds = next(getCmd(SnmpEngine(),CommunityData('public', mpModel=0),UdpTransportTarget((host, port),retries=5),ContextData(),ObjectType(ObjectIdentity(oid)))
      )
      if errorIndication:
        return ['down', str(errorIndication)]
      elif errorStatus:
        return ['down', str(('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?')))]
      else:
        return ['up', int(varBinds[0][1])]
    except:
      return ['down', 'timeout']
