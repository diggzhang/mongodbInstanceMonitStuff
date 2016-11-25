# encoding: utf-8
#!/usr/bin/env python
import inspect
import time
import urllib, urllib2
import json
import socket
import os
import statvfs
import sys
import smtplib
from email.mime.text import MIMEText
import subprocess
import datetime


"""
    程序最终效果：
    1. 自动检测mongodb状态，如果mongodb挂掉，自动重启 done
    2. 系统处于高耗状态，或者硬盘快满，报警 done
    3. 报警可以自动发邮件 done
    4. 后期自动钉钉
"""


# mail configure
mailto_list = ["1192309514@qq.com"]
mail_host = "smtp.126.com"
mail_user = "guangheauto"
mail_pass = "hello123"  # guanghedev
mail_postfix = "126.com"


main_mongo_instance_port = 27017


"""
    check mongodb crash or not
"""
def mongo_crash_or_not(mongo_instance_port):
    res = subprocess.Popen('ps -ef | grep /usr/bin/mongod | grep -v grep', stdout=subprocess.PIPE, shell=True)
    res_output_lines = res.stdout.readlines()
    for line in res_output_lines:
        print("%s")%(line)
    if len(res_output_lines) == 0:
        return True
    else:
        return False


"""
    Monit on mongodb instance
    If mongo crash down then restart mongo by systemctl
"""
def monit_mongo(mongo_instance_port):
    print("MongoDB start at port: %s")%(mongo_instance_port)
    crash = mongo_crash_or_not(mongo_instance_port)
    if crash == True:
        subprocess.call(' '.join(["echo", "yangcong345", "|", "sudo", "-S", "sudo", "systemctl", "restart", "mongod.service"]), shell=True)
        return "Mongo crash down systemctl restart it."
    else:
        return "Mongo running healthy."


def fetchMsg(log_location):
    file_object = open(str(log_location))
    try:
        all_the_text = file_object.read()
    finally:
        file_object.close()
    msg = all_the_text
    return msg


def sendMail(toList, subject, content):
    me = mail_user + "<" + mail_user + "@" + mail_postfix + ">"
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = ";".join(toList)
    try:
        s = smtplib.SMTP()
        s.connect(mail_host)
        s.login(mail_user, mail_pass)
        s.sendmail(me, toList, msg.as_string())
        s.close()
        return True
    except Exception, e:
        print str(e)
        return False


class monitor(object):
    """
        system monitor base class.
    """
    def __init__(self):
        self.data = {}

    def sys_current_time(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def sys_host_name(self):
        return socket.gethostname()

    def sys_cpu_load_avge(self):
        with open("/proc/loadavg") as load_avg_info:
            la_info_str = load_avg_info.read().split()[:3]
            return ",".join(la_info_str)

    def sys_mem_total_info(self):
        with open("/proc/meminfo") as mem_info:
            mem_info_num = int(mem_info.readline().split()[1])
            return mem_info_num / 1024

    def sys_mem_available_info(self):
        with open("/proc/meminfo") as mem_info:
            for line in mem_info:
                if line.startswith("MemAvailable"):
                    mem_ava_num = int(line.split()[1])
                    return mem_ava_num / 1024

    def sys_hard_disk_stat(self, *args):
        disk_stat = {}
        for arg in args:
            disk = os.statvfs(arg)
            percent = (disk.f_blocks - disk.f_bfree) * 100 / (disk.f_blocks -disk.f_bfree + disk.f_bavail)
            disk_stat[arg] = percent
        return disk_stat


def post_man(mail_title, mail_log):
    mail_title = mail_title + " Server WARNING"
    try:
        if sendMail(mailto_list, mail_title, mail_log):
            print("[*] SEND SUCCESS title: %s") % (mail_title)
            sys.exit()
        else:
            print("[*] SEND FAILURE title: %s") % (mail_title)
    except Exception, e:
        print(str(e))
        raise


def print_log(log_host, log_time, log_type, log_value):
    print("%s |%s | %s | %s")%(log_host, log_time, log_type, log_value)


"""
    monitor CPU load and RAM/DISK
"""


C_CPU_LOAD = "Current CPU load"
MEM_CONS = "Mem consumption"
DISK_INFO = "Disk space"
BASE_MEM_CONS = 0.03
BASE_DISK_USE = 85


if __name__ == "__main__":
    """ monit on mongo instance """
    mongo_running_stat = monit_mongo(main_mongo_instance_port)

    """ monit on system load  """
    this_sys_monitor_info_stuff = monitor()
    host_name = this_sys_monitor_info_stuff.sys_host_name()
    current_time = this_sys_monitor_info_stuff.sys_current_time()
    current_cpu_load = this_sys_monitor_info_stuff.sys_cpu_load_avge()
    total_mem_mb = this_sys_monitor_info_stuff.sys_mem_total_info()
    available_mem_mb = this_sys_monitor_info_stuff.sys_mem_available_info()
    mem_consumption = float(available_mem_mb) / total_mem_mb
    disk_stat = this_sys_monitor_info_stuff.sys_hard_disk_stat("/home", "/databackup")

    """
     if Total 31GB RAM available mem only left less than 1GB
     && Disk space left less than 15%
     then Send WARNING Mail
    """
    send_mail = False
    print_log(host_name, current_time, C_CPU_LOAD, current_cpu_load)

    if mem_consumption <= BASE_MEM_CONS:
        send_mail = True
        print_log(host_name, current_time, MEM_CONS, mem_consumption)
    else:
        print_log(host_name, current_time, MEM_CONS, mem_consumption)

    for disk_name in disk_stat:
        if disk_stat[disk_name] >= BASE_DISK_USE:
            send_mail = True
            print_log(host_name, current_time, DISK_INFO, disk_name + " " +str(disk_stat[disk_name]) + "%")
        else:
            print_log(host_name, current_time, DISK_INFO, disk_name + " " + str(disk_stat[disk_name]) + "%")

    if send_mail:
        mail_info = "time: %s, \nhost: %s, \ncpu load: %s, \nmem cons: %s, \ndisk stat: %s, \nmongo stat: %s"%(current_time, host_name, current_cpu_load,
                                                                                                                mem_consumption, disk_stat, mongo_running_stat)
        post_man(current_time, mail_info)
    else:
        mail_info = "time: %s, \nhost: %s, \ncpu load: %s, \nmem cons: %s, \ndisk stat: %s, \nmongo stat: %s"%(current_time, host_name, current_cpu_load,
                                                                                                                mem_consumption, disk_stat, mongo_running_stat)
        # post_man(current_time, mail_info)
