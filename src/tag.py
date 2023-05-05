from functools import wraps
from .custom_test_loader import CustomTestLoader
from .feature import FeatureManager

def tag(tag_name):
    if tag_name.find(' ') != -1: raise Exception(f"Tag <{tag_name}> cannot contain space.")
    def wrap_tagged_func(func):
        @wraps(func)
        def decorator(*args, **kargs):
            return func(*args, **kargs)
        
        if isinstance(func, type):
            CustomTestLoader.test_class_to_tag(func.__qualname__, tag_name)
            FeatureManager.add_feature_tag(func.__qualname__, tag_name)
            return type(decorator.__name__, (func,), dict(decorator.__dict__))
        else:
            CustomTestLoader.test_method_to_tag(func.__qualname__, tag_name)
            FeatureManager.add_scenario_tag(func.__qualname__.split('.')[0], func.__qualname__.split('.')[1], tag_name)
            return decorator
    return wrap_tagged_func