import os

project_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

def get_dict_keys(dict):
    """Return a list containing dict's keys"""
    ret = list(dict.keys())
    return ret

def in_range(i, list):
    """Return if i is a valid index in list"""
    return i in range(len(list))

def get_lines(path):
    """Return path's line count"""
    with open(path, 'r') as f:
        ret = len(f.read().strip().split('\n'))

    return ret

def first_upper(string):
    return string[0].upper() + string[1:]