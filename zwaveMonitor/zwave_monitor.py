#!/usr/bin/env python

import subprocess, shlex
import os
import time
import sys, gc
import signal
import atexit
from time import sleep
import sqlite3 as lite

con = None
procs = {}

def exit_handler(myprocs):
    for ip, proc in myprocs.items():
        if proc is not None:
            print ip
            os.killpg(proc.pid, signal.SIGTERM)

atexit.register(exit_handler, myprocs=procs)

def startMonitor(controller):
    #print "startMonitor %s" % (controller['name'])
    args = '/usr/local/bin/node /home/pi/Projects/Django/zwaveMonitor/zwaveControllerUpdates.js '
    args += str(controller['id'])
    # FNULL = open(os.devnull, 'w')
    #proc = subprocess.Popen(args, shell=True, preexec_fn=os.setsid, stdout=FNULL, stderr=subprocess.STDOUT)
    proc = subprocess.Popen(args, shell=True, preexec_fn=os.setsid, stderr=subprocess.STDOUT)
    return proc

try:
    print "Connecting to db"
    con = lite.connect('/home/pi/Projects/Django/myGates/mygatesdb')
    con.row_factory = lite.Row
    cur = con.cursor()

    while True:
        sleep(10)
        cur.execute("SELECT * FROM zwave_zwavecontroller")

        rows = cur.fetchall()
        cur_ctls = []
        for row in rows:
            cur_ctls.append(row['ipaddress'])
            if row['ipaddress'] not in procs:
                print "%s needs added" % (row['ipaddress'])
                procs[row['ipaddress']] = startMonitor(row)

        for ip, proc in procs.items():
            if ip not in cur_ctls:
                print "%s needs removed" % (ip)
                if proc is not None:
                    os.killpg(proc.pid, signal.SIGTERM)
                    proc = None
                del procs[ip]




except lite.Error, e:
    print "Error %s:" % e.args[0]
    sys.exit(1)

finally:
    if con:
        con.close()
    






