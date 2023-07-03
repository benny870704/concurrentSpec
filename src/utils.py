import sys, os
import inspect
import importlib.util

def get_table():
    calling_frame = inspect.currentframe()
    for _ in range(1):
        calling_frame = calling_frame.f_back
    method_name = calling_frame.f_code.co_name
    return calling_frame.f_locals.get('self').table.get(method_name, None)

def get_text():
    calling_frame = inspect.currentframe()
    for _ in range(1):
        calling_frame = calling_frame.f_back
    method_name = calling_frame.f_code.co_name
    return calling_frame.f_locals.get('self').text.get(method_name, None)

def is_file_empty(file_name):
    return os.path.isfile(file_name) and os.path.getsize(file_name) == 0

def is_instance(object, class_name):
    return type(object).__name__ == class_name

def import_module(import_module_name, file_location):
    if import_module_name in sys.modules:
        del sys.modules[import_module_name]
    spec = importlib.util.spec_from_file_location(import_module_name, file_location)
    steps_module = importlib.util.module_from_spec(spec)
    sys.modules[import_module_name] = steps_module
    spec.loader.exec_module(steps_module)
    
    return steps_module

def get_where_the_class_is_declared(stack_frame_count):
    calling_frame = inspect.currentframe()
    for _ in range(stack_frame_count):
        calling_frame = calling_frame.f_back
    
    location = f"{os.path.basename(calling_frame.f_code.co_filename)}:{calling_frame.f_lineno}"
    variables_of_calling_frame = calling_frame.f_locals
    class_variable = variables_of_calling_frame.get('cls', None)
    if class_variable is not None:
        class_name = class_variable.__name__
        return class_name, None, location
    else:
        class_name = variables_of_calling_frame.get('self', None).__class__.__name__
        if "test" in str(variables_of_calling_frame.get("self", None)):
            method_name = variables_of_calling_frame.get('self', None)._testMethodName
        else:
            method_name = "SystemScenario private method"
            
        return class_name, method_name, location

def get_where_the_function_is_called(stack_frame_count):
    calling_frame = inspect.currentframe()
    for _ in range(stack_frame_count):
        calling_frame = calling_frame.f_back
    
    location = f"{os.path.basename(calling_frame.f_code.co_filename)}:{calling_frame.f_lineno}"
    variables_of_calling_frame = calling_frame.f_locals
    class_variable = variables_of_calling_frame.get('cls', None)
    if class_variable is not None:
        class_name = class_variable.__name__
    else:
        class_name = variables_of_calling_frame.get('self', None).__class__.__name__
        
    return class_name, location

