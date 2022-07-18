import PySimpleGUI as sg
import tasks1

def create_sq_table(cur):
    cur.execute(f"SELECT * FROM {tasks1.table}")
    data = cur.fetchall()

    headings = ['id','name', 'parent', 'subtasks', 'time']

    lst = []

    for raw in data:
        id = raw['id']
        name = raw['name']
        #print(name)
        if raw['parent_id'] is None:
            parent = 'None'
        else:
            parent = tasks1.get_row(tasks1.table, int(raw['parent_id']))['name']

        subtasks = []
        for id_s in eval(raw['subtasks_id']):
            subtasks.append(tasks1.get_row(tasks1.table, id_s)['name'])

        subtasks = ', '.join(subtasks)

        time = tasks1.time(tasks1.table, raw['id']) 
        time_str = str(time).split(".")[0] # it get rids of miliseconds

        lst.append([id,name, parent, subtasks, time_str])

    Tab = [[
        sg.Table(values = lst, headings = headings, enable_click_events = True, key = 'Tab')
        ],
        [
        sg.Button("Add to db", key = "Add to db"),
        sg.Button("Remove from db", key = "-Remove from db"),
        sg.Button("Add to current", key = "Add to current")
        ]
    ]
    return Tab,lst

