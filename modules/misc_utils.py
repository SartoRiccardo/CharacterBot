import os

def get_dict_keys(dict):
    """Return a list containing dict's keys"""
    ret = list(dict.keys())
    return ret


def get_CharacterBot_path():
    """Return CharacterBot's path"""
    ret = os.path.dirname(os.path.abspath(__file__))
    ret = str.join('/', ret.split('/')[:-1])
    return ret

def in_range(i, list):
    """Return if i is a valid index in list"""
    return i in range(len(list))

def get_lines(path):
    """Return path's line count"""
    with open(path, 'r') as f:
        ret = len(f.read().strip().split('\n'))

    return ret