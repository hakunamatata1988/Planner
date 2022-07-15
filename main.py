import PySimpleGUI as sg
import interface2


tab1_layout =  [[sg.T('This is inside tab 1')]]    

Tab = interface2.create_sq_table(interface2.tasks1.cur)

tab2_layout = [[Tab]]    # note that this is loaded at the beginning, what if the data change?

layout = [[
    sg.TabGroup([[
        sg.Tab('Current', tab1_layout, tooltip='tip'), 
        sg.Tab('Database', tab2_layout)]], 
        tooltip='TIP2')
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