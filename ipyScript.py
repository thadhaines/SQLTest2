import sys
import sqlite3
import datetime
import subprocess
import signal

from AMQPAgent import AMQPAgent

def getTimeStr():
    """return time as string"""
    return datetime.datetime.now().strftime('%H:%M:%S.%f')

def main(dbName,limit):
    """Main function
    Assumes database is created"""

    ### AMQP settings
    host = '127.0.0.1'
    ipy = AMQPAgent('IPY', host, [0,'init','time'])

    runFlag = 1
    while runFlag:
        # wait for database ok signal
        ipy.receive('toIPY',ipy.callback) 
        # database should be ready after receive returns
        conn = sqlite3.connect(dbName)
        c = conn.cursor()
        c.execute("SELECT value FROM data WHERE name ='shared'")
        curVal = c.fetchone()[0]

        if curVal >= limit:
            runFlag = 0
            ipy.msg[1] = 'finished'
            ipy.send('toPY3',ipy.msg)
            c.close()
            conn.close()
            continue

        # increment data and update time / proc info
        curVal += 1
        c.execute("""UPDATE data 
            SET value = ?, time = ?, proc = 'IPY - Pong'
            WHERE name = 'shared' """, (curVal, getTimeStr(), ))
        conn.commit()

        # display updated data table
        data = c.execute('select * from data')
        print('***')
        print(getTimeStr() + " IPY updated DB to: " + str(data.fetchall()))

        # close db Connction
        c.close()
        conn.close()

        # create and send message to PY3
        ipy.msg[0] += 1
        ipy.msg[1] = 'DataBase ready - (from IPY)'
        ipy.msg[2] = getTimeStr()
        ipy.send('toPY3',ipy.msg) # sends database ready to PY3

    print("IPY Finished!")

if __name__ == "__main__":
    dbName = sys.argv[1]
    limit = float(sys.argv[2])
    main(dbName, limit)