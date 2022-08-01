import PySimpleGUI as sg
import db_func
import datetime

con = db_func.con
cur = db_func.cur


def create_sq_table() -> tuple:
    '''
    Returns tuple Tab,lst where Tab is pysimplegui.Table() elements with data from Tasks table. lst is list with data from Tasks table.
    '''
    cur.execute(f"SELECT * FROM {'Tasks'}")
    data = cur.fetchall()

    headings = ['id','name', 'parent', 'subtasks', 'time']

    lst = []

    for raw in data:
        id = raw['id']
        name = raw['name']
        #print(name)
        if raw['parent_id'] is None:
            parent = 'None'
        else:
            parent = db_func.get_row('Tasks', int(raw['parent_id']))['name']

        subtasks = []
        for id_s in eval(raw['subtasks_id']):
            # print(id_s)
            subtasks.append(db_func.get_row('Tasks', id_s)['name'])

        subtasks = ', '.join(subtasks)

        time = db_func.time('Tasks', raw['id']) 
        time_str = str(time).split(".")[0] # it get rids of miliseconds

        lst.append([id,name, parent, subtasks, time_str])

    Tab = sg.Table(values = lst, headings = headings, enable_click_events = True, key = 'Tab')
    
    return Tab, lst





def task_layout(task_id = None):
    ''' Returns a layout for a single task. Tasks are from table Tasks (not true?). taks_id is from Curent.
    '''

    Tasks_options = [
        sg.Button('|>', key = "START-" + str(task_id)),
        sg.Button('||', key = "PAUSE-" + str(task_id)),
        sg.Button('Edit', key = "EDIT-" + str(task_id))
        ]

    # You need to take this data from database
    if task_id is None: # for testing
        total_time = datetime.timedelta(0)
        task_duration = datetime.timedelta(0)
        name = 'Test'
    else:
        task = db_func.get_row('Curent',task_id)
        t = db_func.time('Curent', task_id)
        task_duration = eval(task['duration'])
        name = task['name']



    Tasks_progress = [sg.ProgressBar(task_duration.total_seconds() , size = (10,20), expand_x = True, key = "PROGRESS-" + str(task_id))]

    Task_time = [sg.Text(str(t).split('.')[0], key = "TIME-" + str(task_id))]
    
    raw =  [sg.Checkbox('', key = 'CHECKBOX-' + str(task_id), enable_events= True)] + [sg.Text(name , key = 'TASK NAME-' + str(task_id), size = (16,1))] + Tasks_options + Tasks_progress + Task_time

    return raw

def tasks_layout(id_lst):
    '''Returns a layout for all tasks form the list of id (from Curent)'''
    
    layout = [[]]
    
    for i,task in enumerate(id_lst):
        layout.append(task_layout(task))

    return layout


def add_task_button(window)-> None:
    '''
    Function that runs when you press add task button.
    '''

    id_in_tasks = add_task()
    # check if the user exited
    if not id_in_tasks:
        return

    # check if somebody from family is in curent
    lst_of_parent = db_func.get_parents('Tasks', id_in_tasks)


    sql = 'SELECT * FROM Curent WHERE id_tasks IN ({0})'.format(', '.join('?' for _ in lst_of_parent))
    db_func.cur.execute(sql, tuple(lst_of_parent))

    colision = db_func.cur.fetchall()

    if colision:
        family_members = [row['name'] for row in colision]
        sg.Popup(f'There is a task ({ ",".join(family_members) }) from parents in curent. Task was add to database.')

    # Tasks table refresh
    _, lst = create_sq_table()
    window['Tab'].update(values = lst)

    # Curent table refresh
    id_in_curent = db_func.insert_to_curent(id_in_tasks)

    # Adding a row to layout in curent tab
    row = [task_layout(id_in_curent)]
    window.extend_layout(window["Today tasks"], row)

    window['TIME-' + str(id_in_curent)].bind('<Enter>', '+')
    window['TIME-' + str(id_in_curent)].bind('<Leave>', '-')

    return 

