import sqlite3
import sys
import os
import datetime
import subprocess
import signal
import time

print(sys.version)

def checkIpyrun(dbName):
	"""Check status of db ctrl value"""
	conn = sqlite3.connect(dbName)
	c = conn.cursor()
	c.execute("select value from ctrl where name = 'ipyrun'")
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

def main(dbName,limit):
	"""Main function"""
	#print(sys.version)
	conn = sqlite3.connect(dbName)
	runFlag = 1

	while runFlag:

		ms = getms()
		if (ms <500):
			time.sleep(0.07)

		if (ms >500) and (ms < 625):
			if checkIpyrun(dbName):
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
					SET value = ?, time = ?, proc = 'IPY - Pong'
					WHERE name = 'shared' """, (curVal, getTimeStr(), ))
				conn.commit()

				# display updated data table
				data = c.execute('select * from data')
				print(data.fetchall())

				# hand off control
				c.execute("UPDATE ctrl set value = 0 WHERE name = 'ipyrun'")
				c.execute("UPDATE ctrl set value = 1 WHERE name = 'py3run'")
				conn.commit()
				c.close()
				conn.close()

		if (ms >750) and (ms < 875):
			runFlag = checkRun(dbName)

	print("IPY Finished!")

if __name__ == "__main__":
    dbName = sys.argv[1]
    limit = float(sys.argv[2])
    main(dbName, limit)