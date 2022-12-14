import threading
import traceback

GLOBAL_ERROR = []

def __excepthook__(args):
    traceback_message = traceback.format_exc() + "\n"

    global GLOBAL_ERROR
    GLOBAL_ERROR.append((traceback_message, args))

threading.excepthook = __excepthook__

class SequentialGroup:
    def __init__(self):
        self.concurrent_steps = []

    def add_step(self, step):
        self.concurrent_steps.append(step)

    def get_all_steps(self):
        return self.concurrent_steps
    
    def run_all_steps(self, step_definition_instance):
        global GLOBAL_ERROR

        thread_list = []
        for step in self.concurrent_steps:
            thread_list.append(threading.Thread(target=getattr(step_definition_instance, step.method_name), name=step.description, kwargs=step.kwargs))

        for t in thread_list:
            t.start()

        while thread_list:
            for t in thread_list[:]:
                if not t.is_alive():
                    t.join()
                    thread_list.remove(t)

        return GLOBAL_ERROR
        