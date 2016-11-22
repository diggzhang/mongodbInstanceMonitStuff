# encoding: utf-8
import os, sys
import subprocess
import datetime


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
        print("Mongo crash down systemctl restart it now ...")
    else:
        print("Mongo running now ...")


def mem_monit():
    Sys_Mem_Use = os.popen("free | grep Mem | awk '{print $3}'").read()
    Sys_Mem_Use=str(int(Sys_Mem_Use)/1024)
    print("Mem spend %sGB")%(Sys_Mem_Use[0:2])


def cpu_load_monit():
    Sys_Cpu_Use=os.popen("vmstat | grep -v procs | grep -v swpd | awk '{print $13}'").read()
    Sys_Cpu_Use=int(Sys_Cpu_Use)
    print("CPU load %s")%(Sys_Cpu_Use)


if __name__ == '__main__':
    try:
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        monit_mongo(main_mongo_instance_port)
        cpu_load_monit()
        mem_monit()
    except Exception as e:
        print("MongoDB instance restart failed")
        print(sys.exc_info())
        raise
