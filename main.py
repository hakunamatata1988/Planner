import PySimpleGUI as sg
import interface2
import buttons
import sqlite3
import tasks1


starting_tasks = [None]*4

con = sqlite3.connect('data.db')

tab1_layout = [
        [sg.Frame("Tasks", key = "Today tasks",layout = buttons.tasks_layout(starting_tasks)   )],
        [sg.Button("Add task", key = "-ADD TASK-"),sg.Button("Clear", key = "-CLEAR-"),sg.Button("Day", key = "-DAY-"), sg.Stretch(), sg.Text(key = "INFO", justification= "right")]
    ]

t,lst = interface2.create_sq_table(interface2.tasks1.cur)

tab2_layout= [
    [t],
    [sg.Button("Add to db", key = "Add to db"),
    sg.Button("Remove from db", key = "Remove from db"),
    sg.Button("Add to current", key = "Add to current")]
    ]


# note that this is loaded at the beginning, what if the data change?

layout = [[
    sg.TabGroup([[
        sg.Tab('Curent tasks', tab1_layout), 
        sg.Tab('Database', tab2_layout)]])
    ]] 

# tool tip -> podpowiedź

window = sg.Window('My window with tabs', layout, default_element_size=(12,1))    

while True:    

    event, values = window.read()    
    # print(event,values)  
    if event == sg.WIN_CLOSED:             
        break  

    if event[0] == 'Tab' :
        pass
        # print('values:', values)
        # data_selected = [t[row] for row in values[event]]
        # print(data_selected)

    if event == "-ADD TASK-":
        row,task_id = buttons.add_task(con,'Tasks')
        window.extend_layout(window["Today tasks"], row)
        _, lst = interface2.create_sq_table(interface2.tasks1.cur)
        window['Tab'].update(values = lst)
        # starting_tasks refresh

    if event == "Add to current":
        # get id of selected row or do nothing if nothing is selected
        if values['Tab'] == []: 
            print('nothing is selected')
            continue
        [raw] = values['Tab']
        selected_id = lst[raw][0]

        # create a layout
        row = [buttons.task_layout(selected_id)]

        # extend the window['Today tasks']
        window.extend_layout(window["Today tasks"], row)

        # not sure what you want to do if task is already in current
        # need to update some object that truck what is in current


    if event == "Add to db":
        row,task_id = buttons.add_task(con,'Tasks')
        _, lst = interface2.create_sq_table(interface2.tasks1.cur)
        window['Tab'].update(values = lst)

    if event == "Remove from db":
        # get id of selected row or do nothing if nothing is selected
        if values['Tab'] == []: 
            print('nothing is selected')
            continue
        [raw] = values['Tab']
        selected_id = lst[raw][0]

        # check if task has a subtasks 
        row = tasks1.get_row('Tasks',selected_id)
        if eval(row['subtasks_id']) != []:
            print('there are subtasks!') # print somwhere in gui
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







print('window closing')
window.close()
