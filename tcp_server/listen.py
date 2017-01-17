# coding=utf-8
import logging
import socket
import threading
import time
from frame import Frame


# host必须为''
host = ''
port = 60000

# 服务器监听的连接队列的最大数量
backlog = 5

threads = []


def s_listen():
    """ 监听tcp请求并接收 """
    # Create a TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Enable reuse address/port
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind the socket to the port
    server_address = (host, port)
    print "Starting up listen server on %s port %s" % server_address
    sock.bind(server_address)
    # Listen to clients, backlog argument specifies the max no. of queued connections
    sock.listen(backlog)

    # Create new threads
    thread1 = ListenThread(sock)
    thread2 = ListenThread(sock)

    # Start new Threads
    thread1.start()
    thread2.start()

    # Add threads to thread list
    threads.append(thread1)
    threads.append(thread2)

    # Wait for all threads to complete
    for t in threads:
        t.join()


class ListenThread (threading.Thread):
    sock_lock = threading.Lock()
    map_lock = threading.Lock()
    finish = False
    count = 0
    node_num = 11
    node_map = {}
    for i in range(1, node_num + 1):
        node_map[i] = 0

    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock
        self.data = ""
        # 新建数据帧类
        self.f = Frame()
        # 接收时间间隔 秒
        self.delay = 60 * 5
        # 接收的最大数据量
        self.bufSize = 100

    def run(self):
        while True:
            if ListenThread.finish:
                print "sleep 5 min"
                time.sleep(self.delay)
                ListenThread.finish = False

            # Get lock to synchronize threads
            ListenThread.sock_lock.acquire()
            self.get_sock_data()
            # Free lock to release next thread
            ListenThread.sock_lock.release()

            if self.data:
                if not self.f.get_frame(self.data[1:]):
                    continue
                ListenThread.map_lock.acquire()
                if ListenThread.finish:
                    continue
                if self.handle_data():
                    ListenThread.finish = True
                    ListenThread.map_lock.release()
                else:
                    ListenThread.map_lock.release()

    def get_sock_data(self):
        print "Waiting to receive message from client"
        client, address = self.sock.accept()
        self.data = client.recv(self.bufSize)
        # end connection
        client.close()

    def handle_data(self):
        if ListenThread.node_map[self.f.data_class.node_id] == 0:
            ListenThread.node_map[self.f.data_class.node_id] = 1
            ListenThread.count += 1
            self.f.save_database()
            print "node_id: %s save time: %s" % (self.f.data_class.node_id, self.f.data_class.time)

        if ListenThread.count == 10:
            ListenThread.count = 0
            for i in range(1, ListenThread.node_num + 1):
                ListenThread.node_map[i] = 0
            return True

if __name__ == '__main__':
    s_listen()
