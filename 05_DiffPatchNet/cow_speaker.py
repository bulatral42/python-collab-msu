import asyncio
import sys

async def connect_stdin_stdout():
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    w_transport, w_protocol = await loop.connect_write_pipe(asyncio.streams.FlowControlMixin, sys.stdout)
    writer = asyncio.StreamWriter(w_transport, w_protocol, reader, loop)
    return reader, writer


async def cow_speaker(ip, port):
    s_reader, s_writer = await asyncio.open_connection(ip, port)
    u_reader, u_writer = await connect_stdin_stdout()

    msg_q = asyncio.Queue()

    read_cmd = asyncio.create_task(u_reader.readline())
    read_ans = asyncio.create_task(s_reader.readline())

    while not s_reader.at_eof() and not u_reader.at_eof():
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
    read_ans.cancel()
    s_writer.close()
    await s_writer.wait_closed()
    u_writer.close()


if __name__ == '__main__':
    asyncio.run(cow_speaker('0.0.0.0', 1337))
