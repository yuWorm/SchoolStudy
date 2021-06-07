#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import json
import threading
from tkinter import *
from tkinter import messagebox


class MsgPage(Frame):
    root: Tk
    msgView: Text
    msg: StringVar
    client: socket.socket
    ip: str
    port: int
    host: tuple
    name: str
    isRun = False

    def __init__(self, p, **kw):
        Frame.__init__(self, p, **kw)
        self.root = p
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.makeWeight()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.msgView.insert('end', '本聊天室为匿名聊天室，不会保存您的任何聊天内容与ip地址。使用方法：在下面聊天输入框输入信息，然后回车或者点击发送按钮即可发送。\n\n\n')

    def makeWeight(self):
        self.msgView = Text(self, height=36)
        scroll = Scrollbar(self)
        scroll.pack(side=RIGHT, fill=Y)
        self.msgView.pack()
        scroll.config(command=self.msgView.yview)
        self.msgView.config(yscrollcommand=scroll.set)

        frame = Frame(self)
        self.msg = StringVar()
        msg = Entry(frame, textvariable=self.msg, width=64)
        msg.pack(side=LEFT)
        msg.bind("<Return>", self.sends)
        Button(frame, text='发送', command=self.sends).pack(side=RIGHT)
        frame.pack()

    def packs(self):
        self.pack()
        self.root.geometry('500x500')
        self.isRun = True
        self.sendMsg('我来到了聊天室')
        threading.Thread(target=self.recvMsg).start()

    def setHost(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        if ip.strip() == '':
            self.ip = '127.0.0.1'
        if port == 0:
            self.port = 8080
        self.host = (self.ip, self.port)

    def setName(self, name: str):
        self.name = name

    def sends(self, ev=None):
        if self.msg.get().strip() != '':
            self.sendMsg(self.msg.get())
            self.msg.set('')
        else:
            messagebox.showerror('错误', '消息不可为空')

    def sendMsg(self, msg: str):
        msg = json.dumps({'name': self.name, 'msg': msg})
        self.client.sendto(msg.encode('utf8'), self.host)

    def recvMsg(self):
        while True:
            try:
                if not self.isRun:
                    break
                re_msg, addr = self.client.recvfrom(1024)
                msg_d = json.loads(re_msg.decode('utf8'))
                msg = '{name}：{msg}'.format(name=msg_d['name'], msg=msg_d['msg'])
                self.msgView.insert('end', msg + '\n')
            except (ConnectionResetError, ConnectionError, ConnectionAbortedError) as e:
                self.sendMsg('尝试重连')
                threading.Thread(target=self.recvMsg).start()
                break

    def close(self):
        self.root.destroy()
        self.sendMsg('退出了聊天')
        # 终止线程，直接异常退出
        self.client.close()


class IntoPage(Frame):
    root: Tk
    ip: StringVar
    port: IntVar
    name: StringVar
    msg_page: MsgPage

    def __init__(self, p, msg_page, **kw):
        Frame.__init__(self, p, kw)
        self.root = p
        self.root.geometry('300x100')
        self.msg_page = msg_page
        self.makeWeight()

    def makeWeight(self):
        self.ip = StringVar()
        self.port = IntVar()
        self.name = StringVar()

        Label(self, text='聊天室ip').grid(row=0, column=0)
        Label(self, text='聊天室端口').grid(row=1, column=0)
        Label(self, text='昵称').grid(row=2, column=0)

        Entry(self, textvariable=self.ip).grid(row=0, column=1)
        Entry(self, textvariable=self.port).grid(row=1, column=1)
        Entry(self, textvariable=self.name).grid(row=2, column=1)
        Button(self, text='进入', command=self.into).grid(row=3, column=1)

    def into(self):
        if self.ip.get().strip() == '':
            messagebox.showerror('错误', 'ip不可为空！')
            return
        elif self.port.get() == 0:
            messagebox.showerror('错误', '端口不可为空！')
            return
        elif self.name.get().strip() == '':
            messagebox.showerror('错误', '昵称不可为空！')
            return
        self.destroy()
        self.msg_page.setName(self.name.get())
        self.msg_page.setHost(self.ip.get(), self.port.get())
        self.msg_page.packs()


def main():
    root = Tk()
    root.title('匿名聊天室')
    screen_width = root.winfo_screenwidth()  # 获得屏幕宽度
    screen_height = root.winfo_screenheight()
    root.geometry('+%d+%d' % ((screen_width - root.winfo_width()) / 2.5, (screen_height - root.winfo_height()) / 4))
    msg = MsgPage(root)
    into = IntoPage(root, msg)
    into.pack()
    root.mainloop()


if __name__ == '__main__':
    main()
