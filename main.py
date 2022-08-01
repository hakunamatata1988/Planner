import PySimpleGUI as sg
import interface
import sqlite3
import db_func
import datetime
from re import split

# think if your imports are optimal, any circular imports?

def create_window():
    '''
    Need when refreshing window
    '''

    global lst, con, cur
    global bcolor, tcolor

    bcolor = sg.theme_background_color()
    tcolor = sg.theme_text_color()

    con = db_func.con 
    cur = db_func.cur

    # selecting all ids from curent
    # may be a good ide to add this code to tasks_layout
    cur.execute("SELECT id FROM CURENT")
    ids_curent = []
    for task in cur.fetchall():
        ids_curent.append(task['id'])



    # Curent tab layout
    tab1_layout = [
            [sg.Frame("Tasks", expand_x = True, key = "Today tasks", layout = interface.tasks_layout(ids_curent))],
            [sg.VStretch()],
            [sg.Text(size = (4,None)), sg.Text(key = "-INFO TOTAL-", size = (29, None)), sg.ProgressBar(0,size = (10,20), expand_x = True, key = "PROGRESS-Total" ),sg.Text('time', key = "TIME-TOTAL",size = (6,None))],
            [
                sg.Button("Add task", key = "-ADD TASK-"),
                sg.Button("Clear Curent", key  = "-CLEAR CURENT-"),
                sg.Stretch(),
                sg.Button("Curent", key = "-CURENT-"),
                sg.Button("Tasks", key = "-TASKS-"), 
                sg.Button("Test", key = "Test"),
                sg.Stretch(), 
                sg.Text(key = "INFO", size = (15,None), justification= "right")
                ]
        ]

    # Database tab layout
    t,lst = interface.create_sq_table()

    tab2_layout= [
        [t, sg.Multiline("Just some description of the task",key = "description", expand_y = True, expand_x = True, background_color = bcolor, text_color = tcolor)],
        [
            sg.Button("Add to current", key = "Add to current"),
            sg.Button("Add to db", key = "Add to db"),
            sg.Button("Remove from db", key = "Remove from db"),
            ]
        ]


    # Window layout
    layout = [[
        sg.TabGroup([[
            sg.Tab('Curent tasks', tab1_layout), 
            sg.Tab('Database', tab2_layout, key = 'Tab database')]],
            key = 'Tab group', enable_events= True)
        ]] 

    window = sg.Window('Tracker', layout, default_element_size=(12,1), finalize = True)    

    # to update a progress bar
    interface.update(window, start = True)

    return window

window = create_window()

