import socket
import time
import os
from config import client_config


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((client_config['server_ip'], client_config['server_host']))
        except:
            print("无法连接")

        while True:
            message = input("$")
            message = message.strip().split(' ')[0:2]

            if message[0] == 'cd':
                message = ' '.join(message[0:2])
                s.send(message.encode('utf-8'))

            if message[0] == 'ls':
                message = str(message[0])
                s.send(message.encode('utf-8'))
                dir = s.recv(1024).decode('utf-8')
                print(dir)

            if message[0] == 'puts':
                filesize = os.path.getsize(message[1])
                message.append(str(filesize))
                me = ' '.join(message[0:3])
                s.send(me.encode('utf-8'))

                if filesize%1024 == 0:
                    sendnum = filesize//1024
                else:
                    sendnum = (filesize//1024) + 1

                with open(message[1], 'rb') as f:
                    time.sleep(1)
                    for i in range(sendnum):
                        piece = f.read(1024)
                        if len(piece):
                            s.send(piece)
                            print('%.2f%%' % (i / sendnum))
                    else:
                        print('puts end')

            if message[0] == 'gets':
                me = ' '.join(message[0:2])
                s.send(me.encode('utf-8'))
                filesize = int(s.recv(1024).decode('utf-8'))
                print(filesize)
                if filesize % 1024 == 0:
                    sendnum = filesize // 1024
                else:
                    sendnum = (filesize // 1024) + 1

                with open(message[1], 'wb') as f:
                    time.sleep(1)
                    for i in range(sendnum):
                        piece = s.recv(1024)
                        if len(piece):
                            f.write(piece)
                            print('%.2f%%' % (i / sendnum))
                    else:
                        print('gets end')

            if message[0] == 'remove':
                message = ' '.join(message[0:2])
                s.send(message.encode('utf-8'))

            if message[0] == 'pwd':
                message = str(message[0])
                s.send(message.encode('utf-8'))
                pwd = s.recv(1024).decode('utf-8')
                print(pwd)

            if message[0] == 'q':
                break


if __name__ == '__main__':
    main()