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
            # print(id_s)
            subtasks.append(tasks1.get_row(tasks1.table, id_s)['name'])

        subtasks = ', '.join(subtasks)

        time = tasks1.time(tasks1.table, raw['id']) 
        time_str = str(time).split(".")[0] # it get rids of miliseconds

        lst.append([id,name, parent, subtasks, time_str])

    Tab = sg.Table(values = lst, headings = headings, enable_click_events = True, key = 'Tab')
    
    return Tab, lst



    