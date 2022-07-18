import interface2
import PySimpleGUI as sg
import datetime
import sqlite3



def task_layout(task_id = None):

    Tasks_options = [
        sg.Button('|>', key = "START-" + str(task_id)),
        sg.Button('||', key = "PAUSE-" + str(task_id)),
        sg.Button('#', key = "STOP-" + str(task_id)),
        sg.Button('Notes', key = "NOTES-" + str(task_id)),
        sg.Button('Edit', key = "EDIT-" + str(task_id)),
        sg.Button('Remove', key = "REMOVE-" + str(task_id))
        ]

    if task_id is None:
        total_time = datetime.timedelta(0)
        task_duration = 0
        name = 'Test'

    Tasks_progress = [sg.ProgressBar(task_duration , size = (10,20), expand_x = True, key = "PROGRESS-" + str(task_id))]

    Task_time = [sg.Text(str(total_time).split(".")[0], key = "TIME-" + str(task_id))]
    
    raw =  [sg.Checkbox('', key = 'CHECKBOX-' + str(task_id), enable_events= True)] + [sg.Text(name , key = 'TASK NAME-' + str(task_id))] + Tasks_options + Tasks_progress + Task_time

    return raw

def tasks_layout(tasks_lst):
    
    layout = [[]]
    
    for i,task in enumerate(tasks_lst):
        layout.append(task_layout(task))

    return layout


def add_task(cur):
    ''' The function that is starting when pressing add button on current tasks tab. The function is returning raw, an object that you should extend the layout of current tasks tab. It also update the database 
    '''
    h = 60
    v = 1
    r = 2
    s = 10
    multiline_high = 5
    Data = [
            [
            sg.Text('Task ', size = (h//3-r,v)), 
            sg.Input(key = 'name',size = (h,v))
            ],
               
           [
            sg.Text('Duration',size = (h//3-r,v)),
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

            [sg.Text('Parent',size = (h//3-r,v)), sg.Text('None',size = (h//3-r,v)), sg.Stretch(), sg.Button('Select parent', key = 'Select parent')],
            # pop up with db table

            [sg.Text('Checkpoints',size = (h//3-r,v)),sg.Stretch(), sg.Button('Add checkpoint', key = 'Add checkpoint' )],
        
           [sg.Text('Notes', size = (h//3-r,v)), sg.Multiline(key = '-NOTES-',size = (h,5))] 
        
    ]
    
    layout = [[Data,sg.Button("Add", key = "-ADD-")]]
    
    window_add_tasks = sg.Window("Add task",layout)
    
    while True:
        event, values = window_add_tasks.read()

        if event == sg.WIN_CLOSED:
            break

        if event == 'Select parent':
            show_db(cur)

        if event == 'Add checkpoint':
            print("Checkpoints")

            
        if event == "-ADD-":
            duration = datetime.timedelta(hours = values['-DURATIONh-'], minutes = values['-DURATIONm-'], seconds = values['-DURATIONs-'])
            
            time = datetime.timedelta(hours = values['-TIMEh-'], minutes = values['-TIMEm-'], seconds = values['-TIMEs-'])

            # task = Task(values['-TASK-'], duration,time, values['-NOTES-'])
            # database update and get task id
            task_id = None
            break 
    task_id = None
    raw = [task_layout(task_id)]

    window_add_tasks.close()

    return raw

def show_db(cur):
    t, lst = interface2.create_sq_table(interface2.tasks1.cur)

    window = sg.Window('Database', layout =[[t]], default_element_size=(12,1))

    while True:    

        event, values = window.read()    
        print('Event = ' ,event,'Values = ', values)  

        print('value = ', lst[int(event[2][0])][int(event[2][1])])


        if event == sg.WIN_CLOSED:             
            break  

con = sqlite3.connect('data.db')
add_task(con)

con.close()
        
