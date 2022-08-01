'''
File with functions that are creating tables, updating, selecting etc. Note if the table has to be Tasks.
'''

import datetime
import sqlite3

file = 'data.db' # file should be chosen by user, note that you are using one conection
con = sqlite3.connect(file) # note that at this point you are working with one database
con.row_factory = sqlite3.Row # to get an acces to values in raw as in dictionary
cur = con.cursor() # one cursor for all the functions below



def create_table(name:str)-> None:
        '''
        Creates a table Tasks in database. Can set name = 'Tasks'. Retuns None;
        '''
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


def create_table_curent() -> None:
        '''
        Creates a table Curent in database. Retuns None;
        '''
        with con:
                cur.execute(""" CREATE TABLE Curent (
                        id INTEGER PRIMARY KEY,
                        id_tasks INTEGER,
                        name TEXT,
                        time_history TEXT,
                        u_time TEXT,
                        duration TEXT,
                        active TEXT
                )""")


def insert(table, name, id = None, duration = datetime.timedelta(0), u_time = datetime.timedelta(0), parent_id = None, checkpoints = '', notes = ''):
        '''Insert a recor to db (table Tasks),  retuns id of the inserted record. Name can be set to Tasks'''

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

def insert_to_curent(id_tasks, u_time = datetime.timedelta(0)) -> int:
        '''Insert a recor to db (table Curent),  retuns id of the inserted record. Data from table Tasks'''
        # should be already in Tasks
        # u_time not implemented correctly yet

        with con:
                cur.execute(f"SELECT * FROM Tasks  WHERE id = ?", (id_tasks,))
                task = cur.fetchone()

                name = task['name']
                duration = task['duration']

                cur.execute(f"""INSERT INTO Curent VALUES 
                        (NULL, ?, ?, '[]', ?, ?, 'False')""",
                        (id_tasks, name, repr(u_time), duration)
                )

                return cur.lastrowid
                


def delete(table: str, id : int) -> None:
        '''Delete record from table (arbitrary) by id.'''
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
        '''Retuns a row from a table by id (arbitrary table)'''
        with con:
                cur.execute(f"SELECT * FROM {table} WHERE id = ?", (id,))
                return cur.fetchone()


def add_subtask(table, id, subtask_id):
        '''Not used in project.'''
        # no checking for loops yet
        with con:
                cur.execute(f"SELECT * FROM {table} WHERE id = ?", (id,))
                
                lst = eval(cur.fetchone()['subtasks_id'])
                lst.append(subtask_id)

                cur.execute(f"UPDATE {table} SET subtasks_id = ? WHERE id = ?", (repr(lst),id))



def show_table(table: str) -> None:
        '''Showes arbitrary table with headers.'''
        with con:
                cur.execute(f'PRAGMA table_info({table})')
                desc = cur.fetchall()
                names = [fields[1] for fields in desc]
                print(names)

                for row in cur.execute(f"SELECT * FROM {table}"):
                        print(tuple(row))

def get_parents(table : str, id: int) -> list:
        '''
        Retuns the list of all parents id (all generations). Parents are ordered from the closest. Tested only for table Tasks
        '''

        task = get_row(table,id)

        if task['parent_id'] is None:
                return []
        else:
                id_parent = int(task['parent_id'])
                return [id_parent] + get_parents(table,id_parent)


def activate(table:str, id:int, parents = True) -> None:
        '''
        Change the active column to 'True' if it wasn't. Does the same for parents if parents = True in signature.
        Should be working on both tables (but use parents = False on Curent table).
        '''
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



def get_childs(table:str,id:int) -> list:
        '''Returns the list of ids of all childes (all generations) from Tasks table. Table can be set to Tasks.
        '''

        task = get_row(table,id)
        if task['subtasks_id'] == '[]':
                return []
        else:
                lst_id = eval(task['subtasks_id'])
                for id_s in lst_id:
                        lst_id += get_childs(table,id_s)

                return lst_id
        
def deactivate(table:str, id:int, family = True) -> list:
        '''
        Change the active column active to 'False' if it wasn't. Does the same for family if family = True in signature.
        Should be working on both tables (but use family = False on Curent table).
        ''' 
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

def time(table:str, id:int):
        '''
        Sums up and returns times spend on the task. Should work on both tables (need column 'time_history', 'u_time' and 'active') . Returning datetime.timedelta object.
        '''
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
                        t += dt
                
                return t + eval(task['u_time'])


def add_checkpoint(table, id, description):
        '''
        Not used in project.
        '''
        # You can make it more robust. You can get points (progress) for a checkpoint or set time (or data) to reach checkpoint
        with con:
                task = get_row(table,id)
                checkpoint_lst = eval(task['checkpoints'])+[[description,False]]
                cur.execute(f"UPDATE {table} SET checkpoints = ? WHERE id = {id}", (repr(checkpoint_lst),))


