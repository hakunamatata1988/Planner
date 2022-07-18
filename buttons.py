import PySimpleGUI as sg
import datetime


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


def add_task():
    ''' The function that is starting when pressing add button on current tasks tab. The function is returning raw, an object that you should extend the layout of current tasks tab. It also update the database 
    '''
    h = 60
    v = 1
    r = 2
    s = 10
    multiline_high = 5
    Column1 = [[sg.Text('Task ')],[sg.Text('Duration')],[sg.Text('Untruck Time')],[sg.Text('Notes',size = (s,multiline_high))]]
    Column2 = [
            [sg.Input(key = 'name',size = (h,v))],
               
           [
            sg.Input('hours',key = '-DURATIONh-',size = (h//3-r,v)),
            sg.Input('minutes',key = '-DURATIONm-',size = (h//3-r,v)),
            sg.Input('seconds',key = '-DURATIONs-',size = (h//3-r,v))
           ], # check how to dived raws
        
            [
            sg.Input('hours',key = '-TIMEh-',size = (h//3-r,v)),
            sg.Input('minutes',key = '-TIMEm-',size = (h//3-r,v)),
            sg.Input('seconds',key = '-TIMEs-',size = (h//3-r,v))  
            ],

            [sg.Stretch(), sg.Button('Select parent')],

            [sg.Stretch(), sg.Button('Add checkpoint')],
        
           [sg.Multiline(key = '-NOTES-',size = (h,5))] 
        
    ]
    
    layout = [[sg.Column(layout = Column1),sg.Column(layout = Column2)],[sg.Button("Add", key = "-ADD-")]]
    
    window_add_tasks = sg.Window("Add task",layout)
    
    while True:
        event, values = window_add_tasks.read()

        if event == sg.WIN_CLOSED:
            break
            
        if event == "-ADD-":
            duration = datetime.timedelta(hours = values['-DURATIONh-'], minutes = values['-DURATIONm-'], seconds = values['-DURATIONs-'])
            
            time = datetime.timedelta(hours = values['-TIMEh-'], minutes = values['-TIMEm-'], seconds = values['-TIMEs-'])

            # task = Task(values['-TASK-'], duration,time, values['-NOTES-'])
            # database update and get task id
            task_id = 3
            break 

    raw = [task_layout(task_id)]

    window_add_tasks.close()

    return raw

add_task()
