import PySimpleGUI as sg
import interface2
import buttons
import sqlite3
import tasks1
import datetime
# think if your imports are optimal, any circular imports?

# change lst to window['Tab'] ???


starting_tasks = [] # should be loaded from curent

bcolor = sg.theme_background_color()
tcolor = sg.theme_text_color()

file = 'data.db'
con = sqlite3.connect(file) # file should be chosen by user, note that you are using one conection
# conection and cursor probably should be in the same file

# Curent tab layout
tab1_layout = [
        [sg.Frame("Tasks", key = "Today tasks", layout = buttons.tasks_layout(starting_tasks))],
        [sg.VStretch()],
        [
            sg.Button("Add task", key = "-ADD TASK-"),
            sg.Button("Clear", key = "-CLEAR-"),
            sg.Button("Day", key = "-DAY-"), 
            sg.Stretch(), 
            sg.Text(key = "INFO", justification= "right")
            ]
    ]

# Database tab layout
t,lst = interface2.create_sq_table(interface2.tasks1.cur)

tab2_layout= [
    [t, sg.Multiline("Just some description of the task",key = "description", expand_y = True, background_color = bcolor, text_color = tcolor)],
    [
        sg.Button("Add to db", key = "Add to db"),
        sg.Button("Remove from db", key = "Remove from db"),
        sg.Button("Add to current", key = "Add to current")
        ]
    ]


# Window layout
layout = [[
    sg.TabGroup([[
        sg.Tab('Curent tasks', tab1_layout), 
        sg.Tab('Database', tab2_layout, key = 'Tab database')]],
        key = 'Tab group', enable_events= True)
    ]] 

window = sg.Window('Tracker', layout, default_element_size=(12,1), finalize = True, )    

while True:    

    event, values = window.read(timeout = 20)    
    # print(event,values)  

    if event == sg.WIN_CLOSED: 
        # Saving progress of curent active tasks

        tasks1.cur.execute("Select * FROM Curent WHERE active = 'True'",)
        for task in tasks1.cur.fetchall():
            # from id in current to id in tasks
            id_curent = int(task['id'])
            id_task = int(task['id_tasks'])

            tasks1.deactivate('Curent', id_curent, family = False) # deactivate not wirking on curent?
            tasks1.deactivate('Tasks', id_task)

        con.commit()  
        break  

    if event[0] == 'Tab':
        # getting id
        row = event[2][0]
        selected_id = lst[row][0]

        buttons.description(selected_id, window)
        

    if event == "-ADD TASK-":
        buttons.add_task_button(con,window)

    if event == "Add to current":
        # get id of selected row or do nothing if nothing is selected
        if values['Tab'] == []: 
            sg.Popup('Choose a task')
            continue
        [raw] = values['Tab']
        selected_id = lst[raw][0]

        buttons.add_to_curent(selected_id, window)

    if event == "Add to db":
        # check if the user exited earlier
        temp = buttons.add_task(con,'Tasks')
        if temp is None:
            continue
        task_id = temp

        # creating list with updated values
        _, lst = interface2.create_sq_table(interface2.tasks1.cur)

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

        buttons.remove_from_db(selected_id, lst, window)


    if isinstance(event,str) and event.split('-')[0] == "START":
        id = int(event.split('-')[1])
        sql = 'SELECT * FROM Curent WHERE id = ?'
        tasks1.cur.execute(sql, (id,))
        id_tasks = tasks1.cur.fetchone()['id_tasks']

        # checking if sb from family is active
        lst_of_parent = tasks1.get_parents('Tasks',id_tasks)
        lst_of_childs = tasks1.get_childs('Tasks',id_tasks)
        family = lst_of_parent + lst_of_childs + [id_tasks]

        sql = 'SELECT * FROM Tasks WHERE id IN ({0}) AND active = "True"'.format(', '.join('?' for _ in family))
        tasks1.cur.execute(sql, tuple(family))

        colision = tasks1.cur.fetchall()

        if colision:
            family_members = [row['name'] for row in colision]
            sg.Popup(f'There is a task ({ ",".join(family_members) }) from family that is running. Pause it to start this one.')
            continue

        tasks1.activate('Curent',id, parents = False)
        tasks1.activate('Tasks',id_tasks)


    if isinstance(event,str) and event.split('-')[0] == "PAUSE":
        id = int(event.split('-')[1])
        id_task = tasks1.get_row('Curent',id)['id_tasks']

        # id = tasks1.get_row('Curent',id)

        tasks1.deactivate('Curent', id, family = False)
        tasks1.deactivate('Tasks', id_task)


    if event == '-CLEAR-':
        # just for testing
        tasks1.show_table('Curent')

    if event == '-DAY-':
        # just for testing
        tasks1.show_table('Tasks')

    tasks1.cur.execute("Select * FROM Curent WHERE active = 'True'",)
    for task in tasks1.cur.fetchall():
        # from id in current to id in tasks
        id_curent = int(task['id'])
        id_task = int(task['id_tasks'])

        t = tasks1.time('Curent', id_curent)
        d = eval(task['duration']).total_seconds()
        window['TIME-' + str(id_curent)].update(str(t).split('.')[0])
        window['PROGRESS-' + str(id_curent)].update(current_count = t.total_seconds(), max=d)

    
    if event == 'Tab group':
        _, lst = interface2.create_sq_table(interface2.tasks1.cur)
        window['Tab'].update(values = lst)

    if isinstance(event,str) and event.split('-')[0] == "EDIT":
        id = int(event.split('-')[1])
        sql = 'SELECT * FROM Curent WHERE id = ?'
        tasks1.cur.execute(sql, (id,))
        task =  tasks1.cur.fetchone()
        id_tasks = task['id_tasks']


        buttons.edit_task(con, 'Tasks', id_tasks, id)
        tasks1.cur.execute(sql, (id,))
        task =  tasks1.cur.fetchone()
        # name update
        window['TASK NAME-' + str(id)].update(task['name'])
        # progresbarr update
        t = tasks1.time('Curent', id)
        d = eval(task['duration']).total_seconds()
        window['TIME-' + str(id)].update(str(t).split('.')[0])
        window['PROGRESS-' + str(id)].update(current_count = t.total_seconds(), max=d)





print('window closing')
window.close()
