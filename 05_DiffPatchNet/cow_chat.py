import asyncio
import cowsay as cs


clients = {}

class CowUser:
    self_id = None
    _ip = None
    _port = None
    _name = None
    _q = None

    def __init__(self, ip, port, name = None):
        self._id = f"{ip}:{port}"
        self._ip = ip
        self._port = port
        self._name = name
        self._q = asyncio.Queue()

    def id(self):
        return self._id

    def ip(self):
        return self._ip

    def port(self):
        return self._port

    def name(self):
        return self._name

    def login(self, name):
        # if name in cs.list_cows():
        #     self._name = name
        self._name = name
        return not self._name is None

    def is_logged_in(self):
        return not self._name is None


async def chat(reader, writer):
    ip, port = writer.get_extra_info('peername')
    me = CowUser(ip, port)
    print(f"User#{me.id()} (connected)")
    clients[me.id()] = me
    me.login(f"u%{me.id()}")
    print(f"User#{me.id()} (logged in as) {me.name()}")

    send = asyncio.create_task(reader.readline())
    receive = asyncio.create_task(me._q.get())
    while not reader.at_eof():
        done, pending = await asyncio.wait([send, receive], return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            if task is send:
                send = asyncio.create_task(reader.readline())
                for user in clients.values():
                    if user is not me:
                        await user._q.put(f"{me.name()} {task.result().decode().strip()}")
            elif task is receive:
                receive = asyncio.create_task(me._q.get())
                writer.write(f"{task.result()}\n".encode())
                await writer.drain()
    send.cancel()
    receive.cancel()
    print(f"User#{me.id()} (quit)")
    del clients[me.id()]
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(chat, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

asyncio.run(main())
