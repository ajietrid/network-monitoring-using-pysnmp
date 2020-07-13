import psutil

def get_cpu_util():
    percentage = psutil.cpu_percent(interval=1)
    freq = psutil.cpu_freq()
    return [float(percentage), round(freq[0]/1000, 2)]

def get_memory():
    mem = psutil.virtual_memory()
    used = round((mem[0]-mem[1])/1000000000, 2)
    total = round(mem[0]/1000000000, 2)
    percentage_used = round(mem[2])
    return [used, total, percentage_used]

class SelfMonitoring():
    def get_pc_stats(self):
        cpu_util = get_cpu_util()
        memory = get_memory()
        return [cpu_util, memory]