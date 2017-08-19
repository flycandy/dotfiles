"""
Usage:
    play_warp.py [options]

Options:
    --debug
    --host=<h>     Host [default: 0.0.0.0]
    --port=<p>     Port [default: 1081]
    --verbose=<v>  Verbose [default: 0]
"""
from socket import TCP_NODELAY
from time import time
import asyncio
import logging
import random
import functools
import re

import aiosocks
import asyncio_redis
from aiosocks.helpers import Socks5Addr
from docopt import docopt as docoptinit
# import qbtrade as qb
import concurrent.futures
import json
import requests

FIRST_COMPLETED = concurrent.futures.FIRST_COMPLETED
# socks5_addr = Socks5Addr('ubuntu.urwork.qbtrade.org', '1080')
socks5_addr = Socks5Addr('localhost', '1080')
socks5_auth = None

REGEX_HOST = re.compile(r'(.+?):([0-9]{1,5})')
REGEX_CONTENT_LENGTH = re.compile(r'\r\nContent-Length: ([0-9]+)\r\n', re.IGNORECASE)
REGEX_CONNECTION = re.compile(r'\r\nConnection: (.+)\r\n', re.IGNORECASE)

clients = {}
verbose = 0


def is_aboard(host):
    url = 'http://ip.cn/index.php?ip={}'
    html = requests.get(url.format(host)).text.lower()
    if 'china' in html:
        return False
    else:
        return True


class Config:
    timeout = 30


class ProxySelector:
    def __init__(self):
        self.redis = None
        self.proxy_host = {}
        self.inwall = None
        self.outwall = None
        asyncio.ensure_future(self.init())

    async def init(self):
        self.redis = await asyncio_redis.Pool.create('service.qbtrade.org', poolsize=5)
        self.inwall = json.loads(await self.redis.get('proxy:human-inwall'))
        self.outwall = json.loads(await self.redis.get('proxy:human-outwall'))

    def get_use_proxy_or_not(self, url):
        for item in self.inwall:
            if url.endswith(item):
                return False

        for i in self.outwall:
            if url.endswith(i):
                logging.info(f'go through proxy "{url}"')
                return True
        res = self.smart_proxy(url)
        if res:
            logging.info(f'go through proxy "{url}"')
        return res

    def smart_proxy(self, url):
        if url in self.proxy_host.items():
            if is_aboard(url):
                return True
            else:
                return False
        else:
            return False

    def set_result(self, host, timeout, use_proxy):
        self.proxy_host[host] = {'proxy': use_proxy, 'timeout': timeout}


def accept_client(client_reader, client_writer, *, loop=None):
    ident = hex(id(client_reader))[-6:]
    task = asyncio.ensure_future(process_warp(client_reader, client_writer, loop=loop), loop=loop)
    clients[task] = (client_reader, client_writer)
    started_time = time()

    def client_done(task):
        del clients[task]
        client_writer.close()
        logging.debug('[%s] Connection closed (took %.5f seconds)' % (ident, time() - started_time))

    logging.info('[%s] Connection started' % ident)
    task.add_done_callback(client_done)


