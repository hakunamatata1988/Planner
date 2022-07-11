# %%
import datetime
import sqlite3
import copy

con = sqlite3.connect('data.db')


def id_to_task(id):
    pass # return a Task object from database or return an error

class Task():
    def __init__(self, name , id , duration = datetime.timedelta(0), u_time = datetime.timedelta(0), parent = None):
        # name = name of the task
        self.name = name

        # id = unique number that identify task
        # need to add some logic for database
        self.id = id

        # duration = how long are you planing to do a task. timedelta object
        self.duration = duration

        # u_time = how long have you been doing the task untracted in time_history
        # note that this will not be implemented ni parents yet
        self.u_time = u_time

        # subtasks = a list of id subtasks that self is divided to
        self.subtasks_id = []

        # Add some object that will store the information when the tasks was going

        # List of parents' id
        # There may be some situation when you want more then one 'direct' parent
        # You want to avoid loops in the tree of tasks/parents
        # order is important, why?
        self.parents_id = []

        if parent:
            self.parents += parent.parents
            parent.add_subtask(self) 

        # list of a checkpoints, checkpoint suppose to be of str type
        # think how to make use of checkpoints and subtasks that make sense
        self.checkpoints = []

        self.active = False

        # list of [start,stop] that represents period of time that a task (or a child) was performed, 
        # start and stop are datetime.datetime objects
        # add a function (?) that shows was going on at this periods (i.e. what subtasks was running)
     
        self.time_history = []

        self.notes = ''

    def add_subtask(self, task):
        self.subtasks_id.append(task.id)
        task.parents_id = [self] + self.parents_id

        # update child's parents
        def update(childs_id):
            if childs_id == []:
                return
            for id in childs_id:
                child = id_to_task(id)
                child.parents += task.parents_id
                update(id)


        update(task.subtasks_id)

        # save all changes to db


    def remove(self, task):
        self.subtasks_id.remove(task.id)
        # save chenges to db

    def deletet(task):
        pass


    def activate(self):
        # you can try diffrent implementation when db will be done

        if self.active:
            return

        self.active = True
        now = datetime.datetime.today()
        self.time_history.append([now])
        for id in self.parents_id:
            parent = id_to_task(id)
            if parent.active:
                continue
            parent.active = True
            parent.time_history.append([now])

        # save chenges to db

    def childs(self):
        # Returns the list of ids of all childes (all generations)

        def childs_recurence(task,lst):
            if not task.subtasks_id:
                return lst
            else:
                lst += task.subtasks_id
                for sub in task.subtasks:
                    childs_recurence(sub, lst)

            return lst

        return childs_recurence(self, [])

    def deactivate(self):
        if not self.active:
            return

        self.active = False
        now = datetime.datetime.today()
        self.time_history[-1].append(now)


        # update the state of parents
        for id in self.parents_id: # the order in self.parents is important
            parent = id_to_task(id)
            parent.active = False
            for id in parent.subtasks_id:
                child = id_to_task(id)
                if child.active:
                    parent.active = True
                    break

            if parent.active == False:
                parent.time_history[-1].append(now)

            #    save

        # update the state of childs
        for id in self.childs():
            child = id_to_task(id)
            if not child:
                continue
            if child.active == False:
                continue

            child.active = False
            child.time_history[-1].append(now)

        # save

    def time(self):
        history = copy.deepcopy(self.time_history)
        if not history:
            return self.u_time

        if self.active:
            history[-1].append(datetime.datetime.today())
            
        t = datetime.timedelta(0)
        for start,end in history:
            dt = end - start
            t += dt

        return t + self.u_time

    def add_checkpoint(self, name, done = False, notes = ''):
        checkpoint = Checkpoint(name, done, notes) 
        self.checkpoints.append(checkpoint)   


    
    def __getitem__(self, idx):
        return self.subtasks[idx]

    def __setitem__(self, idx, task):
        self.subtasks[idx] = task

    def __iter__(self):
        return (x for x in self.subtasks)

    def __str__(self):

        if not self.parents:
            parents = "None"
        else:
            parents_names = (p.name for p in self.parents)
            parents = "-> ".join(parents_names)


        if not self.subtasks:
            subtasks = "None"
        else:
            subtasks_names_lst = []
            for task in self.subtasks:
                if isinstance(task,Task):
                    subtasks_names_lst.append(task.name)
                else:
                    subtasks_names_lst.append(task) # task is str case

            subtasks = ', '.join(subtasks_names_lst)

        str =  f"Name : {self.name}.\nParents: {parents}.\nActive : {self.active}.\nTime history: {self.time_history}.\nDuration : {self.duration}.\nUntracted time : {self.u_time}.\nTime : {self.time()}.\nSubtasks: {subtasks}.\nCheckpoints : {self.checkpoints}.\nNotes : {self.notes}."
        return str


    def __repr__(self):
        return self.name


# random tree for testing
# %%
learning = Task("learning")

math = Task("math", parent = learning)

algebra = Task("algebra", parent = math)
pol_div = Task("polynomial division", parent = algebra)

topology = Task("topology", parent = math)

python = Task("python", parent = learning)

data_str = Task("data structures", parent = python)

trees = Task("trees", parent = data_str)
lists = Task("lists", parent = data_str)

decorators = Task("decorator", parent = python)
oop = Task("oop", parent = python)

cl = Task("cl", parent = oop)
inheritence = Task("inheritence", parent = oop)
atr = Task("atr", parent = oop)

class Checkpoint():
    # Class that represents checkpoint in your tasks
    # May want to convert checkpoints to tasks (and tasks to check points?)

    def __init__(self, name, done = False, notes = ''):
        self.name = name
        self.done = done
        self.notes = notes

    # not sure if that is working correctly
    def __repr__(self):
        done = "done" if self.done else "not done"
        return f"({self.name}, {done}, {self.notes})"

    def checkpoint_status(self):
        self.done = not self.done

    def checkpoint_to_task(self,parent):
        pass