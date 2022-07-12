from asyncio.windows_events import NULL
import sqlite3

con = sqlite3.connect('data.db')

cur = con.cursor()

def create_table(name):
        # potential SQL injection
        with con:
                cur.execute(""" CREATE TABLE {} (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        duration TEXT,
                        u_time TEXT,
                        subtasks_id  TEXT,
                        parent_id INTEGER,
                        checpoints TEXT,
                        active TEXT
                )      
                """.format(name))


def insert(table, name, id = None, duration = 0, u_time = 0, parent_id = None):
# not sure how many parameters you need
# potential SQL injection
        with con:
                cur.execute("""INSERT INTO {} VALUES 
                        (NULL, ?, ?, ?, '', ?, '', 'False')""".format(table),
                        (name, duration, u_time, parent_id)
                )

def delete(table, id ):
# not sure how many parameters you need
# potential SQL injection
        with con:
                cur.execute("""DELETE FROM {} WHERE id = ? """.format(table),
                        (id,)
                )

def set_coursor(table,id):
        with con:
                cur.execute(f"SELECT * FROM {table} WHERE id = ?", (id,))

def add_subtask(table, id, subtask_id):
        with con:
                old_ids = cur.execute(f"SELECT subtasks_id FROM {table} WHERE id = ?", (id,))[0]
                new_ids = old_ids + str(subtask_id)
                print(new_ids)
                #cur.execute(f"UPDATE {table} SET sub")

# cur.execute('DROP TABLE Tasks')
# create_table('Tasks')
#insert('Tasks', 'Other')
#delete('Tasks',3)

add_subtask("Tasks", 77,2)

# set_coursor("Tasks",2)
# for row in cur:
#         print(row)

# for row in cur.execute("SELECT * FROM Tasks"):
#         print(row)

# Save (commit) the changes
# con.commit()

con.close()