# SQLTest2
Script to test cross instance / code language commuincation via SQLite3 and AMQP using Python 3 and Ironpython.
Cloned from SQLTest.
## Results:
Cross instance / code language communication using AMQP and SQL database works.

This feels like a good solution as desired data can be logically put in/read from
an SQL database via agent methods. 

Still does a lot of writing to disk, but may be slightly easier than an AMQP only solution.

## Bottom line:
I think this is the way to go forward with the desired project communication.

However, some thought should be given the purely AMQP method before committing.
