import interface2
import tasks1
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


def add_task(cur,table):
    ''' The function that is starting when pressing add button on current tasks tab. The function is returning raw, an object that you should extend the layout of current tasks tab. It also update the database 
    '''
    h = 60
    v = 1
    r = 2
    s = 10
    multiline_high = 5

    # some starting values:
    
    parent_id = None
    checkpoints_str = ''

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

            [sg.Text('Checkpoints',size = (h//3-r,v)),sg.Multiline(checkpoints_str, key = 'Checkpoints',size = (h-2,4)),],

            # you removed  sg.Stretch(), sg.Button('Edit checkpoints', key = 'Edit checkpoints' )
        
           [sg.Text('Notes', size = (h//3-r,v)), sg.Multiline(key = '-NOTES-',size = (h-2,4))] 
        
    ]
    
    layout = [[Data,sg.Button("Add", key = "-ADD-")]]
    
    window_add_tasks = sg.Window("Add task",layout)
    
    while True:
        event, values = window_add_tasks.read()

        if event == sg.WIN_CLOSED:
            break

        if event == 'Select parent':
            if id_name_from_db(cur) != None:
                parent_id, parent_name = id_name_from_db(cur)
                window_add_tasks['Parent'].update(f'Id: {parent_id} Name: {parent_name}')



        # if event == 'Edit checkpoints':
        #     checkpoints = edit_checkpoints(checkpoints)
        #     window_add_tasks['Checkpoints'].update('\n'.join(checkpoints))

            
        if event == "-ADD-":
            
            h = int(values['-DURATIONh-']) if is_number(values['-DURATIONh-']) else 0
            m = int(values['-DURATIONm-']) if is_number(values['-DURATIONm-']) else 0
            s = int(values['-DURATIONs-']) if is_number(values['-DURATIONs-']) else 0
            duration = datetime.timedelta(hours = h, minutes = m, seconds = s)

            h = int(values['-TIMEh-']) if is_number(values['-TIMEh-']) else 0
            m = int(values['-TIMEm-']) if is_number(values['-TIMEm-']) else 0
            s = int(values['-TIMEs-']) if is_number(values['-TIMEs-']) else 0
            
            u_time = datetime.timedelta(hours = h, minutes = m, seconds = s)

            tasks1.insert(table, values['name'], duration = duration, u_time = u_time, parent_id = parent_id)
            # task = Task(values['-TASK-'], duration,time, values['-NOTES-'])
            # database update and return task id and other necesery values

            task_id = cur.lastrowid
            cur.commit()
            add = True
            break 

    window_add_tasks.close()

    if add:
        raw = [task_layout(task_id)]
        return raw, task_id

    return 

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
            cancel = True          
            break  

    window.close()
    if not cancel:
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

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    except TypeError:
        return False




con = sqlite3.connect('data.db')
cur = con.cursor()

add_task(cur,'Tasks')

# edit_checkpoints(['do this', 'remember this'])
# print(read_value('miki','some values'))

con.close()
        