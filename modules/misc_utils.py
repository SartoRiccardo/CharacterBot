import os
import aiohttp

project_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
debug = False

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


async def get_file_content(link):
    """Return the content of the file the link points to"""
    async with aiohttp.ClientSession() as cs:
        async with cs.get(link) as f:
            content = await f.read()
            print(content)


def dprint(*args):
    if debug:
        msg = ''
        for a in args:
            msg += f"{a} "
        print(msg)