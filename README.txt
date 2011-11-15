Installation &c.

1) Run ./phenny - this creates a default config file
2) Edit ~/.phenny/default.py
3) Run ./phenny - this now runs phenny with your settings

Enjoy!

-- 
Sean B. Palmer, http://inamidst.com/sbp/


Notes: 
echo '.dump' | sqlite3 tgg.db | cat > dump.tgg.db
to dump the database to the file

Converting An Entire Database To An ASCII Text File

Use the ".dump" command to convert the entire contents of a database into a single ASCII text file. This file can be converted back into a database by piping it back into sqlite3.

A good way to make an archival copy of a database is this:

    $ echo '.dump' | sqlite3 ex1 | gzip -c >ex1.dump.gz

This generates a file named ex1.dump.gz that contains everything you need to reconstruct the database at a later time, or on another machine. To reconstruct the database, just type:

    $ zcat ex1.dump.gz | sqlite3 ex2

The text format is pure SQL so you can also use the .dump command to export an SQLite database into other popular SQL database engines. Like this:

    $ createdb ex2
    $ sqlite3 ex1 .dump | psql ex2