import socketserver
import json
import socket
import threading

# 服务器直接保存用户密码的md5加密版，此处实验较简单，直接存储在字典好了

# 创建一个用户字典，存储所有用户信息
user_dict = {}

# 创建一个用户名映射ip的字典
user_name_list = []

# 群组字典
group_dict = {}

group_name_list = []

class MessageTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        # try:
        while True:
            self.data = self.request.recv(65536)
            print("{} send data".format(self.client_address))
            if not self.data:
                print("connection lost")
                break
            res = ServerFunction(self.request, self.data)
            # 这一句只是将数据传输回去并且大写，没有其他多余的处理
            # 这里的request是一个socket对象，可以提供其他操作
            if (res):
                self.request.sendall(bytes(json.dumps(res), encoding='utf-8'))
            # self.request.sendall(bytes(json.dumps(user_dict.keys()),encoding='utf-8'))
        # except Exception as e:
        print(self.client_address, "连接断开")
        # finally:
        print("断开用户连接")
        self.request.close()
        # 要寻找到该用户并将其socket删除？

    def setup(self):
        print("before handle,连接建立：", self.client_address)
        # 将用户加入到用户字典中,key是用户的IP地址，value是用户的socket对象
        # 用户登录的IP可能不变，但是port会变，因此不能以此作为key，其并不具有唯一性
        # user_dict[self.client_address] = {
        #     'socket':self.request
        # }
        # 同时返回所有用户列表
        # socket 中send 和 sendall的区别
        # send会返回发送的字节数，可有应用程序接着继续发送
        # sendall发送后返回None，若发送意外，会触发异常

    def finish(self):
        # finish 函数是在调用完handle后进行操作
        # global user_dict
        # super().finish()
        # 将用户删除
        # user_dict.pop(self.client_address)
        print("finish run  after handle")

class FileTCPHandler(socketserver.BaseRequestHandler):
    length = None
    recv = None
    curr_count = None
    data_buffer = None
    hasUserInfo = False
    def handle(self):
        # try:
        while True:
            self.data = self.request.recv(65536)
            print("{} send data".format(self.client_address))
            if not self.data:
                print("connection lost")
                break
            if self.hasUserInfo == False:
                try:
                    user_info = json.loads(self.data)
                    print('+'*20)
                    print('FileThread')
                    print(user_info)
                    # 写入数据
                    user_dict[user_info['account']]['file-socket'] = self.request
                    self.hasUserInfo = True
                    # 跳过
                except:
                    pass
            else: 
                if self.curr_count is None or self.recv is None or self.length is None:
                    # 获取info信息
                    info_length = int.from_bytes(self.data[:8],byteorder = "big",signed=False)
                    # info 信息
                    info_content = json.loads(self.data[8:8+info_length])
                    # 计算总共需要转发字节数
                    self.length = info_content['file-size'] + 8 + info_length
                    # 记录当前发送人
                    self.recv = info_content['to']
                    # 记录当前已经转发数
                    self.curr_count = len(self.data)
                    print("Message Percent: {} %".format(self.curr_count/self.length*100))
                    # 转发
                    print(user_dict)
                    user_dict[self.recv]['file-socket'].send(self.data)
                    self.data_buffer = self.data
                else:
                    self.curr_count += len(self.data)
                    self.data_buffer = self.data_buffer + self.data
                    # 转发
                    # user_dict[self.recv].send(self.data)
                    user_dict[self.recv]['file-socket'].send(self.data)
                    print("Message Percent: {} %".format(self.curr_count/self.length*100))
                    if self.curr_count == self.length:
                        # 文件接受完成
                        # 将数据转发给其他人，数据文件都不需要在本地进行存储
                        self.length = None
                        self.curr_count = None
                        self.recv = None

            # filename = '2621.wav'
            # filecontent = None
            # with open(filename, 'rb') as f:
            #     filecontent = f.read()
                
            # # json无法处理bytes类型文件
            # # 需要直接发送
            # info = json.dumps({
            #     'file-name': '2621.wav',
            #     'from': 'A',
            #     'to': 'B',
            #     'file-size': len(filecontent)
            # })

            # print(info)

            # b_info = bytes(info, encoding='utf-8')

            # # 应保证长度在一定范围内

            # # 采用json+文件内容的方式
            
            # self.request.send(len(b_info).to_bytes(8,"big",signed=False)+b_info+filecontent)
            # if (res):
            #     self.request.sendall(bytes(json.dumps(res), encoding='utf-8'))
            # self.request.sendall(bytes(json.dumps(user_dict.keys()),encoding='utf-8'))
        # except Exception as e:
        print(self.client_address, "连接断开")
        # finally:
        print("断开用户连接")
        self.request.close()
        # 要寻找到该用户并将其socket删除？

    def setup(self):
        print("File Thread")
        print("before handle,连接建立：", self.client_address)
        # 将用户加入到用户字典中,key是用户的IP地址，value是用户的socket对象
        # 用户登录的IP可能不变，但是port会变，因此不能以此作为key，其并不具有唯一性
        # user_dict[self.client_address] = {
        #     'socket':self.request
        # }
        # 同时返回所有用户列表
        # socket 中send 和 sendall的区别
        # send会返回发送的字节数，可有应用程序接着继续发送
        # sendall发送后返回None，若发送意外，会触发异常

    def finish(self):
        # finish 函数是在调用完handle后进行操作
        # global user_dict
        # super().finish()
        # 将用户删除
        # user_dict.pop(self.client_address)
        print("finish run  after handle")

