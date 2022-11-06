user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
accept='text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
domain=''
root_url=f'https://numpy.org/doc/stable/reference/'
from urllib.parse import urljoin,urlparse
from bs4 import BeautifulSoup
import aiohttp
from myasync import *
from mypath import *
from typing import Iterable
import re
root_urlobj=urlparse(root_url)

@ensure_future
async def get(url:str,index:bool)->tuple[str,bytes,bool]|None:
    try:
        stimeout = aiohttp.ClientTimeout(total=None,sock_connect=0.8,sock_read=0.8)
        async with aiohttp.ClientSession(timeout=stimeout) as session:
            async with session.get(url,headers={
                'user-agent':user_agent,
                'accept':accept
            }) as res:
                return url,await res.read(),index
    except:
        return None

def removeback(s:str,target:str):
    t=s.find(target)
    if t==-1:return s
    return s[:t]

def get_abspath(url:str)->str:
    urlobj=urlparse(url)
    abspath=pathjoin('out',urlobj.scheme,urlobj.netloc,urlobj.path)
    if abspath[-1]=='/':
        abspath+='index.html'    
    return abspath

def get_relpath(rellink:str)->str:
    return pathrelate(removeback(removeback(rellink.replace('://','/'),'#'),'?'))

def save(url:str,data:str|bytes):
    abspath=get_abspath(url)
    pathcreate('/'.join(abspath.split('/')[:-1]))
    if isinstance(data,str):
        data=data.encode(encoding='utf-8')
    with open(abspath,'wb') as f:
        f.write(data)

def html_parse(url:str,data:bytes)->list:
    try:
        root = BeautifulSoup(data.decode(encoding='utf-8'), "html.parser")
    except:return []
    tasks=[]
    for tt in ['link','script','img','a']:
        tags:Iterable[BeautifulSoup]=root.find_all(tt)
        for tag in tags:
            for attr in ['href','src']:
                if tag.has_attr(attr):
                    link=tag[attr]
                    if isinstance(link,list):
                        link=link[0]
                    relpath=get_relpath(link)
                    abspath=get_abspath(urljoin(url,link))
                    tag[attr]=relpath
                    if not os.path.exists(abspath):
                        if re.compile(r'^(../)*([a-zA-z0-9\.\-\_\-]+/)*[a-zA-z0-9\.\-\_\-]+(/|.html?)')\
                            .fullmatch(relpath) is None:
                            tasks.append(get(urljoin(url,link),False))
                        else:
                            tasks.append(get(urljoin(url,link),True))
    save(url,root.prettify())
    return tasks

tasks=[get(root_url,True)]
data:tuple[str, bytes, bool]=run_async(tasks)[0]
tasks=html_parse(*data[:2])
while len(tasks)>0:
    print(len(tasks))
    ress:list[tuple[str,bytes,bool]]=run_async(tasks)
    tasks=[]
    for pack in ress:
        if pack is None:
            continue
        url,d,idx=pack
        if idx:
            tasks+=html_parse(url,d)
        else:
            save(url,d)