while True:    

    event, values = window.read(timeout = 20)    
    # print(event,values)  

    if event == sg.WIN_CLOSED: 
        # Saving progress of curent active tasks

        db_func.cur.execute("Select * FROM Curent WHERE active = 'True'",)
        for task in db_func.cur.fetchall():
            # from id in current to id in tasks
            id_curent = int(task['id'])
            id_task = int(task['id_tasks'])

            db_func.deactivate('Curent', id_curent, family = False)
            db_func.deactivate('Tasks', id_task)

        con.commit()  
        break  

    if event[0] == 'Tab':
        # getting id
        row = event[2][0]
        
        # print('row =', row)
        # print('lst = ', lst)

        if row is None:
            continue
        selected_id = lst[row][0]

        interface.description(selected_id, window)
        

    if event == "-ADD TASK-":
        interface.add_task_button(window)

    if event == "Add to current":
        # get id of selected row or do nothing if nothing is selected
        if values['Tab'] == []: 
            sg.Popup('Choose a task')
            continue
        [raw] = values['Tab']

        selected_id = lst[raw][0]

        interface.add_to_curent(selected_id, window)

    if event == "Add to db":
        # check if the user exited earlier
        temp = interface.add_task()
        if temp is None:
            continue
        task_id = temp

        # creating list with updated values
        _, lst = interface.create_sq_table()

        # updating the table
        window['Tab'].update(values = lst)

    if event == "Remove from db":
        # add some info that task wont be in raports

        # get id of selected row or do nothing if nothing is selected
        if values['Tab'] == []: 
            sg.Popup('Choose a task')
            continue
        [raw] = values['Tab']
        selected_id = lst[raw][0]

        interface.remove_from_db(selected_id)

        # refresh Tab
        _, lst = interface.create_sq_table()
        window['Tab'].update(values = lst)


    if isinstance(event,str) and event.split('-')[0] == "START":
        id = int(event.split('-')[1])
        sql = 'SELECT * FROM Curent WHERE id = ?'
        db_func.cur.execute(sql, (id,))
        id_tasks = db_func.cur.fetchone()['id_tasks']

        # checking if sb from family is active
        lst_of_parent = db_func.get_parents('Tasks',id_tasks)
        lst_of_childs = db_func.get_childs('Tasks',id_tasks)
        family = lst_of_parent + lst_of_childs + [id_tasks]

        sql = 'SELECT * FROM Tasks WHERE id IN ({0}) AND active = "True"'.format(', '.join('?' for _ in family))
        db_func.cur.execute(sql, tuple(family))

        colision = db_func.cur.fetchall()

        if colision:
            family_members = [row['name'] for row in colision]
            sg.Popup(f'There is a task ({ ",".join(family_members) }) from family that is running. Pause it to start this one.')
            continue

        db_func.activate('Curent',id, parents = False)
        db_func.activate('Tasks',id_tasks)


    if isinstance(event,str) and event.split('-')[0] == "PAUSE":
        id = int(event.split('-')[1])

        # you dont want to pause not active task (in curent, can be active in tasks)
        task = db_func.get_row('Curent',id)
        if task['active'] == "False":
            continue

        id_task = db_func.get_row('Curent',id)['id_tasks']

        db_func.deactivate('Curent', id, family = False)
        db_func.deactivate('Tasks', id_task)

    if event == "-CLEAR CURENT-":

        db_func.cur.execute("Select * FROM Curent WHERE active = 'True'")
        for task in db_func.cur.fetchall():
            # from id in current to id in tasks
            id_curent = int(task['id'])
            id_task = int(task['id_tasks'])

            db_func.deactivate('Curent', id_curent, family = False)
            db_func.deactivate('Tasks', id_task)

        db_func.delete_table("Curent")
        db_func.create_table_curent()

        con.commit()  

        window.close()
        window = create_window()




    if event == '-CURENT-':
        # just for testing
        db_func.show_table('Curent')

    if event == '-TASKS-':
        # just for testing
        db_func.show_table('Tasks')

    if event == "Test":
        print('values =', values)

    if event[-1] ==  '+':
        id_cur = split('[+-]',event)[-2]
        if id_cur == 'TOTAL':
            window['INFO'].update(interface.update(window))
            continue


        task = db_func.get_row('Curent', id_cur)

        t = db_func.time('Curent', id_cur)
        delta = eval(task['duration']) - t
        if delta < datetime.timedelta(0):
            duration_str = str(eval(task['duration'])).split('.')[0]
            text = f'Finished ({duration_str})'
        else:
            text = 'Remaining ' +str(delta).split('.')[0]
        window['INFO'].update(text)

    if event[-1] ==  '-':
        window['INFO'].update('')

    if event == 'Tab group':
        _, lst = interface.create_sq_table()
        window['Tab'].update(values = lst)

    if isinstance(event,str) and event.split('-')[0] == "EDIT":
        id = int(event.split('-')[1])
        sql = 'SELECT * FROM Curent WHERE id = ?'
        db_func.cur.execute(sql, (id,))
        task =  db_func.cur.fetchone()
        id_tasks = task['id_tasks']


        interface.edit_task(id_tasks, id)
        db_func.cur.execute(sql, (id,))
        task =  db_func.cur.fetchone()
        # name update
        window['TASK NAME-' + str(id)].update(task['name'])
        # progresbarr update
        t = db_func.time('Curent', id)
        d = eval(task['duration']).total_seconds()
        window['TIME-' + str(id)].update(str(t).split('.')[0])
        window['PROGRESS-' + str(id)].update(current_count = t.total_seconds(), max=d)
        window['TIME-' + str(id)].bind('<Enter>', '+')
        window['TIME-' + str(id)].bind('<Leave>', '-')

    # Updating a progress of tasks in curent
    interface.update(window)


con.commit()
con.close()
print('window closing')
window.close()
