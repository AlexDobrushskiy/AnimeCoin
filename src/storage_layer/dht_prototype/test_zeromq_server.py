import asyncio
import zmq
import zmq.asyncio
import random

from datetime import datetime as dt

# TODO: use uvloop it is super fast!


async def zmq_server(sock):
    async def async_process(ident, msg):
        waittime = random.randint(0, 2)
        print("MESSAGE RECEIVED: %s, batch processing will take %s", msg, waittime)
        tmp = msg.upper() + bytes(" waittime: " + str(waittime), "utf-8")
        reply = await asyncio.sleep(waittime, tmp)
        await sock.send_multipart([ident, reply])

    while True:
        ident, msg = await sock.recv_multipart()  # waits for msg to be ready
        asyncio.ensure_future(async_process(ident, msg))


async def heartbeat():
    while True:
        print("HB", dt.now())
        await asyncio.sleep(1)

if __name__ == "__main__":
    ctx = zmq.asyncio.Context()
    sock = ctx.socket(zmq.ROUTER)
    sock.bind("tcp://127.0.0.1:12345")

    loop = asyncio.get_event_loop()
    loop.create_task(zmq_server(sock))
    loop.create_task(heartbeat())
    loop.run_forever()
