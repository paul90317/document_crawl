import os
import re

def pathrelate(path:str)->str:
    if len(path)==0:
        return ''
    flag=path[-1]=='/'
    sps=path.split('/')
    sps=[s for s in sps if s!='.' and s!='']
    ret=[]
    for s in sps:
        if s=='..':
            if len(ret)>0 and ret[-1]!='..':
                ret.pop(-1)
            else:
                ret.append('..')
        else:
            ret.append(s)
    ret='/'.join(ret)
    if flag:
        return ret+'/'
    return ret

def pathjoin(*paths)->str:
    return pathrelate('/'.join(paths))
    
def pathcreate(path:str)->None:
    curr=''
    path=pathrelate(path)
    sps=path.split('/')
    for pp in sps:
        if not os.path.exists(curr+pp):
            os.mkdir(curr+pp)
        curr+=pp+'/'
