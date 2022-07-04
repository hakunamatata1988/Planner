# %%
import datetime
import copy

class Task():
    def __init__(self, name , duration = 0, s_time = 0, parent = None):
        # name = name of the task
        self.name = name

        # duration = lonag are you planing to do a task
        # format = ??
        self.duration = duration

        # time = how long have you been doing the task
        # format = ??
        self.s_time = s_time

        # subtasks = a list of subtasks that self is divided to
        # elements of a subtasks list can be task instances or strings that represents name of a subtasks (in case the subtasks not exist as a instance of a task class yet)
        self.subtasks = []

        # Add some object that will store the information when the tasks was going

        # May be usefull to add a pointer to the parent
        # Potentially you may want to show all parents (i.e parent of parent)
        # There may be some situation when you want more then one 'direct' parent
        # You want to avoid loops in the tree of tasks
        self.parents = []

        if parent:
            self.parents += parent.parents
            parent.add(self)


        self.active = False

        # list of pairs [start,stop] that represents period of time that the task was performed
        self.time_history = []

    def add(self, task):
        self.subtasks.append(task)
        task.parents = [self] + self.parents

        # update child's parents
        def update(childs):
            if childs == []:
                return
            for child in childs:
                child.parents += task.parents
                update(child)

        update(task.subtasks)


    def remove(self, task):
        self.subtasks.remove(task)

    def divid(self, *tasks):
        # doesnt look useful for now
        # make more sense to add one task at the time
        pass

    def activate(self):
        if self.active:
            return

        self.active = True
        now = datetime.datetime.today()
        self.time_history.append([now])
        for parent in self.parents:
            if parent.active:
                continue
            parent.active = True
            parent.time_history.append([now])

    def childs(self):
        # Returns the list of all childes (all generations)

        def childs_recurence(task,lst):
            if not task.subtasks:
                return lst
            else:
                lst += task.subtasks
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
        for parent in self.parents: # the order in self.parents is important
            parent.active = False
            for child in parent.subtasks:
                if child.active:
                    parent.active = True
                    break

            if parent.active == False:
                parent.time_history[-1].append(now)

        # update the state of childs
        for child in self.childs():
            if not child:
                continue
            if child.active == False:
                continue

            child.active = False
            child.time_history[-1].append(now)

    def time(self):
        history = copy.deepcopy(self.time_history)
        if not history:
            return datetime.timedelta(0)

        if self.active:
            history[-1].append(datetime.datetime.today())
            
        t = datetime.timedelta(0)
        for start,end in history:
            dt = end - start
            t += dt

        return t

    
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

        str =  f"Task's name : {self.name}.\nTask's parents: {parents}.\nActive : {self.active}.\nTask's history: {self.time_history}.\nTask's duration : {self.duration}.\nTasks's time : {self.time}.\nSubtasks: {subtasks}."
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

