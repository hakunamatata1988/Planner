'''
Run to quickly set up some database. Table Curent will be empty.
'''


import db_func


db_func.delete_table("Tasks")
db_func.create_table("Tasks")
db_func.delete_table("Curent")
db_func.create_table_curent()


db_func.insert("Tasks","new task1")
db_func.insert("Tasks","new task2", parent_id =1)
db_func.insert("Tasks","new task3", parent_id =1)
db_func.insert("Tasks","new task4", parent_id =2)
db_func.insert("Tasks","new task5")
db_func.insert("Tasks","new task6", parent_id =5)
db_func.insert("Tasks","new task7", parent_id =5)
db_func.insert("Tasks","new task8", parent_id =7)

# db_func.insert_to_curent(1)
# db_func.insert_to_curent(7)
# db_func.insert_to_curent(2)
# db_func.insert_to_curent(3)

table = "Tasks"

# db_func.activate('Curent',1, parents = False)
# db_func.deactivate('Curent',1,family = False)


# db_func.activate(table, 5)
# db_func.deactivate(table,5)
# db_func.add_checkpoint(table, 1, 
# 'buy a milk')

# db_func.show_table("Tasks")
# db_func.show_table('Curent')

# print('time 1 = ',time('Curent', 1))
# print(time(table, 5))
# db_func.con.commit()

# db_func.con.close()

# %%