import sqlite3

con = sqlite3.connect('data.db')

cur = con.cursor()

# cur.execute('DROP TABLE people')
# cur.execute('''CREATE TABLE people 
#             (
#                 id INTEGER PRIMARY KEY,
#                 NAME text
#             )
#                ''')

# Insert a row of data
cur.execute("INSERT INTO people VALUES (Null, 'miki')")


for row in cur.execute("SELECT * FROM people"):
        print(row)

# Save (commit) the changes
con.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
con.close()