async def process_warp(client_reader, client_writer, *, loop=None):
    ident = str(hex(id(client_reader)))[-6:]
    header = ''
    payload = b''
    try:
        RECV_MAX_RETRY = 3
        recvRetry = 0
        while True:
            line = await client_reader.readline()
            if not line:
                if len(header) == 0 and recvRetry < RECV_MAX_RETRY:
                    # handle the case when the client make connection but sending data is delayed for some reasons
                    recvRetry += 1
                    await asyncio.sleep(0.2, loop=loop)
                    continue
                else:
                    break
            if line == b'\r\n':
                break
            if line != b'':
                header += line.decode()

        m = REGEX_CONTENT_LENGTH.search(header)
        if m:
            cl = int(m.group(1))
            while (len(payload) < cl):
                payload += await client_reader.read(1024)
    except Exception as e:
        logging.warning(e)

    if len(header) == 0:
        logging.debug('[%s] !!! Task reject (empty request)' % ident)
        return
    req = header.split('\r\n')[:-1]
    if len(req) < 4:
        logging.debug('[%s] !!! Task reject (invalid request)' % ident)
        return
    head = req[0].split(' ')
    if head[0] == 'CONNECT':  # https proxy
        await wrap_https(client_reader, client_writer, head, ident, loop)
    else:
        # http proxy
        logging.info(f'proxy http website {head}')
        # import pprint
        # pprint.pprint(req)
        phost = False
        sreq = []
        sreqHeaderEndIndex = 0
        for line in req[1:]:
            headerNameAndValue = line.split(': ', 1)
            if len(headerNameAndValue) == 2:
                headerName, headerValue = headerNameAndValue
            else:
                headerName, headerValue = headerNameAndValue[0], None

            if headerName.lower() == "host":
                phost = headerValue
            elif headerName.lower() == "connection":
                if headerValue.lower() in ('keep-alive', 'persist'):
                    # current version of this program does not support the HTTP keep-alive feature
                    sreq.append("Connection: close")
                else:
                    sreq.append(line)
            elif headerName.lower() != 'proxy-connection':
                sreq.append(line)
                if len(line) == 0 and sreqHeaderEndIndex == 0:
                    sreqHeaderEndIndex = len(sreq) - 1
        if sreqHeaderEndIndex == 0:
            sreqHeaderEndIndex = len(sreq)

        m = REGEX_CONNECTION.search(header)
        if not m:
            sreq.insert(sreqHeaderEndIndex, "Connection: close")

        if not phost:
            phost = '127.0.0.1'
        path = head[1][len(phost) + 7:]

        logging.debug('%sWRAPPING <%s %s>' % ('[%s] ' % ident if verbose >= 1 else '', head[0], head[1]))

        new_head = ' '.join([head[0], path, head[2]])

        m = REGEX_HOST.search(phost)
        if m:
            host = m.group(1)
            port = int(m.group(2))
        else:
            host = phost
            port = 80
        logging.info(f"host {host} port {port}")
        try:
            if proxy_selector.get_use_proxy_or_not(host):
                req_reader, req_writer = await aiosocks.open_connection(proxy=socks5_addr,
                                                                        proxy_auth=socks5_auth,
                                                                        dst=(host, port), remote_resolve=True,
                                                                        loop=loop)
            else:
                try:
                    req_reader, req_writer = await asyncio.wait_for(
                        asyncio.open_connection(host, port, flags=TCP_NODELAY,
                                                loop=loop), timeout=Config.timeout)
                except:
                    logging.exception(f'timeout for {host} add it to proxy')
                    proxy_selector.set_result(host, timeout=True, use_proxy=False)
                    # if host not in PROXY_HOST:
                    #     PROXY_HOST.append(host)
                    #     asyncio.ensure_future(redis.set('proxy:host', json.dumps(PROXY_HOST)))
                    raise
            logging.debug(f"host {host} port {port} connect")
            # print(new_head)
            req_writer.write(('%s\r\n' % new_head).encode())
            await req_writer.drain()
            await asyncio.sleep(0.01, loop=loop)

            # def generate_dummyheaders():
                # def generate_rndstrs(strings, length):
                    # return ''.join(random.choice(strings) for _ in range(length))
# 
                # import string
                # return ['X-%s: %s\r\n' % (generate_rndstrs(string.ascii_uppercase, 16),
                                          # generate_rndstrs(string.ascii_letters + string.digits, 128)) for _ in
                        # range(32)]

            # req_writer.writelines(list(map(lambda x: x.encode(), generate_dummyheaders())))
            # await req_writer.drain()

            #req_writer.write(b'Host: ')
            #await req_writer.drain()

            #def feed_phost(phost):
                #i = 1
                #while phost:
                    #yield random.randrange(2, 4), phost[:i]
                    #phost = phost[i:]
                    #i = random.randrange(2, 5)
