"""Script to test cross instance / code language commuincation via SQLite3"""

import sqlite3
import sys
import os
import datetime
import subprocess
import signal
import time

def checkPy3Run(dbName):
	"""Check status of db ctrl value"""
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	c.execute("select value from ctrl where name = 'py3run'")
	status = c.fetchone()[0]
	conn.close()
	return status

def checkRun(dbName):
	"""Check status of db ctrl value"""
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	c.execute("select value from ctrl where name = 'run'")
	status = c.fetchone()[0]
	conn.close()
	return status

def getTimeStr():
	"""return time as string"""
	now = datetime.datetime.now()
	return now.strftime("%Y-%m-%d %H:%M:%S.%f")

def getms():
	"""return milliseconds"""
	now = datetime.datetime.now()
	ms = float(now.strftime('%f'))/1000
	return ms


print(sys.version)

dbName = 'test.db'
limit = 100.0 # number of times to update value

conn = sqlite3.connect(dbName)

c = conn.cursor()

# clear any previous ctrl table if it exists
try:
	c.execute('drop table ctrl')
	conn.commit()
except sqlite3.OperationalError as e:
	print('error caught:')
	print(e)

# clear any previous data table if it exists
try:
	c.execute('drop table data')
	conn.commit()
except sqlite3.OperationalError as e:
	print('error caught:')
	print(e)

#create new ctrl table, with auto increment ndx
c.execute("""create table ctrl
	(ndx integer primary key,
	name text not null,
	value int not null);
	""")
#create new ctrl table, with auto increment ndx
c.execute("""create table data
	(ndx integer primary key,
	name text not null,
	value real not null,
	time text not null,
	proc text not null);
	""")

# create rows in ctrl table
c.execute(""" insert into ctrl (name, value) values ('run', 1)""")
c.execute(""" insert into ctrl (name, value) values ('py3run', 0)""")
c.execute(""" insert into ctrl (name, value) values ('ipyrun', 1)""")

# create row in data table
c.execute(""" insert into data (name, value, time, proc)
	values ('shared', 1, ?, 'PY3')""", (getTimeStr(), )) # 'extra' comma required
conn.commit()

# verify data in ctrl table
data = c.execute('select * from ctrl')
print(data.fetchall())

data = c.execute('select * from data')
print(data.fetchall())

c.close()
runFlag = 1

# start outside process
cmd = "ipy ipyScript.py " + dbName + ' ' + str(limit) 
ipyProc = subprocess.Popen(cmd)

while runFlag:
	ms = getms()
	
	if (ms >500):
			time.sleep(0.07)

	if ms < 125:

		if checkPy3Run(dbName):
			conn = sqlite3.connect(dbName)
			c = conn.cursor()
			c.execute("SELECT value FROM data WHERE name ='shared'")
			curVal = c.fetchone()[0]
			if curVal >= limit:
				c.execute("UPDATE ctrl SET value = 0 WHERE name = 'run' ")
				conn.commit()
				continue
			
			# increment data and update time / proc info
			curVal += 1
			c.execute("""UPDATE data 
				SET value = ?, time = ?, proc = 'PY3 - Ping'
				WHERE name = 'shared' """, (curVal, getTimeStr(), ))
			conn.commit()

			# display updated data table
			data = c.execute('select * from data')
			print(data.fetchall())

			# hand off control
			c.execute("UPDATE ctrl set value = 0 WHERE name = 'py3run'")
			c.execute("UPDATE ctrl set value = 1 WHERE name = 'ipyrun'")
			conn.commit()
			c.close()
			conn.close()

	if (ms >250) and (ms < 375):
		runFlag = checkRun(dbName)

# close other script for sure
ipyProc.send_signal(signal.SIGTERM)
print('PY3 Finished!')

"""
Results:
Cross instance / code language communication using a database works.

However, It is slow and can use a lot of cpu contantly checking the ms time if
a communication schedule with 'smart' waits is not implemented

Using a specific timeing schedule, each instance can access 
and modify the database every 1 second without fail 

Any faster and database becomes locked due to concurrency issues
that throw errors and crash code.

Bottom line:
This could work, but it would be slow.

There may be better SQL database options - apparently, sqlite3 is not meant for 
fast actions and was used as a proof of concept since it is packaged
with both Python 3 and Ironpython 32bit.
"""