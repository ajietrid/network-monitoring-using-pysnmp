from email.mime.text import MIMEText
import smtplib

class EmailHelper():
    def send_email(self, uptime, traffic, ping, sqf):
        fromaddr = "nmsdimasajie@gmail.com"
        toaddr = "nmsdimasajie@gmail.com"

        htmlopen = open("emailtemplate.html")
        htmlread = htmlopen.read()

        htmlread = htmlread.replace("$(uptime)", str(uptime))
        htmlread = htmlread.replace("$(traffic)", str(traffic))
        htmlread = htmlread.replace("$(ping)", str(ping))
        htmlread = htmlread.replace("$(sqf)", str(sqf))
        htmlread = htmlread.replace("$(totalsensordown)", str(uptime+traffic+ping+sqf))

        msg = MIMEText(htmlread, 'html')
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "NMS ALERT"

        debug = False
        if debug:
            print(msg.as_string())
        else:
            server = smtplib.SMTP('smtp.gmail.com',587)
            server.starttls()
            server.login("nmsdimasajie@gmail.com", "MiPuU5288YJbpfW")
            text = msg.as_string()
            server.sendmail(fromaddr, toaddr, text)
            server.quit()