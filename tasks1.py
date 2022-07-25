import datetime
import sqlite3

con = sqlite3.connect('data.db') # note that at this point you are working with one database

con.row_factory = sqlite3.Row # to get an acces to values in raw as in dictionary

cur = con.cursor()

def create_table(name):
        # potential SQL injection
        # can add atomic task to time_history intervals
        # can add notes
        with con:
                cur.execute(""" CREATE TABLE {} (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        active TEXT,
                        duration TEXT,
                        u_time TEXT,
                        subtasks_id  TEXT,
                        parent_id INTEGER,
                        time_history TEXT,
                        checkpoints TEXT,
                        notes TEXT
                )      
                """.format(name))


def create_table_curent():
        with con:
                cur.execute(""" CREATE TABLE Curent (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        time_history TEXT,
                        u_time TEXT,
                        duration TEXT,
                        active TEXT
                )""")


def insert(table, name, id = None, duration = datetime.timedelta(0), u_time = datetime.timedelta(0), parent_id = None, checkpoints = '', notes = ''):
        '''insert a recor to db,  retuns id of the inserted record'''

# connection is set globally
# not sure how many parameters you need
# potential SQL injection
        with con:
                cur.execute(f"""INSERT INTO {table} VALUES 
                        (NULL, ?, 'False' , ?, ?, '[]', ?,'[]', ?, ?)""",
                        (name, repr(duration), repr(u_time), parent_id, checkpoints, notes)
                )
                con.commit()

                if parent_id is not None:
                        add_subtask(table, parent_id, cur.lastrowid)

                return cur.lastrowid

def insert_to_curent(id, u_time = datetime.timedelta(0)):
        # should be already in Tasks
        # u_time not implemented correctly yet

        with con:
                cur.execute(f"SELECT * FROM Tasks  WHERE id = ?", (id,))
                task = cur.fetchone()

                name = task['name']
                duration = task['duration']

                cur.execute(f"""INSERT INTO Curent VALUES 
                        (?,?,'[]', ?, ?, 'False')""",
                        (id, name, repr(u_time), duration)
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
        # print('Table = ', repr(table), ',id = ', repr(id))
        with con:
                cur.execute(f"SELECT * FROM {table} WHERE id = ?", (id,))
                return cur.fetchone()

def add_subtask(table, id, subtask_id):
        # no checking for loops yet
        with con:
                cur.execute(f"SELECT * FROM {table} WHERE id = ?", (id,))
                
                lst = eval(cur.fetchone()['subtasks_id'])
                lst.append(subtask_id)

                cur.execute(f"UPDATE {table} SET subtasks_id = ? WHERE id = ?", (repr(lst),id))



def show_table(table):
        with con:
                cur.execute(f'PRAGMA table_info({table})')
                desc = cur.fetchall()
                names = [fields[1] for fields in desc]
                print(names)

                for row in cur.execute(f"SELECT * FROM {table}"):
                        print(tuple(row))

def get_parents(table,id):
        # Returns list of all parents id (all generations)
        # Order from the closest

        task = get_row(table,id)
        if task['parent_id'] is None:
                return []
        else:
                id_parent = int(task['parent_id'])
                return [id_parent] + get_parents(table,id_parent)


def activate(table, id, parents = True):
        with con:
                task = get_row(table,id)
                # print('parents =', get_parents(table,id))
                if task['active'] == "True":
                        return

                now = datetime.datetime.today()
                new = eval(task['time_history'])+[[now]]
                cur.execute(f"UPDATE {table} SET time_history = '{repr(new)}', active = 'True' WHERE id = {id}")

                # update state of parents
                if parents:
                        for id_p in get_parents(table,id):
                                parent = get_row(table,id_p)
                                if parent['active'] == "True":
                                        return # older parents should be active
                                new = eval(parent['time_history'])+[[now]]
                                cur.execute(f"UPDATE {table} SET time_history = '{repr(new)}', active = 'True' WHERE id = {id_p}")



def get_childs(table,id):
        # Returns the list of ids of all childes (all generations)

        task = get_row(table,id)
        if task['subtasks_id'] == '[]':
                return []
        else:
                lst_id = eval(task['subtasks_id'])
                for id_s in lst_id:
                        lst_id += get_childs(table,id_s)

                return lst_id
        
def deactivate(table, id, family = True):
        with con:
                task = get_row(table,id)
                if task['active'] == "False":
                        return 

                now = datetime.datetime.today()
                lst = eval(task['time_history'])
                lst[-1].append(now)

                cur.execute(f"UPDATE {table} SET time_history = '{repr(lst)}', active = 'False' WHERE id = {id}")

                if not family:
                        return

                # update state of parents, can be optimize (order?)
                for id_p in get_parents(table,id):
                        parent = get_row(table,id_p)
                        flag = False
                        for id_s in eval(parent['subtasks_id']):
                                subtask = get_row(table,id_s)
                                if subtask['active'] == 'True':
                                        flag = True
                                        break

                        if not flag:
                                lst = eval(parent['time_history'])
                                lst[-1].append(now)
                                cur.execute(f"UPDATE {table} SET time_history = '{repr(lst)}', active = 'False' WHERE id = {id_p}")   

                # update state of childs
                for id_c in get_childs(table,id):
                        subtask = get_row(table,id_c)
                        if subtask['active'] == 'False':
                                continue
                        lst = eval(subtask['time_history'])
                        lst[-1].append(now)
                        cur.execute(f"UPDATE {table} SET time_history = '{repr(lst)}', active = 'False' WHERE id = {id_c}")                         

def time(table, id):
        with con:
                task = get_row(table,id)
                time_lst = eval(task['time_history'])

                if time_lst == []:
                        return eval(task['u_time'])

                if task['active'] == 'True':
                        time_lst[-1].append(datetime.datetime.today())

                t = datetime.timedelta(0)
                for start,end in time_lst:
                        dt = end - start
                        t +=dt
                
                return t + eval(task['u_time'])


def add_checkpoint(table, id, description):
        # You can make it more robust. You can get points (progress) for a checkpoint or set time (or data) to reach checkpoint
        with con:
                task = get_row(table,id)
                checkpoint_lst = eval(task['checkpoints'])+[[description,False]]
                cur.execute(f"UPDATE {table} SET checkpoints = ? WHERE id = {id}", (repr(checkpoint_lst),))




# Uncomment to test

delete_table("Tasks")
create_table("Tasks")
delete_table("Curent")
create_table_curent()


insert("Tasks","new task1")
insert("Tasks","new task2", parent_id =1)
insert("Tasks","new task3", parent_id =1)
insert("Tasks","new task4", parent_id =2)
insert("Tasks","new task5")
insert("Tasks","new task6", parent_id =5)
insert("Tasks","new task7", parent_id =5)
insert("Tasks","new task8", parent_id =7)

# insert_to_curent(1)
# insert_to_curent(7)
# insert_to_curent(2)
# insert_to_curent(3)

table = "Tasks"

# activate('Curent',1, parents = False)
# deactivate('Curent',1,family = False)


# activate(table, 5)
# deactivate(table,5)
# add_checkpoint(table, 1, 
# 'buy a milk')

# show_table("Tasks")
# show_table('Curent')

# print('time 1 = ',time('Curent', 1))
# print(time(table, 5))
# con.commit()

# con.close()

# %%