def ServerFunction(req, args):
    res = {}
    # try:
    data = json.loads(args)
    print(data)
    request_type = data['type']
    if request_type == 'login':
        res['error'] = False
        user_dict[data['account']] = {
            'socket': req,
            'name': data['account'],
            'password': data['password']
        }
        user_name_list.append(data['account'])
        res['nowSession'] = data['account']
        res['type'] = 'listAppend'

        for userName in user_name_list:
            if (userName != data['account']):
                try:
                    res['attachedMessage'] = userName
                    user_dict[userName]['socket'].send(bytes(json.dumps(res), encoding='utf-8'))
                except:
                    print('ERROR: 用户 {} 不在线'.format(userName))
                
        res['type'] = 'login'
        res['group'] = group_name_list
        res['user'] = user_name_list
        return res
        # user = user_dict.get(key)
        # # 获取用户姓名，没获取到则是没有
        # name = user.get('name',None)
        # if name is None:
        #     # 1号错误，代表没有这个用户，没有注册
        #     res['error'] = True
        #     res['error-message'] = '尚未注册'
        #     res['error-title'] = '登录失败'
        # else:
        #     # 确实有这么一个用户，比较密码对不对
        #     if data['password'] == user['password']:
        #         # 登录成功
        #         res['error'] = False

        #     else:
        #         # 密码错误，2号错误
        #         res['error'] = True
        #         res['error-message'] = '密码错误'
        #         res['error-title'] = '登录失败'
    elif request_type == 'register':
        print('注册')
        # 判断是否有名字重复的现象
        # 而且是一个IP对应一个用户
        # 先判断是否重名
        res['error'] = False
        res['type'] = 'register'
        return res
        if data['account'] in user_name_list:
            # 重名了
            # 3号错误，用户名已存在
            res['error'] = True
            res['error-message'] = '用户名已存在'
            res['error-title'] = '注册失败'
        else:
            print('新建')
            try:
                # 4 号错误，该IP已经存在一个账号
                res['error'] = True
                res['error-message'] = '该IP下已经有一个账户: {}'.format(
                    user_dict[data['account']]['name'])
                res['error-title'] = '注册失败'
            except KeyError:
                user_dict[data['account']]['name'] = data['account']
                user_dict[data['account']]['password'] = data['password']
                user_name_list.append(data['account'])
                res['error'] = False
        # 剩下的再加
    elif request_type == 'P2P':
        print(data['to'])
        user_dict[data['to']]['socket'].send(
            bytes(json.dumps(data), encoding='utf-8'))
        return res
    elif request_type == 'create-group':
        if (data['group-name'] in group_name_list):
            res['error'] = True
            res['error-message'] = '群聊名称已存在'
            res['error-title'] = '新建群聊失败'
        else:
            group_dict[data['group-name']] = {
                'name': data['group-name'],
                'number': 0,
                'memberName': []
            }
            group_name_list.append(data['group-name'])
            data['type'] = 'groupAppend'
            for userName in user_name_list:
                user_dict[userName]['socket'].send(
                    bytes(json.dumps(data), encoding='utf-8'))
            # for userName in user_name_list :
            #     if (userName != data['nowSession']) :
            #         user_dict[userName]['socket'].send(bytes(json.dumps(data), encoding = 'utf-8'))
        return res
    elif request_type == 'Group':
        for userName in user_name_list:
            if (userName != data['from']):
                user_dict[userName]['socket'].send(
                    bytes(json.dumps(data), encoding='utf-8'))
        return res
    print(res)
    # except:
    # 550号错误，服务器run time error
    # res['error'] = True
    # res['error-title'] = '服务器异常'
    # res['error-message'] = '服务器执行时出现故障'
    # # 回应消息的类型
    # res['error'] = False
    res['type'] = request_type
    res['group'] = group_name_list
    res['user'] = user_name_list
    return res

class MessageThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print('[init] message server')
        print('Message Listen Port : 9999')
        ms_server = socketserver.ThreadingTCPServer(
            ("0.0.0.0", 9999), MessageTCPHandler)  # 多线程版
        ms_server.serve_forever()

class FileThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("[init] file server")
        print('Message Listen Port : 8888')
        fl_server = socketserver.ThreadingTCPServer(
            ("0.0.0.0", 8888), FileTCPHandler)  # 多线程版
        fl_server.serve_forever()

if __name__ == "__main__":
    try:
        m_th = MessageThread()
        f_th = FileThread()
        m_th.start()
        f_th.start()
        m_th.join()
        f_th.join()
    except Exception as e:
        print(e)
