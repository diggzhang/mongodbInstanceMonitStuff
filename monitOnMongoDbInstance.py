# encoding: utf-8
import os, sys
import subprocess


main_mongo_instance_port = 27017


"""
    check mongodb crash or not
"""
def mongo_crash_or_not(mongo_instance_port):
    res = subprocess.Popen('ps -ef | grep /usr/bin/mongod | grep -v grep', stdout=subprocess.PIPE, shell=True)
    res_output_lines = res.stdout.readlines()
    print("MongoDB Instance {ps -ef} Info: %s")%(res_output_lines)
    if len(res_output_lines) == 0:
        return True
    else:
        return False


"""
    monit on mongodb instance
    if mongo crash down then restart mongo by systemctl
"""
def monit_mongo(mongo_instance_port):
    print("MongoDB start at port: %s")%(mongo_instance_port)
    crash = mongo_crash_or_not(mongo_instance_port)
    if crash == True:
        subprocess.call(' '.join(["echo", "yangcong345", "|", "sudo", "-S", "sudo", "systemctl", "restart", "mongod.service"]), shell=True)
    else:
        print("MongoDB Instance Running Well ...")


if __name__ == '__main__':
    try:
        monit_mongo(main_mongo_instance_port)
    except Exception as e:
        print("MongoDB Instance restart failed")
        print(sys.exc_info())
        raise
