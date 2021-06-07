#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import threading


class Server:
    server: socket.socket
    client_addr: list

    def __init__(self, host: tuple):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind(host)
        self.client_addr = []

    def run(self):
        while True:
            try:
                msg, addr = self.server.recvfrom(1024)
                print(msg.decode('utf8'))
                if addr not in self.client_addr:
                    self.client_addr.append(addr)
                threading.Thread(target=self.send, args=(msg,)).start()
            except ConnectionResetError as e:
                print('连接出错')
                continue

    def send(self, msg):
        for addr in self.client_addr:
            # print(addr)
            self.server.sendto(msg, addr)


if __name__ == '__main__':
    s = Server(('127.0.0.1', 8080))
    s.run()
