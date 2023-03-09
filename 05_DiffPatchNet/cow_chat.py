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

    async def login(self, name):
        if name == self._name or not self._name is None:
            await self._q.put("You can't relog in, please quit before")
        if name in free_names:
            free_names.remove(name)
            used_names.add(name)
            self._name = name
            await self._q.put(f"Welcome to Cow Chat, {self._name}!")
            print(f"User#{self._id} (logged in as) {self._name}")
        else:
            await self._q.put("Name is reserved, choose another")
        return not self._name is None

    def is_logged_in(self):
        return not self._name is None

    async def who(self):
        await self._q.put(f"{repr(sorted(list(used_names)))}")

    async def cows(self):
        await self._q.put(f"{repr(sorted(list(free_names)))}")

    async def quit(self):
        used_names.remove(self._name)
        free_names.add(self._name)
        self._name = None
        print(f"User#{self._id} (quit)")

    async def share(self, text):
        if not self.is_logged_in():
            await self._q.put("You can't chat befor logging in")
            return
        for user in clients.values():
            if user.id() != self._id and user.is_logged_in():
                await user._q.put(f"{self._name} (to all): {text}")
        return True

    async def say(self, to, text):
        if not self.is_logged_in():
            await self._q.put("You can't chat befor logging in")
        for user in clients.values():
            if user.name() == to and user.is_logged_in():
                await user._q.put(f"{self._name}: {text}")

    def receive_task(self):
        return asyncio.create_task(self._q.get())


async def chat(reader, writer):
    ip, port = writer.get_extra_info('peername')
    me = CowUser(ip, port)
    clients[me.id()] = me

    send = asyncio.create_task(reader.readline())
    receive = me.receive_task()
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
                        receive.cancel()
                        send.cancel()
                        del clients[me.id()]
                        writer.close()
                        await writer.wait_closed()
                        return
                    case ['login', name]:
                        await me.login(name)
                    case ['yield', text]:
                        await me.share(text)
                    case ['say', to, text]:
                        await me.say(to, text)
            elif task is receive:
                receive = me.receive_task()
                writer.write(f"{task.result()}\n".encode())
                await writer.drain()

    await me.quit()
    receive.cancel()
    send.cancel()
    del clients[me.id()]
    writer.close()
    await writer.wait_closed()


async def main():
    server = await asyncio.start_server(chat, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

asyncio.run(main())
