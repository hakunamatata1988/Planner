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
    
    checkpoints = []

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

            [sg.Text('Parent',size = (h//3-r,v)), sg.Text('None', key = "Parent",size = (h//3-r,v)), sg.Stretch(), sg.Button('Select parent', key = 'Select parent')],
            # pop up with db table

            [sg.Text('Checkpoints',size = (h//3-r,v)),sg.Text(str(checkpoints), key = 'Checkpoints',size = (h//3-r,v)), sg.Stretch(), sg.Button('Edit checkpoints', key = 'Edit checkpoints' )],
        
           [sg.Text('Notes', size = (h//3-r,v)), sg.Multiline(key = '-NOTES-',size = (h,5))] 
        
    ]
    
    layout = [[Data,sg.Button("Add", key = "-ADD-")]]
    
    window_add_tasks = sg.Window("Add task",layout)
    
    while True:
        event, values = window_add_tasks.read()

        if event == sg.WIN_CLOSED:
            break

        if event == 'Select parent':
            parent_id, parent_name = id_name_from_db(cur)
            window_add_tasks['Parent'].update(f'Id: {parent_id} Name: {parent_name}')



        if event == 'Edit checkpoints':
            checkpoints = edit_checkpoints(checkpoints)
            window_add_tasks['Checkpoints'].update(str(checkpoints))

            
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

def id_name_from_db(cur):
    t, lst = interface2.create_sq_table(interface2.tasks1.cur)

    window = sg.Window('Database', layout =[[t],[sg.Button("Choose", key = "Choose")]], default_element_size=(12,1))

    while True:    

        event, values = window.read()    

        if values['Tab'] and event == "Choose":
            id = lst[values['Tab'][0]][0]
            name = lst[values['Tab'][0]][1]
            break


        if event == sg.WIN_CLOSED:             
            break  

    window.close()
    return id,name

def edit_checkpoints(checkpoints):
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
    layout = [[sg.Input(value, key = 'Input')], [sg.Submit('Save'), sg.Cancel('Cancel')]]
     
    window = sg.Window(title, layout)    

    event, values = window.read()    
    window.close()

    return event, values





con = sqlite3.connect('data.db')

add_task(con)
# edit_checkpoints(['do this', 'remember this'])
# print(read_value('miki','some values'))

con.close()
        
