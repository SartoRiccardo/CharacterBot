import os

def get_dict_keys(dict):
    ret = list(dict.keys())
    return ret


def get_CharacterBot_path():
    ret = os.path.dirname(os.path.abspath(__file__))
    ret = str.join('/', ret.split('/')[:-1])
    return ret

def in_range(i, list):
    return i in range(len(list))