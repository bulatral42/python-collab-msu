import asyncio
import cowsay as cs
import shlex
from io import StringIO


clients = {}
free_names = set(cs.list_cows())
used_names = set()


class CowUser:
    self_id = None
    _ip = None
    _port = None
    _name = None
    _q = None
    # _notif_cow = cs.read_dot_cow(StringIO("""
    # $the_cow = <<EOC;
    #   $thoughts
    #       $thoughts
    #         P^P
    #        (+ +)
    #       ( >*< )
    #         [Y]
    #     ( ------- )
    #    ( ......... )
    #     ( _______ )
    #         L  L
    # EOC
    # """))


    def __init__(self, ip, port, name = None):
        self._id = f"{ip}:{port}"
        self._ip = ip
        self._port = port
        self._name = name
        self._q = asyncio.Queue()
        print(f"User#{self._id} (connected)")

    async def report(self, message, user=True):
        #await self._q.put(cs.cowsay(message, cowfile=self._notif_cow))
        if user:
            await self._q.put(message)
        else:
            await self._q.put('CMD ' + message)

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
            await self.report("You can't relog in, please quit before")
        elif name in free_names:
            free_names.remove(name)
            used_names.add(name)
            self._name = name
            await self.report(f"Welcome to Cow Chat, {self._name}!")
            print(f"User#{self._id} (logged in as) {self._name}")
        elif name in used_names:
            await self.report("Name is reserved, choose another")
        else:
            await self.report("Name is not cowish, choose true cowish name! You may use cows command")
        return not self._name is None

    def is_logged_in(self):
        return not self._name is None

    async def who(self, user=True):
        await self.report(', '.join(name for name in sorted(list(used_names))), user=user)

    async def cows(self, user=True):
        await self.report(', '.join(name for name in sorted(list(free_names))), user=user)

    async def quit(self):
        if self.is_logged_in():
            used_names.remove(self._name)
            free_names.add(self._name)
            self._name = None
        print(f"User#{self._id} (quit)")

    def cow_message(self, message):
        return cs.cowsay(message, cow=self._name)

    async def send_to_user(self, user, message):
        message = message.replace('\n', '\t')
        await user._q.put(message)

    async def share(self, text):
        if not self.is_logged_in():
            await self.report("You can't chat befor logging in")
            return
        for user in clients.values():
            if user.is_logged_in():
                await self.send_to_user(user, self.cow_message(f"{self._name} (to all): {text}"))
        return True

    async def say(self, to, text):
        if not self.is_logged_in():
            await self.report("You can't chat befor logging in")
        for user in clients.values():
            if user.name() == to and user.is_logged_in():
                await self.send_to_user(user, self.cow_message(f"{self._name}: {text}"))
                return
        await self.report("No cow with such name")

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
                got = task.result().decode()
                if len(got.strip()):
                    print(f'User#{me.id()}: {got.strip()}')
                parsed = shlex.split(task.result().decode())

                if len(parsed) > 0 and parsed[0] == 'CMD':
                    parsed = parsed[1:]
                    from_user = False
                else:
                    from_user = True

                match parsed:
                    case ['who']:
                        await me.who(from_user)
                    case ['cows']:
                        await me.cows(from_user)
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
                    case ['login']:
                        await me.report('Specify name to login')
                    case ['yield', text]:
                        await me.share(text)
                    case ['yield']:
                        await me.report('No message to yield')
                    case ['say', to, text]:
                        await me.say(to, text)
                    case ['say', to]:
                        await me.report('No message to say or cow name is missing')
                    case [*_]:
                        await me.report(f'Unknow command: {task.result().decode()}')
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
