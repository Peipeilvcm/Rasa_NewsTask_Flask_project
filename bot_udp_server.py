import socket,time,math,os
import sys

from mobile_models import handle_saying

BUFFER_SIZE = 1500

try:#监听端口设置
    port = 8888
except IndexError:
    print("Please enter a correct port number.")
    sys.exit()

try:#UDP连接
    server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
except socket.error:
    print("failed to create socket.")
    sys.exit()
server.bind(("",port))

def response(res, addr):
    #未来，需要考虑长消息，多条消息的处理
    server.sendto(res.encode("utf-8"), client_addr)
    

if __name__=='__main__':
    while(1):
        print("waiting on port:",port)

        data, client_addr = server.recvfrom(BUFFER_SIZE)
        print("接收到: ",data)
        
        res = handle_saying(data.decode("utf-8"))
        print("处理结果: ",res)

        response(res, client_addr)

    server.close()