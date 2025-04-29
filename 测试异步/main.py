import asyncio
import time

def sync_fun1():
    print("sync_fun1")
    time.sleep(1)
    a=1
    b=2
    c=3
    a=a+b
    b=b+c
    c=a+b
    print(a)
    print(b)
    print(c)
    print("sync_fun1 end")
    return 1

def sync_fun2():
    print("sync_fun2")
    time.sleep(1)
    print("sync_fun2 end")
    return 2


async def main():
    a=sync_fun1()
    print(a)
    b=sync_fun2()
    print(b)


if __name__ == "__main__":
    asyncio.run(main())