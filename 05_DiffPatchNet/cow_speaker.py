import asyncio
import cmd
import sys


class CowSpeakerCmd(cmd.Cmd):
    def do_who(self, args):
        pass

async def connect_stdin_stdout():
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    w_transport, w_protocol = await loop.connect_write_pipe(asyncio.streams.FlowControlMixin, sys.stdout)
    writer = asyncio.StreamWriter(w_transport, w_protocol, reader, loop)
    return reader, writer


async def cow_speaker(ip, port):
    cow_cmd = CowSpeakerCmd()

    s_reader, s_writer = await asyncio.open_connection(ip, port)
    u_reader, u_writer = await connect_stdin_stdout()

    msg_q = asyncio.Queue()

    read_cmd = asyncio.create_task(u_reader.readline())
    # send_cmd = None
    read_ans = asyncio.create_task(s_reader.read(4096))
    # send_ans = None

    while not s_reader.at_eof() and not u_reader.at_eof():
        # done, pending = await asyncio.wait([read_cmd, send_cmd, read_ans, send_ans], return_when=asyncio.FIRST_COMPLETED)
        done, pending = await asyncio.wait([read_cmd, read_ans], return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            if task is read_cmd:
                read_cmd = asyncio.create_task(u_reader.readline())
                s_writer.write(task.result())
                await s_writer.drain()
            elif task is read_ans:
                read_ans = asyncio.create_task(s_reader.readline())
                u_writer.write(task.result())
                await u_writer.drain()
    read_cmd.cancel()
    # send_cmd.cancel()
    read_ans.cancel()
    # send_ans.cancel()
    print("DONE")
    s_writer.close()
    await s_writer.wait_closed()
    u_writer.close()
    # await u_writer.wait_closed()


async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection('0.0.0.0', 1337)

    print(f'Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()
    print('Sent')
    data = await reader.read(100)
    print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()
    await writer.wait_closed()


if __name__ == '__main__':
    asyncio.run(cow_speaker('0.0.0.0', 1337))
    # asyncio.run(tcp_echo_client('login satanic'))
