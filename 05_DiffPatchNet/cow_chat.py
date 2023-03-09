import asyncio
import cowsay as cs
import shlex


clients = {}
free_names = set(cs.list_cows())
used_names = set()


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
        print(f"User#{self._id} (connected)")

    def id(self):
        return self._id

    def ip(self):
        return self._ip

    def port(self):
        return self._port

    def name(self):
        return self._name

    def login(self, name):
        if name in free_names:
            free_names.remove(name)
            used_names.add(name)
            self._name = name
            print(f"User#{self._id} (logged in as) {self._name}")
        return not self._name is None

    def is_logged_in(self):
        return not self._name is None

    async def who(self):
        await self._q.put(f"{repr(used_names)}")

    async def cows(self):
        await self._q.put(f"{repr(list(free_names))}")

    async def quit(self):
        self._name = None
        print(f"User#{self._id} (quit)")




async def chat(reader, writer):
    ip, port = writer.get_extra_info('peername')
    me = CowUser(ip, port)
    clients[me.id()] = me
    me.login(next(iter(free_names)))

    send = asyncio.create_task(reader.readline())
    receive = asyncio.create_task(me._q.get())
    while not reader.at_eof():
        done, pending = await asyncio.wait([send, receive], return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            if task is send:
                send = asyncio.create_task(reader.readline())

                parsed = shlex.split(task.result().decode())
                match parsed:
                    case ['who']:
                        await me.who()
                    case ['cows']:
                        await me.cows()
                    case ['quit']:
                        await me.quit()
                        send.cancel()
                        del clients[me.id()]
                        writer.close()
                        await writer.wait_closed()
                        break
            elif task is receive:
                receive = asyncio.create_task(me._q.get())

                writer.write(f"{task.result()}\n".encode())
                await writer.drain()


async def main():
    server = await asyncio.start_server(chat, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

asyncio.run(main())
