# coding=utf-8
"""
第二版本的接收上位机发送的数据
以队列的存储形式进行接收，一个线程接收，压入队列尾。另一线程，从队列头取出数据，解析每一帧。

"""
import logging
import socket
import threading
import time
from frame import Frame


logging.basicConfig(format='%(asctime)s %(message)s', filename='listen_queue.log', level=logging.INFO)


# host必须为''
host = ''
port = 60000

# 服务器监听的连接队列的最大数量
backlog = 5

threads = []

# 新建数据帧类
f = Frame()

# 接收时间间隔 秒
delay = 60 * 5

# 接收的最大数据量
bufSize = 100


def s_listen():
    """ 监听tcp请求并接收 """
    # Create a TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Enable reuse address/port
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind the socket to the port
    server_address = (host, port)

    logging.info("Starting up listen server on %s port %s" % server_address)
    sock.bind(server_address)
    # Listen to clients, backlog argument specifies the max no. of queued connections
    sock.listen(backlog)

    # Create new threads
    thread1 = threading.Thread(target=sock_acpt, args=(sock,))
    thread2 = threading.Thread(target=get_data, args=())

    # Start new Threads
    thread1.start()
    thread2.start()

    # Add threads to thread list
    threads.append(thread1)
    threads.append(thread2)

    # Wait for all threads to complete
    for t in threads:
        t.join()


queue = []

queue_lock = threading.Lock()


def sock_acpt(sock):
    """ socket接收tcp信息，存入队列尾部 """
    global queue
    while True:
        # Get lock to synchronize threads
        queue_lock.acquire()

        try:
            client, address = sock.accept()
            if len(queue) < 20:
                queue.append(client.recv(bufSize))
        except:
            logging.error("queue.append(client.recv(bufSize)) Error")

        # Free lock to release next thread
        queue_lock.release()
        # end connection
        client.close()


def get_data():
    global queue
    # 每时间间隔内需要接收的不同节点数
    count = 0
    # node_map用于检验每时间间隔内是否有接收到同一节点（node_id）的信息
    node_num = 11
    node_map = {}
    for i in range(1, node_num + 1):
        node_map[i] = 0
    while True:
        data = ""
        queue_lock.acquire()
        if len(queue) != 0:
            data = queue.pop()
        queue_lock.release()
        if data:
            try:
                if not f.get_frame(data[1:]):
                    continue
            except ValueError:
                logging.error("Data ValueError")
                continue

            if node_map[f.data_class.node_id] == 0:
                node_map[f.data_class.node_id] = 1
                count += 1
                f.save_database()
                logging.info("node_id: %s save time: %s" % (f.data_class.node_id, f.data_class.time))

            if count == 10:
                count = 0
                for i in range(1, node_num + 1):
                    node_map[i] = 0
                queue_lock.acquire()
                queue = []
                logging.info("sleep 5 min")
                time.sleep(delay)
                queue_lock.release()


if __name__ == '__main__':
    s_listen()


