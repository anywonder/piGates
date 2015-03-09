#!/usr/bin/env python

from hotqueue import HotQueue
import piface.pfio as pfio
import redis

pfio.init()

queue = HotQueue("myqueue", host="localhost", port=6379, db=0)
statusServer = redis.Redis("localhost")

statusServer.setnx("status", "closed")
currentStatus = statusServer.get("status")

if currentStatus == 'open':
	pfio.digital_write(0,1)
else:
	pfio.digital_write(0,0)
	

for item in queue.consume():
	print item
	if item == 'open':
		pfio.digital_write(0,1)
		statusServer.set("status", "open")
	if item == 'close':
		pfio.digital_write(0,0)
		statusServer.set("status", "closed")
	if item == 'exit':
		exit(0)

