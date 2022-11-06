import asyncio
def ensure_future(func):
    def wrapper(*argv):
        return asyncio.ensure_future(func(*argv))
    return wrapper

def run_async(tasks:list):
    loop=asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
    return [t.result() for t in tasks]