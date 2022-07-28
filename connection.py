from main import file
import sqlite3
import interface2

con = sqlite3.connect(file)
interface2.create_sq_table(interface2.tasks1.cur)

