# SQLTest
Script to test cross instance / code language commuincation via SQLite3.
More specifically Python 3 and Ironpython.

## Results:
Cross instance / code language communication using a database works.
However, It is slow and can use a lot of cpu contantly checking the 'ms' time if
a communication schedule with 'smart' waits is not implemented.

Using a specific timeing schedule, each instance can access 
and modify the database every 1 second without fail.

Any faster and database becomes locked due to concurrency issues
that in turn throw errors and lock/crash the code.

## Bottom line:
This could work, but it would be slow.
There may be better SQL database options - apparently, sqlite3 is not meant for 'fast action'.
However it was an easy option to create a proof of concept since it is packaged
with both Python 3 and Ironpython 32bit.
