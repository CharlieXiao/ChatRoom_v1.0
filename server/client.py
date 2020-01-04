import socket
import threading

class RecvThread(threading.Thread):
    def __init__(self,client_socket):
        print("init receive thread")
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.isExit = False

    def run(self):
        try:
            while True:
                if self.isExit:
                    break
                recv_msg = self.client_socket.recv(1024)
                if len(recv_msg) == 0:
                    break
                print("message: {}".format(recv_msg.decode()))
        finally:
            return
        
if __name__ == "__main__":
    try:
        client=socket.socket()
        client.connect(('127.0.0.1',9999))
        thread_recv = RecvThread(client)
        thread_recv.start()
        while True:
            send_msg = input("(quit推出)>>").strip()
            if len(send_msg) == 0:
                continue
            elif send_msg == "quit":
                thread_recv.isExit = True
                client.close()
                break
                # 应该还需要关闭接受进程
            else:
                print(client.send(send_msg.encode()))
    except Exception as e:
        print(e)
    

