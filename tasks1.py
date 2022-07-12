from asyncio.windows_events import NULL
import sqlite3

con = sqlite3.connect('data.db') # note that at this point you are working with one database

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
                cur.execute(f"""INSERT INTO {table} VALUES 
                        (NULL, ?, ?, ?, '[]', ?, '', 'False')""",
                        (name, duration, u_time, parent_id)
                )

def delete(table, id ):
# not sure how many parameters you need
# potential SQL injection
        with con:
                cur.execute(f"""DELETE FROM {table} WHERE id = ? """,
                        (id,)
                )

def delete_table(table):
        with con:
                cur.execute(f"DROP TABLE {table}")


def get_row(table,id):
        with con:
                cur.execute(f"SELECT * FROM {table} WHERE id = ?", (id,))
                return cur.fetchone()

def add_subtask(table, id, subtask_id):
        with con:
                cur.execute(f"SELECT subtasks_id FROM {table} WHERE id = ?", (id,))
                
                lst = eval(cur.fetchone()[0])
                lst.append(subtask_id)
                print(repr(lst))
                cur.execute(f"UPDATE {table} SET subtasks_id = ? WHERE id = ?", (repr(lst),id))



def show_table(table):
        with con:
                print('(id, name, duration, u_time, subtasks_id, parent_id, checkpoints, active)')
                for row in cur.execute(f"SELECT * FROM {table}"):
                        print(row)


add_subtask("Tasks",13, 15)

insert("Tasks","new task")

show_table("Tasks")


con.commit()

con.close()

# %%