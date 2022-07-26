import PySimpleGUI as sg
import interface2
import buttons
import sqlite3
import tasks1
import datetime


starting_tasks = []
bcolor = sg.theme_background_color()
tcolor = sg.theme_text_color()

con = sqlite3.connect('data.db')

tab1_layout = [
        [sg.Frame("Tasks", key = "Today tasks",layout = buttons.tasks_layout(starting_tasks),   )],
        [sg.VStretch()],
        [sg.Button("Add task", key = "-ADD TASK-"),sg.Button("Clear", key = "-CLEAR-"),sg.Button("Day", key = "-DAY-"), sg.Stretch(), sg.Text(key = "INFO", justification= "right")]
    ]

t,lst = interface2.create_sq_table(interface2.tasks1.cur)

tab2_layout= [
    [t, sg.Multiline("Just some description of the task",key = "description", expand_y = True, background_color = bcolor, text_color = tcolor)],
    [sg.Button("Add to db", key = "Add to db"),
    sg.Button("Remove from db", key = "Remove from db"),
    sg.Button("Add to current", key = "Add to current")]
    ]


# note that this is loaded at the beginning, what if the data change?

layout = [[
    sg.TabGroup([[
        sg.Tab('Curent tasks', tab1_layout), 
        sg.Tab('Database', tab2_layout, key = 'Tab database')]],
        key = 'Tab group', enable_events= True)
    ]] 

# tool tip -> podpowiedź

window = sg.Window('My window with tabs', layout, default_element_size=(12,1), finalize = True, )    

while True:    

    event, values = window.read(timeout = 20)    
    # print(event,values)  
    if event == sg.WIN_CLOSED: 
        # Saving progress of curent active tasks
        for task in lst:
            id = int(task[0])
            tasks1.deactivate('Curent',id, family = False)
            tasks1.deactivate('Tasks',id)

        con.commit()  
        break  

    if event[0] == 'Tab' :
        pass
        # print('events = ', event ,' values:', values)
        row = event[2][0]
        selected_id = lst[row][0]
        selection = tasks1.get_row('Tasks', selected_id)

        if selection['parent_id'] is None:
            parent = 'None'
        else:
            parent = tasks1.get_row(tasks1.table, int(selection['parent_id']))['name']

        subtasks = []
        for id_s in eval(selection['subtasks_id']):
            subtasks.append(tasks1.get_row(tasks1.table, id_s)['name'])

        subtasks = ', '.join(subtasks)

        string = f'''Name:\n{selection['name']}\n\nParent:\n{parent}\n\nSubtasks:\n{subtasks}\n\nCheckpoints:\n{selection['checkpoints']}\n\nNotes:\n{selection['notes']}       
        
        '''
        window['description'].update(string)
        


    if event == "-ADD TASK-":
        buttons.add_task_button(con,window)

    if event == "Add to current":
        # get id of selected row or do nothing if nothing is selected
        if values['Tab'] == []: 
            sg.Popup('Choose a task')
            continue
        [raw] = values['Tab']
        selected_id = lst[raw][0]

        # check if somebody from family is in curent
        lst_of_parent = tasks1.get_parents('Tasks',selected_id)
        lst_of_childs = tasks1.get_childs('Tasks',selected_id)
        family = lst_of_parent + lst_of_childs + [selected_id]

        sql = 'SELECT * FROM Curent WHERE id_tasks IN ({0})'.format(', '.join('?' for _ in family))
        tasks1.cur.execute(sql, tuple(family))

        colision = tasks1.cur.fetchall()

        if colision:
            family_members = [row['name'] for row in colision]
            sg.Popup(f'There is a task ({ ",".join(family_members) }) from family in curent.')

        # need to update some object that truck what is in current
        id_in_cur = tasks1.insert_to_curent(selected_id)

        # create a layout
        row = [buttons.task_layout(id_in_cur)]

        # extend the window['Today tasks']
        window.extend_layout(window["Today tasks"], row)

    if event == "Add to db":
        # check if the user exited
        temp = buttons.add_task(con,'Tasks')
        if temp is None:
            continue
        row,task_id = temp
        _, lst = interface2.create_sq_table(interface2.tasks1.cur)
        window['Tab'].update(values = lst)

    if event == "Remove from db":
        # get id of selected row or do nothing if nothing is selected
        if values['Tab'] == []: 
            sg.Popup('Choose a task')
            continue
        [raw] = values['Tab']
        selected_id = lst[raw][0]

        # check if task has a subtasks 
        row = tasks1.get_row('Tasks',selected_id)
        if eval(row['subtasks_id']) != []:
            sg.Popup(f'There are some subtasks!') # lazy
            continue

        # check if it is in current!!

        # check if task has a parent and remove it from parent 
        if row['parent_id'] != None:
            parent_id = row['parent_id']
            parent = tasks1.get_row('Tasks',parent_id)
            # print('list = ', eval(parent['subtasks_id']), ' id = ', selected_id)
            sub_lst = eval(parent['subtasks_id'])
            sub_lst.remove(selected_id)
            # print(update_lst)
            tasks1.cur.execute(f"UPDATE {'Tasks'} SET subtasks_id = ? WHERE id = {parent_id}", (repr(sub_lst),))

        
        # remove task from db
        tasks1.delete('Tasks', selected_id)

        # refresh Tab
        _, lst = interface2.create_sq_table(interface2.tasks1.cur)
        window['Tab'].update(values = lst)

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
