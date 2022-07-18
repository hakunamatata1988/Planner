import PySimpleGUI as sg
import interface2
import buttons


starting_tasks = [None]*4

tab1_layout = [
        [sg.Frame("Tasks",key = "Today tasks",layout = buttons.tasks_layout(starting_tasks)   )],
        [sg.Button("Add task", key = "-ADD TASK-"),sg.Button("Clear", key = "-CLEAR-"),sg.Button("Day", key = "-DAY-"), sg.Stretch(), sg.Text(key = "INFO", justification= "right")]
    ]


tab2_layout,lst = interface2.create_sq_table(interface2.tasks1.cur)

# note that this is loaded at the beginning, what if the data change?

layout = [[
    sg.TabGroup([[
        sg.Tab('Current tasks', tab1_layout), 
        sg.Tab('Database', tab2_layout)]])
    ]] 

# tool tip -> podpowiedź

window = sg.Window('My window with tabs', layout, default_element_size=(12,1))    

while True:    

    event, values = window.read()    
    print(event,values)  
    if event == sg.WIN_CLOSED:             
        break  

    if event[0] == 'Tab' :
        #print('event = ', event, 'values = ',values['Tab'])
        print(event[2][0])
        # add task with right id to current tasks table
        # for now probably refresh the window
        # in future you can make some task not visable to get rid of refreshing effect