#
            #for delay, c in feed_phost(phost):
                #await asyncio.sleep(0.01, loop=loop)
                #req_writer.write(c.encode())
                #await req_writer.drain()
            #req_writer.write(b'\r\n')
            req_writer.writelines(list(map(lambda x: (x + '\r\n').encode(), sreq)))
            req_writer.write(b'\r\n')
            if payload != b'':
                req_writer.write(payload)
                req_writer.write(b'\r\n')
            await req_writer.drain()

            try:
                while True:
                    buf = await req_reader.read(2048)
                    if len(buf) == 0:
                        break
                    client_writer.write(buf)
            except Exception as e:
                logging.warning(e)

            logging.debug(f"host {host} port {port} finish")
        except Exception as e:
            logging.warning(e)


async def wrap_https(client_reader, client_writer, head, ident, loop):
    try:
        logging.debug('proxy https %sBYPASSING <%s %s> (SSL connection)' %
                      ('[%s] ' % ident if verbose >= 1 else '', head[0], head[1]))
        m = REGEX_HOST.search(head[1])
        host = m.group(1)
        port = int(m.group(2))
        logging.debug(f'http proxy to {host}, {port}')
        try:
            if proxy_selector.get_use_proxy_or_not(host):
                req_reader, req_writer = await aiosocks.open_connection(proxy=socks5_addr,
                                                                        proxy_auth=socks5_auth,
                                                                        dst=(host, port), remote_resolve=True,
                                                                        loop=loop)
            else:
                req_reader, req_writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port, ssl=False, loop=loop), timeout=Config.timeout)
        except:
            logging.warning(f'timeout for {host} add it to proxy')
            proxy_selector.set_result(host, timeout=True, use_proxy=False)
            # if host not in PROXY_HOST:
            #     PROXY_HOST.append(host)
            #     await redis.set('proxy:host', json.dumps(PROXY_HOST))
            # req_reader, req_writer = await aiosocks.open_connection(proxy=socks5_addr, proxy_auth=socks5_auth,
            #                                                         dst=(host, port), remote_resolve=True,
            #                                                         loop=loop)
            raise
        client_writer.write(b'HTTP/1.1 200 Connection established\r\n\r\n')

        async def relay_stream(reader, writer):
            try:
                while True:
                    line = await reader.read(1024)
                    if len(line) == 0:
                        break
                    writer.write(line)
                    await asyncio.sleep(0)
            except Exception as e:
                logging.warning(e)

        tasks = [
            asyncio.ensure_future(relay_stream(client_reader, req_writer), loop=loop),
            asyncio.ensure_future(relay_stream(req_reader, client_writer), loop=loop),
        ]
        await asyncio.wait(tasks, loop=loop, return_when=FIRST_COMPLETED)
    except:
        logging.exception('unexpected failed')
    finally:
        return


async def start_warp_server(host, port, *, loop=None):
    try:
        accept = functools.partial(accept_client, loop=loop)
        server = await asyncio.start_server(accept, host=host, port=port, loop=loop)
    except OSError as ex:
        logging.error('!!! Failed to bind server at [%s:%d]: %s' % (host, port, ex.args[1]))
        raise
    else:
        logging.info('Server bound at [%s:%d].' % (host, port))
        return server


def main():
    """CLI frontend function.  It takes command line options e.g. host,
    port and provides `--help` message.
    """
    docopt = docoptinit(__doc__)
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] [%(levelname)s] [ %(filename)s:%(lineno)s - %(name)s ] %(message)s ')
    logging.info('basic config')
    # qb.set_logger(__file__, debug=docopt['--debug'])
    host = docopt['--host']
    port = int(docopt['--port'])
    if not (1 <= port <= 65535):
        raise Exception('port must be 1-65535')

    global verbose
    verbose = int(docopt['--verbose'])
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start_warp_server(host, port))
        loop.run_forever()
    except OSError:
        pass
    except KeyboardInterrupt:
        print('bye')
    finally:
        loop.close()


if __name__ == '__main__':
    proxy_selector = ProxySelector()
    main()
