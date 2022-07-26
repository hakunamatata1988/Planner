import interface2
import tasks1
import PySimpleGUI as sg
import datetime
import sqlite3



def task_layout(task_id = None):
    ''' Returns a layout for a single task. Tasks are from table Tasks. 
    taks_id is from Curent.
    '''

    # No checkpoints for now

    Tasks_options = [
        sg.Button('|>', key = "START-" + str(task_id)),
        sg.Button('||', key = "PAUSE-" + str(task_id)),
        sg.Button('#', key = "STOP-" + str(task_id)),
        sg.Button('Notes', key = "NOTES-" + str(task_id)),
        sg.Button('Edit', key = "EDIT-" + str(task_id)),
        sg.Button('Remove', key = "REMOVE-" + str(task_id))
        ]

    # You need to take this data from database
    if task_id is None:
        total_time = datetime.timedelta(0)
        task_duration = datetime.timedelta(0)
        name = 'Test'
    else:
        task = tasks1.get_row('Curent',task_id)
        total_time = datetime.timedelta(0)
        task_duration = eval(task['duration'])
        name = task['name']


    Tasks_progress = [sg.ProgressBar(task_duration.total_seconds() , size = (10,20), expand_x = True, key = "PROGRESS-" + str(task_id))]

    Task_time = [sg.Text(str(total_time).split(".")[0], key = "TIME-" + str(task_id))]
    
    raw =  [sg.Checkbox('', key = 'CHECKBOX-' + str(task_id), enable_events= True)] + [sg.Text(name , key = 'TASK NAME-' + str(task_id), size = (12,1))] + Tasks_options + Tasks_progress + Task_time

    return raw

def tasks_layout(id_lst):
    '''Returns a layout for all tasks form list od id'''
    
    layout = [[]]
    
    for i,task in enumerate(id_lst):
        layout.append(task_layout(task))

    return layout


def add_task_button(con,window):
    id_in_tasks = add_task(con,'Tasks')
    # check if the user exited
    if not id_in_tasks:
        return

    # check if somebody from family is in curent
    lst_of_parent = tasks1.get_parents('Tasks',id_in_tasks)


    sql = 'SELECT * FROM Curent WHERE id_tasks IN ({0})'.format(', '.join('?' for _ in lst_of_parent))
    tasks1.cur.execute(sql, tuple(lst_of_parent))

    colision = tasks1.cur.fetchall()

    if colision:
        family_members = [row['name'] for row in colision]
        sg.Popup(f'There is a task ({ ",".join(family_members) }) from parents in curent. Task was add to database.')

    # Tasks table refresh
    _, lst = interface2.create_sq_table(interface2.tasks1.cur)
    window['Tab'].update(values = lst)

    # Curent table refresh
    id_in_curent = tasks1.insert_to_curent(id_in_tasks)

    # Adding a row to layout in curent tab
    row = [task_layout(id_in_curent)]
    window.extend_layout(window["Today tasks"], row)

    return 

def add_task(con,table):
    '''
    Add task to table. Returns id in that table (or None if exit). Don't create a layout.
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
            temp = id_name_from_db(cur)
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

            task_id = tasks1.insert(table, values['name'], duration = duration, u_time = u_time, parent_id = parent_id, checkpoints = values['Checkpoints'], notes = values['-NOTES-'])

            con.commit()
            add = True

            break 

    window_add_tasks.close()
    

    if add:
        return task_id

    return 

# def  add_task2(con,table):
#     ''' The function that is starting when pressing add button on current tasks tab. The function is returning row and task_id (in the Tasks table). It also update the con.
#         '''
#     h = 60
#     v = 1
#     r = 2
#     s = 10

#     # some starting values:
    
#     parent_id = None
#     checkpoints_str = ''
#     cur = con.cursor()

#     Data = [
#             [
#             sg.Text('Task ', size = (h//3-r,v)), 
#             sg.Input(key = 'name',size = (h,v))
#             ],
               
#            [
#             sg.Text('Duration of a session',size = (h//3-r,v)),
#             sg.Input('hours',key = '-DURATIONh-',size = (h//3-r,v)),
#             sg.Input('minutes',key = '-DURATIONm-',size = (h//3-r,v)),
#             sg.Input('seconds',key = '-DURATIONs-',size = (h//3-r,v))
#            ], 
        
#             [
#             sg.Text('Untruck Time',size = (h//3-r,v)),
#             sg.Input('hours',key = '-TIMEh-',size = (h//3-r,v)),
#             sg.Input('minutes',key = '-TIMEm-',size = (h//3-r,v)),
#             sg.Input('seconds',key = '-TIMEs-',size = (h//3-r,v))  
#             ],

