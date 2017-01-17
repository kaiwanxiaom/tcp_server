# coding=utf-8
import database
import time
import re


class Frame(object):

    def __init__(self):
        self.ip = []
        self.port = []
        self.id = 0
        self.block = 0
        self.type = 0
        self.length = 0
        self.reserved = []
        self.data = []
        self.data_class = Environment()

    def get_frame(self, frame):
        """ 把字符串帧内的信息构造成类 """
        if not self.check_frame(frame):
            return False
        # 把字符串转换为字节数组
        frame_ary = re.compile(r'.{2}').findall(frame)
        self.ip = frame_ary[0:6]
        self.port = frame_ary[6:8]
        self.id = frame_ary[8]
        self.block = frame_ary[9]
        self.type = frame_ary[10]
        self.length = frame_ary[11]
        self.reserved = frame_ary[12:16]
        self.data = frame_ary[16:]
        self.data_class.get_data(self.data)
        # 经过测试，接收的帧会出现部分信息错误，比如id错误，以下是临时处理。合理的处理方式为：校验码校验 写到check_frame内
        if self.data_class.node_id > 11 or self.data_class.node_id < 1:
            return False

        return True

    def save_database(self):
        """ 把一帧的数据内容存储到数据库 """
        self.data_class.save()

    def check_frame(self, frame):
        """ 检验帧是否正确，学长不清楚帧校验方法，所以没写校验 """
        if len(frame) < 82:
            return False
        return True


class Environment(object):
    """ 每一帧内数据内容，即每一个环境节点的信息 """
    def __init__(self):
        self.time = ""
        self.node_type = 0
        self.node_id = 0
        self.temperature = 0
        self.humidity = 0
        self.light = 0
        self.CO2 = 0
        self.nodeIn = 0
        self.nodeOut = 0
        self.Cflag = 0
        self.In485 = 0

    def get_data(self, data):
        self.time = time.strftime("%Y-%m-%d %X", time.localtime(time.time()))
        self.node_type = int(data[1]+data[0], 16)
        self.node_id = int(data[3]+data[2], 16)
        self.temperature = int(data[5]+data[4], 16) / 10.0
        self.humidity = int(data[7]+data[6], 16) / 10.0
        self.light = int(data[11]+data[10]+data[9]+data[8], 16)
        self.CO2 = int(data[13]+data[12], 16)
        self.nodeIn = int(data[14], 16)
        self.nodeOut = int(data[15], 16)
        self.Cflag = int(data[16], 16)
        self.In485 = data[18]+data[17]+data[16]

    def save(self):
        sq_command = "insert into Environment(time, nodetype, nodeid, temperature, humidity, light, CO2, " \
                     "nodeIn, nodeOut, Cflag, In485) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        sq_data = [self.time, self.node_type, self.node_id, self.temperature, self.humidity, self.light, self.CO2,
                   self.nodeIn, self.nodeOut, self.Cflag, self.In485]
        database.save_data(sq_command, sq_data)

if __name__ == '__main__':
    tmp_f = ":731CDF21000075170101011400000000010002002701BF024303000099010F0001FFFF000182FF0061"
    ary = re.compile(r'.{2}').findall(tmp_f[1:])
    print "%d" % int(ary[0]+ary[1], 16)
    f = Frame()
    f.get_frame(tmp_f[1:])
    f.save_database()

    # for a in ary:
    #     print "%x" %a
    # print f.ip, f.port, f.length
    # print f.data_class.node_type, f.data_class.node_id, f.data_class.temperature
    # print time.strftime("%Y-%m-%d %X", time.localtime(time.time()))
