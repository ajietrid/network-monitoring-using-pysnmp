import subprocess
import platform
import re

class PingHelper:
    def ping(self, host):
        try:
            # Option for the number of packets as a function of
            param = '-n' if platform.system().lower()=='windows' else '-c'
            # Building the command. Ex: "ping -c 1 google.com"
            command = ['ping', param, '4', host]
            output = subprocess.check_output(command).decode("utf-8")
            output = output.split('\n')[-3:]
            # -1 is a blank line, -3 & -2 contain the actual results
            xmit_stats = output[0].split(",")
            timing_stats = output[1].split("=")[1].split("/")

            if "duplicates" in xmit_stats[2]:
                packet_loss = float(xmit_stats[3].split("%")[0])
            else:
                packet_loss = float(xmit_stats[2].split("%")[0])

            ping_min = float(timing_stats[0])
            ping_avg = float(timing_stats[1])
            ping_max = float(timing_stats[2])
            return [ping_avg, ping_min, ping_max, packet_loss]

        except subprocess.CalledProcessError as e:
            return "Request timed out"