#             [sg.Text('Parent',size = (h//3-r,v)), sg.Text('None', key = "Parent",size = (h//3-r,v)), sg.Stretch(), sg.Button('Select parent', key = 'Select parent')],
#             # pop up with db table

#             [sg.Text('Checkpoints',size = (h//3-r,v)),sg.Multiline(checkpoints_str, key = 'Checkpoints',size = (h-2,4)),],

#             # you removed  sg.Stretch(), sg.Button('Edit checkpoints', key = 'Edit checkpoints' )
        
#            [sg.Text('Notes', size = (h//3-r,v)), sg.Multiline(key = '-NOTES-',size = (h-2,4))] 
        
#     ]
    
#     layout = [[Data,sg.Button("Add", key = "-ADD-")]]
    
#     window_add_tasks = sg.Window("Add task",layout)

#     add = False
    
#     while True:
#         event, values = window_add_tasks.read()

#         if event == sg.WIN_CLOSED:
#             break

#         if event == 'Select parent':
#             temp = id_name_from_db(cur)
#             if temp != None:
#                 parent_id, parent_name = temp
#                 window_add_tasks['Parent'].update(f'Id: {parent_id} Name: {parent_name}')


            
#         if event == "-ADD-":
            
#             h = int(values['-DURATIONh-']) if is_number(values['-DURATIONh-']) else 0
#             m = int(values['-DURATIONm-']) if is_number(values['-DURATIONm-']) else 0
#             s = int(values['-DURATIONs-']) if is_number(values['-DURATIONs-']) else 0
#             duration = datetime.timedelta(hours = h, minutes = m, seconds = s)

#             h = int(values['-TIMEh-']) if is_number(values['-TIMEh-']) else 0
#             m = int(values['-TIMEm-']) if is_number(values['-TIMEm-']) else 0
#             s = int(values['-TIMEs-']) if is_number(values['-TIMEs-']) else 0
            
#             u_time = datetime.timedelta(hours = h, minutes = m, seconds = s)

#             task_id = tasks1.insert(table, values['name'], duration = duration, u_time = u_time, parent_id = parent_id, checkpoints = values['Checkpoints'], notes = values['-NOTES-'])

#             # cur.execute('SELECT * FROM Tasks')

#             # task_id = con.lastrowid
#             # print(task_id)
#             con.commit()
#             add = True

#             break 

#     window_add_tasks.close()
    

#     if add:
#         raw = [task_layout(task_id)]
#         return raw, task_id

#     return





#     # check if the user exited
#         temp = buttons.add_task(con,'Tasks')
#         if temp is None:
#             continue

#         row,task_id = temp

#         # check if somebody from family is in curent
#         lst_of_parent = tasks1.get_parents('Tasks',task_id)


#         sql = 'SELECT * FROM Curent WHERE id IN ({0})'.format(', '.join('?' for _ in lst_of_parent))
#         tasks1.cur.execute(sql, tuple(lst_of_parent))

#         colision = tasks1.cur.fetchall()

#         if colision:
#             family_members = [row['name'] for row in colision]
#             sg.Popup(f'There is a task ({ ",".join(family_members) }) from parents in curent. Task was add to database.')
#             continue

#         window.extend_layout(window["Today tasks"], row)

#         _, lst = interface2.create_sq_table(interface2.tasks1.cur)
#         window['Tab'].update(values = lst)
#         # curent refresh
#         tasks1.insert_to_curent(task_id)

def edit_task(con, table, id, id_curent = None):
    ''' The function that is starting when pressing Edit button. It changes the data of Tasks table and update database.
    '''
    # In future you want to distinquish edit global and edit local (just in current?)
    h = 60
    v = 1
    r = 2
    s = 10

    task = tasks1.get_row('Tasks',id)
    
    if task['parent_id'] is not None:
        parent_id = int(task['parent_id'])
        parent_name = tasks1.get_row('Tasks',parent_id)['name']
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

            [sg.Text('Parent',size = (h//3-r,v)), sg.Text(parent_string, key = "Parent",size = (h//3-r,v)), sg.Stretch(), sg.Button('Select parent', key = 'Select parent')],
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
            temp = id_name_from_db(cur)
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

            sql = f'''UPDATE {table}
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
    


def id_name_from_db(cur):
    '''Returns id,name from coursor cur that you selected from database table.'''


    t, lst = interface2.create_sq_table(interface2.tasks1.cur)

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

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    except TypeError:
        return False




# con = sqlite3.connect('data.db')

# add_task(con,'Tasks')

# edit_checkpoints(['do this', 'remember this'])
# print(read_value('miki','some values'))

# con.close()
        