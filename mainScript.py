"""Script to test cross instance / code language commuincation via SQLite3
Addtional testing with AMQP to remove sleeps"""

import sqlite3
import datetime
import subprocess
import signal

from AMQPAgent import AMQPAgent

def getTimeStr():
    """return time as string"""
    return datetime.datetime.now().strftime('%H:%M:%S.%f')

limit = 100 # number of times to update value

### Create database for testing
dbName = 'test.db'
conn = sqlite3.connect(dbName,  )
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
c.execute("""create table data
	(ndx integer primary key,
	name text not null,
	value real not null,
	time text not null,
	proc text not null);
	""")

# create row in data table
c.execute(""" insert into data (name, value, time, proc)
	values ('shared', 1, ?, 'PY3')""", (getTimeStr(), )) # 'extra' comma required
conn.commit()

# verify data in table
data = c.execute('select * from data')
print(data.fetchall())
c.close()

### AMQP settings
host = '127.0.0.1'
py3 = AMQPAgent('PY3', host, [0,'init','time'])

# start outside process
cmd = "ipy ipyScript.py " + dbName + ' ' + str(limit) 
ipyProc = subprocess.Popen(cmd)

runFlag = 1
while runFlag:
    # create and send message to IPY
    py3.msg[0] += 1
    py3.msg[1] = 'DataBase ready - (from PY3)'
    py3.msg[2] = getTimeStr()
    py3.send('toIPY',py3.msg) # sends database ready to IPY

    # waits for message that database is ready from IPY
    py3.receive('toPY3',py3.callback)

    if py3.msg[1] == 'finished':
        runFlag = 0;
        continue

    # connect to db
    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute("SELECT value FROM data WHERE name ='shared'")
    curVal = c.fetchone()[0]

    #check for stopping conditions
    if curVal >= limit:
        runFlag = 0
        continue

    # increment data and update time / proc info
    curVal += 1
    c.execute("""UPDATE data 
        SET value = ?, time = ?, proc = 'PY3 - Ping'
        WHERE name = 'shared' """, (curVal, getTimeStr(), ))
    conn.commit()

    # display updated data table
    data = c.execute('select * from data')
    print('***')
    print(getTimeStr() + " PY3 updated DB to: " + str(data.fetchall()))

    # close db Connction
    c.close()
    conn.close()

print('PY3 Finished!')
# close other script for sure
ipyProc.send_signal(signal.SIGTERM)
print('IPY Terminated')

"""
Results:
Cross instance / code language communication using AMQP and SQL database works.

This feels like a good solution as desired data can be logically put in/read from
an SQL database via agent methods. 

Still does a lot of writing to disk but may be slightly easier than an AMQP only solution.

Bottom line:
I think this is the way to go forward with the desired project communication.
"""