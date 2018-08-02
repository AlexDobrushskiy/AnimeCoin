import sys
import asyncio
import zmq
import zmq.asyncio


async def zmq_send(url, msg, identity):
    ctx = zmq.asyncio.Context()
    sock = ctx.socket(zmq.DEALER)
    sock.setsockopt(zmq.IDENTITY, bytes(str(identity), "utf-8"))
    sock.connect(url)
    await sock.send_multipart([msg])
    print("SENT", msg)
    msg = await sock.recv_multipart()  # waits for msg to be ready
    print("MESSAGE RECEIVED: %s", msg)

if __name__ == "__main__":
    msg = bytes(sys.argv[1], "utf-8")

    loop = asyncio.get_event_loop()
    f = [zmq_send("tcp://127.0.0.1:12345", msg + bytes(str(x), "utf-8"), x) for x in range(10)]
    loop.run_until_complete(asyncio.wait(f))