def add_task():
    '''
    Add task to table Tasks. Returns id (or None if exit). Don't create a layout.
    '''
    h = 60
    v = 1
    r = 2
    s = 10

    # some starting values:
    
    parent_id = None
    checkpoints_str = ''
    cur = con.cursor()

    Data = [
            [
            sg.Text('Task ', size = (h//3-r,v)), 
            sg.Input(key = 'name',size = (h,v))
            ],
               
           [
            sg.Text('Duration of a session',size = (h//3-r,v)),
            sg.Input('hours',key = '-DURATIONh-',size = (h//3-r,v)),
            sg.Input('minutes',key = '-DURATIONm-',size = (h//3-r,v)),
            sg.Input('seconds',key = '-DURATIONs-',size = (h//3-r,v))
           ], 
        
            [
            sg.Text('Untruck Time',size = (h//3-r,v)),
            sg.Input('hours',key = '-TIMEh-',size = (h//3-r,v)),
            sg.Input('minutes',key = '-TIMEm-',size = (h//3-r,v)),
            sg.Input('seconds',key = '-TIMEs-',size = (h//3-r,v))  
            ],

            [sg.Text('Parent',size = (h//3-r,v)), sg.Text('None', key = "Parent",size = (h//3-r,v)), sg.Stretch(), sg.Button('Select parent', key = 'Select parent')],
            # pop up with db table

            [sg.Text('Checkpoints',size = (h//3-r,v)),sg.Multiline(checkpoints_str, key = 'Checkpoints',size = (h-2,4)),],
        
           [sg.Text('Notes', size = (h//3-r,v)), sg.Multiline(key = '-NOTES-',size = (h-2,4))]     
    ]
    
    layout = [[Data,sg.Button("Add", key = "-ADD-")]]
    
    window_add_tasks = sg.Window("Add task",layout)

    add = False
    
    while True:
        event, values = window_add_tasks.read()

        if event == sg.WIN_CLOSED:
            break

        if event == 'Select parent':
            temp = id_name_from_db()
            if temp != None:
                parent_id, parent_name = temp
                window_add_tasks['Parent'].update(f'Id: {parent_id} Name: {parent_name}')
            
        if event == "-ADD-":
            
            h = int(values['-DURATIONh-']) if is_number(values['-DURATIONh-']) else 0
            m = int(values['-DURATIONm-']) if is_number(values['-DURATIONm-']) else 0
            s = int(values['-DURATIONs-']) if is_number(values['-DURATIONs-']) else 0
            duration = datetime.timedelta(hours = h, minutes = m, seconds = s)

            h = int(values['-TIMEh-']) if is_number(values['-TIMEh-']) else 0
            m = int(values['-TIMEm-']) if is_number(values['-TIMEm-']) else 0
            s = int(values['-TIMEs-']) if is_number(values['-TIMEs-']) else 0
            
            u_time = datetime.timedelta(hours = h, minutes = m, seconds = s)

            task_id = db_func.insert('Tasks', values['name'], duration = duration, u_time = u_time, parent_id = parent_id, checkpoints = values['Checkpoints'], notes = values['-NOTES-'])

            con.commit()
            add = True

            break 

    window_add_tasks.close()
    

    if add:
        return task_id

    return 



def edit_task(id, id_curent = None):
    ''' 
    The function that is starting when pressing Edit button. It changes the data of Tasks table and update database. If id_curent is not None it changes data in Curent table.
    '''
    # In future you want to distinquish edit global and edit local (just in current?)
    h = 60
    v = 1
    r = 2
    s = 10

    task = db_func.get_row('Tasks',id)
    
    if task['parent_id'] is not None:
        parent_id = int(task['parent_id'])
        parent_name = db_func.get_row('Tasks',parent_id)['name']
        parent_string = f'Id: {parent_id} Name: {parent_name}'
    else:
        parent_id = None
        parent_name = str(None)
        parent_string = str(None)
    checkpoints_str = task['checkpoints']

    td = eval(task['duration'])

    d_hours = int(td.total_seconds()// 3600)
    _, remainder = divmod(td.seconds, 3600)
    d_minutes, d_seconds = divmod(remainder, 60)


    cur = con.cursor()

    Data = [
            [
            sg.Text('Task ', size = (h//3-r,v)), 
            sg.Input(task['name'],key = 'name',size = (h,v))
            ],
               
           [
            sg.Text('Duration of a session',size = (h//3-r,v)),
            sg.Input(str(d_hours),key = '-DURATIONh-',size = (h//3-r,v)),
            sg.Input(str(d_minutes),key = '-DURATIONm-',size = (h//3-r,v)),
            sg.Input(str(d_seconds),key = '-DURATIONs-',size = (h//3-r,v))
           ], 
        
            [
            sg.Text('Untruck Time',size = (h//3-r,v)),
            sg.Input('hours',key = '-TIMEh-',size = (h//3-r,v)),
            sg.Input('minutes',key = '-TIMEm-',size = (h//3-r,v)),
            sg.Input('seconds',key = '-TIMEs-',size = (h//3-r,v))  
            ],

            [sg.Text('Parent',size = (h//3-r,v)), sg.Text(parent_string, key = "Parent",size = (h//3-r,v)), sg.Stretch()],
            # pop up with db table

            [sg.Text('Checkpoints',size = (h//3-r,v)),sg.Multiline(checkpoints_str, key = 'Checkpoints',size = (h-2,4)),],

            # you removed  sg.Stretch(), sg.Button('Edit checkpoints', key = 'Edit checkpoints' )
        
           [sg.Text('Notes', size = (h//3-r,v)), sg.Multiline(task['NOTES'], key = '-NOTES-',size = (h-2,4))] 
        
    ]
    
    layout = [[Data,sg.Button("Save", key = "-SAVE-")]]
    
    window_add_tasks = sg.Window("Edit task",layout)
    
    while True:
        event, values = window_add_tasks.read()

        if event == sg.WIN_CLOSED:
            break

        if event == 'Select parent':
            temp = id_name_from_db()
            if temp != None:
                parent_id, parent_name = temp
                window_add_tasks['Parent'].update(f'Id: {parent_id} Name: {parent_name}')
     
        if event == "-SAVE-":
            
            h = int(values['-DURATIONh-']) if is_number(values['-DURATIONh-']) else 0
            m = int(values['-DURATIONm-']) if is_number(values['-DURATIONm-']) else 0
            s = int(values['-DURATIONs-']) if is_number(values['-DURATIONs-']) else 0
            duration = datetime.timedelta(hours = h, minutes = m, seconds = s)

            h = int(values['-TIMEh-']) if is_number(values['-TIMEh-']) else 0
            m = int(values['-TIMEm-']) if is_number(values['-TIMEm-']) else 0
            s = int(values['-TIMEs-']) if is_number(values['-TIMEs-']) else 0
            
            u_time = datetime.timedelta(hours = h, minutes = m, seconds = s)

            sql = f'''UPDATE Tasks
                    SET name = ?,
                        duration = ?,
                        u_time = ?,
                        parent_id = ?,
                        checkpoints = ?,
                        notes = ?
                    WHERE id = ? '''
            
            

            cur.execute(sql,(values['name'], repr(duration), repr(u_time),  parent_id, values['Checkpoints'], values['-NOTES-'],id))

            con.commit()

            if id_curent:
                sql2 = f'''UPDATE Curent
                        SET name = ?,
                            duration = ?,
                            u_time = ?
                        WHERE id = ? '''


                cur.execute(sql2,(values['name'], repr(duration), repr(u_time), id_curent))

            con.commit()


            break 

    window_add_tasks.close()

    return 
    


def id_name_from_db():
    '''Returns tuple id,name from coursor cur that you selected from database table.'''


    t, lst = create_sq_table()

    window = sg.Window('Database', layout =[[t],[sg.Button("Choose", key = "Choose")]], default_element_size=(12,1))

    cancel = False

    while True:    

        event, values = window.read()    

        if values['Tab'] and event == "Choose":
            id = lst[values['Tab'][0]][0]
            name = lst[values['Tab'][0]][1]
            break


        if event == sg.WIN_CLOSED:   
            cancel = True          
            break  

    window.close()
    if not cancel:
        return id,name

def edit_checkpoints(checkpoints):
    '''I dont think that is usefull. You decided to write checkpoints in multline elements.'''

    column = [[sg.Button('Up    ')],[sg.Button('Down')]]
    layout = [[sg.Listbox(checkpoints,s = (30,10), key = 'checkpoints'), sg.Column(column)], 
    [sg.Button('Add'),sg.Button('Remove'), sg.B("Save",key = 'Save')]]

    window_checkpoints = sg.Window("Checkpoints",layout )

    while True:
        event, values = window_checkpoints.read()

        if event == sg.WIN_CLOSED:
            break

        if event == 'Add':
            e,v = read_value('Add checkpoint', value = '')
            if e == 'Save':
                checkpoints.append(v['Input'])
                window_checkpoints['checkpoints'].update(checkpoints)

        if event == 'Remove':
            checkpoints.remove(values['checkpoints'][0])
            window_checkpoints['checkpoints'].update(checkpoints)

        if event == "Up":
            pass
        if event == "Down":
            pass
        if event == 'Save':
            break
    window_checkpoints.close()

    return checkpoints

def read_value(title, value = ''):
    '''Small popup to write a value'''
    layout = [[sg.Input(value, key = 'Input')], [sg.Submit('Save'), sg.Cancel('Cancel')]]
     
    window = sg.Window(title, layout)    

    event, values = window.read()    
    window.close()

    return event, values

def is_number(s) -> bool:
    '''
    Returns True if it can convert s to float.
    '''
    try:
        float(s)
        return True
    except ValueError:
        return False
    except TypeError:
        return False

def description(selected_id: int, window) -> None:
    '''
    Updates the multiline element in database tab (description). After update it showes info of selected element (selected_id).
    selected_id : int
    window : pysimplegui Window()
    '''
    selection = db_func.get_row('Tasks', selected_id)

    if selection is None:
        return

    if selection['parent_id'] is None:
        parent = 'None'
    else:
        parent = db_func.get_row('Tasks', int(selection['parent_id']))['name']

    subtasks = []
    for id_s in eval(selection['subtasks_id']):
            subtasks.append(db_func.get_row('Tasks', id_s)['name'])

    subtasks = ', '.join(subtasks)

    string = f'''Name:\n{selection['name']}\n\nParent:\n{parent}\n\nSubtasks:\n{subtasks}\n\nCheckpoints:\n{selection['checkpoints']}\n\nNotes:\n{selection['notes']}       
            
    '''
    window['description'].update(string)

def add_to_curent(selected_id: int, window) -> None:
    '''
    Insert task (selected_id) to Curent table. Update curent tab. Shows wornings if there is a family member in Curent already.
    selected_id : int
    window : pysimplequi.Window()
    '''

    # check if somebody from family is in curent
    lst_of_parent = db_func.get_parents('Tasks',selected_id)
    lst_of_childs = db_func.get_childs('Tasks',selected_id)
    family = lst_of_parent + lst_of_childs + [selected_id]

    sql = 'SELECT * FROM Curent WHERE id_tasks IN ({0})'.format(', '.join('?' for _ in family))
    db_func.cur.execute(sql, tuple(family))

    colision = db_func.cur.fetchall()

    if colision:
        family_members = [row['name'] for row in colision]
        sg.Popup(f'There is a task ({ ",".join(family_members) }) from family in curent.')

    # insert data to Curent table
    id_in_cur = db_func.insert_to_curent(selected_id)

    # create a layout
    row = [task_layout(id_in_cur)]

    # extend the window['Today tasks']
    window.extend_layout(window["Today tasks"], row)

    window['TIME-' + str(id_in_cur)].bind('<Enter>', '+')
    window['TIME-' + str(id_in_cur)].bind('<Leave>', '-')


def remove_from_db(selected_id: int):
    '''
    Remove task (selected_id) from Tasks table. Take care of parent data. Not refreshing database tab.
    selected_id : int (id in Tasks table)
    '''

    # check if task has a subtasks 
    row = db_func.get_row('Tasks',selected_id)
    
    if row == None:
        return

    # check if it is in current
    sql = """SELECT * FROM CURENT WHERE id_tasks = ?"""
    cur.execute(sql,(selected_id,))
    if cur.fetchall():
        sg.Popup(f'The task is in curent table! Clear the curen table before removing the task.') 
        return

    if eval(row['subtasks_id']) != []:
        sg.Popup(f'There are some subtasks! Remove subtasks before removing the task.') # lazy
        return



    # check if task has a parent and remove it from parent 
    if row['parent_id'] != None:
        parent_id = row['parent_id']
        parent = db_func.get_row('Tasks',parent_id)
        # print('list = ', eval(parent['subtasks_id']), ' id = ', selected_id)
        sub_lst = eval(parent['subtasks_id'])
        sub_lst.remove(selected_id)
        # print(update_lst)
        db_func.cur.execute(f"UPDATE {'Tasks'} SET subtasks_id = ? WHERE id = {parent_id}", (repr(sub_lst),))

    # remove task from db
    db_func.delete('Tasks', selected_id)


def update(window, start = False):
    ''''
    Function that update progres bars of tasks in curent (and total time). Used at main loop (start = False) and at the start of the program  (start = True). Function returns str with info to print when hovering over total time.
    '''
    total_planned, total_remaining, total_working = datetime.timedelta(0), datetime.timedelta(0), datetime.timedelta(0)
    db_func.cur.execute("Select * FROM Curent")
    for task in db_func.cur.fetchall():
        # from id in current to id in tasks
        id_curent = int(task['id'])
        # id_task = int(task['id_tasks'])

        t = db_func.time('Curent', id_curent)
        d = eval(task['duration']).total_seconds()
        window['TIME-' + str(id_curent)].update(str(t).split('.')[0])
        window['PROGRESS-' + str(id_curent)].update(current_count = t.total_seconds(), max=d)
        if start:
            window['TIME-' + str(id_curent)].bind('<Enter>', '+')
            window['TIME-' + str(id_curent)].bind('<Leave>', '-')

        del_rem = eval(task['duration']) - t if eval(task['duration']) - t >  datetime.timedelta(0) else datetime.timedelta(0)

        total_planned += eval(task['duration'])
        total_remaining += del_rem
        total_working += t


    info_total = f'Total time planned {str(total_planned).split(".")[0]}'
    window['PROGRESS-Total'].update(total_working.total_seconds(), max = total_working.total_seconds() + total_remaining.total_seconds())

    if start:
        window['TIME-' + 'TOTAL'].bind('<Enter>', '+')
        window['TIME-' + 'TOTAL'].bind('<Leave>', '-')
    
    window["-INFO TOTAL-"].update(info_total)
    window["TIME-TOTAL"].update(str(total_working).split(".")[0])

    if total_remaining != datetime.timedelta(0):
        mes = f"Remaining {str(total_remaining).split('.')[0]}"
    else:
        mes = f"Finished ({str(total_planned).split('.')[0]})"


    return mes
    