import socket
import select
import os, time
from concurrent.futures import ThreadPoolExecutor
from config import server_config


CONNECTIONS = {}


def read_event(sock):
    message = sock.recv(1024)
    message = message.decode('utf-8').split(' ')
    if message[0] == 'cd':
        os.chdir(message[1])

    if message[0] == 'ls':
        dir = os.listdir()
        dir = ' '.join(dir)
        sock.send(dir.encode('utf-8'))

    if message[0] == 'puts':
        filesize = int(message[2])
        print(filesize)
        if filesize % 1024 == 0:
            sendnum = filesize // 1024
        else:
            sendnum = (filesize // 1024) + 1

        with open(message[1], 'wb') as f:
            time.sleep(1)
            for i in range(sendnum):
                piece = sock.recv(1024)
                if len(piece):
                    f.write(piece)

    if message[0] == 'gets':
        filesize = os.path.getsize(message[1])
        sock.send(str(filesize).encode('utf-8'))
        if filesize % 1024 == 0:
            sendnum = filesize // 1024
        else:
            sendnum = (filesize // 1024) + 1
        with open(message[1], 'rb') as f:
            time.sleep(1)
            for i in range(sendnum):
                piece = f.read(1024)
                if len(piece):
                    sock.send(piece)

    if message[0] == 'remove':
        os.remove(message[1])

    if message[0] == 'pwd':
        pwd = os.getcwd()
        sock.send(pwd.encode('utf-8'))


def create_server_socket():
    """
    创建socket并返回
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((server_config['listen_ip'], server_config['listen_host']))
    s.listen(server_config['listen_number'])
    s.setblocking(False)
    return s


def handle_inotify_event(epoll, server, fd, event_type, thread_pool):
    """
    处理响应事件
    """
    # 处理新连接
    if fd == server.fileno():
        c, address = server.accept()
        c.setblocking(False)
        child_fd = c.fileno()
        epoll.register(child_fd, select.EPOLLIN)
        CONNECTIONS[child_fd] = c
    else:
        c = CONNECTIONS[fd]
        # 关闭事件
        if event_type & select.EPOLLHUP:
            print('close client')
            epoll.unregister(fd)
            CONNECTIONS[fd].close()
            del CONNECTIONS[fd]
        # 可读事件
        elif event_type & select.EPOLLIN:
            thread_pool.submit(read_event, c)
        # 可写事件
        elif event_type & select.EPOLLOUT:
            pass


def run_server():
    thread_pool = ThreadPoolExecutor(server_config['thread_pool_number'])
    serversocket = create_server_socket()
    epoll = select.epoll()
    epoll.register(serversocket.fileno(), select.EPOLLIN)
    try:
        while True:
            events = epoll.poll(server_config['timeout'])
            if not events:
                continue
            for fd, event_type in events:
                handle_inotify_event(epoll, serversocket, fd, event_type, thread_pool)
    finally:
        epoll.unregister(serversocket.fileno())
        epoll.close()
        serversocket.close()


if __name__ == '__main__':
    run_server()






