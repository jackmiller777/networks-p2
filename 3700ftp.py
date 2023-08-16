#!/usr/bin/env python3

from socket import *
import ssl
import sys    
import os
from random import randint

#./client -p 27993 proj1.3700.network miller.john

class Client:
    
    def __init__(self, host, port, data, tls : bool = False):
        self.port = int(port)
        self.tls = tls
        self.hostname = gethostbyname(host)
        self.data = data
        self.session_id = None
        self.client_socket = None

    # Sends a message to the server encoded with a newline
    def send(self, message):
        if not self.data:
            message = (message + '\r\n').encode()
        self.client_socket.send(message)
    
    # Recieves from the server until newline is received
    def recv(self):
        message_from_server = ''
        for i in range(8):
            message_from_server += self.client_socket.recv(1024).decode()
            if '\r\n' in message_from_server:
                if self.data:
                    return message_from_server
                else:
                    return Response(message_from_server)
                
    def data_recv(self, size):
        binary = self.client_socket.recv(size)
        return binary
    
    # Create and connect client socket.
    def start(self):
        
        # Close socket if open
        try:
            self.client_socket.close()
        except:
            pass
        
        identifier = (self.hostname, self.port)
        
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect(identifier)
        
        if self.tls:
            context = ssl.create_default_context()
            self.client_socket = context.wrap_socket(self.client_socket, server_hostname=self.hostname)
        print('Successfully connected to ', self.hostname, ':', self.port, sep='')
            
    def close(self):
        self.client_socket.close()
  
#

class Response:
    rid = 0
    def __init__(self, res):
        Response.rid += 1
        print(Response.rid, res.replace('\r\n',''))
        try:
            self.res = res
            self.code = res[0:3]
            self.msg = res[3:].replace('\r\n','')
        except:
            print('Failed to read response')
            
    def __str__(self):
        return self.res
    
    def has_ip(self):
        return self.code == '227'
        
    def get_ip_port(self):
#        print(self)
        if self.code == '227':
            s = self.msg.find('(') + 1
            e = self.msg.find(')')
            nums = self.msg[s:e].split(',')
            ip = nums[0] + '.' + nums[1] + '.' + nums[2] + '.' + nums[3]
            port = (eval(nums[4]) << 8) + eval(nums[5])
            return ip, port
        else:
            return None
        
    def check(self):
        num = eval(self.code[0])
        if num == 1:
            msg = 'expected'
        elif num == 2:
            msg = 'success'
        elif num == 3:
            msg = 'preliminary success'
        else:
            msg = 'error'
        return msg
        
class FTPClient:
    VALID_OPS = ['ls','mkdir','rmdir','rm','cp','mv']
    
    def __init__(self, operation, arg1, arg2 = None):
        self.operation = operation
        self.arg1 = arg1
        self.arg2 = arg2
        
        if arg1.find('ftp://') != -1:
            ftp_arg = arg1
            self.local_path = arg2
            self.upload = False
        elif arg2.find('ftp://') != -1:
            ftp_arg = arg2
            self.local_path = arg1
            self.upload = True
            
        s = len('ftp://')
        e = ftp_arg[s:].find(':') + s
        self.username = ftp_arg[s:e]
        s = e + 1
        e = ftp_arg.find('@')
        self.password = ftp_arg[s:e]
        s = e + 1
        e = ftp_arg[e:].find(':') + e
        self.hostname = ftp_arg[s:e]
        s = e + 1
        e = ftp_arg[s:].find('/') + s
        self.port = ftp_arg[s:e]
        s = e
        self.host_path = ftp_arg[s:]
        
#        print(s,e,self.username)
#        print(s,e,self.password)
#        print(s,e,self.hostname)
#        print(s,e,self.port)
#        print(s,self.host_path)
        
        self.login()
        
    def run(self):
        op = self.operation
        if op == 'ls':
            self.ls()
        elif op == 'mkdir':
            self.mkdir()
        elif op == 'rmdir':
            self.rmdir()
        elif op == 'rm':
            self.rm()
        elif op == 'cp':
            self.cp()
        elif op == 'mv':
            self.mv()
            
        elif op == 'mv':
            pass
            
        self.close()

    def close(self):
        try:
            self.control.send('QUIT')
            self.control.recv()
            self.control.close()
        except:
            pass
        try:
            self.data_channel.close()
        except:
            pass
        
    def login(self):
        self.control = Client(self.hostname, self.port, data=False)
        self.control.start()
        self.control.send("USER " + self.username)
        self.control.recv()
        self.control.send("PASS " + self.password)
        self.control.recv()
        self.control.send("TYPE I")
        self.control.recv()
        self.control.send("MODE S")
        self.control.recv()        
        self.control.send("STRU F")
        self.control.recv()
        
    def mkdir(self):
        self.control.send("MKD " + self.host_path)
        self.control.recv()   
    def rmdir(self):
        self.control.send("RMD " + self.host_path)
        self.control.recv()
        
    def open_data_channel(self):
        self.control.send("PASV")
        response = self.control.recv()
        while not response.has_ip():
            response = self.control.recv()
        ip, port = response.get_ip_port()
        print('Connecting to ', ip, ':', port, sep='')
        self.data_channel = Client(ip, port, data=True)
        self.data_channel.start()
        
    def ls(self):
        
        self.control.send("PASV")
        response = self.control.recv()
        while not response.has_ip():
            response = self.control.recv()
        ip, port = response.get_ip_port()
        print('Connecting to ', ip, ':', port, sep='')
        self.data_channel = Client(ip, port, data=True)
        self.data_channel.start()
        
        self.control.send("LIST " + self.host_path)
        
        print(self.data_channel.recv())
        self.data_channel.close()
        
    def rm(self):
        self.dele(False)
    
    def retr(self):
        
        self.open_data_channel()
        
        self.control.send("RETR " + self.host_path) 
        res = self.control.recv().res
        s = res.find('(') + 1
        e = res.find(')')
        size = eval(res[s:e].split(' ')[0])
        s = self.host_path.rfind('/') + 1
        filename = self.host_path[s:]
        binary = self.data_channel.data_recv(size)
        print(self.local_path)
        file = open(self.local_path, 'wb')
        file.write(binary)
        self.data_channel.close()
        
    # Stores file on the ftp server
    def stor(self):
        
        self.open_data_channel()
        
        self.control.send("STOR " + self.host_path)
        self.control.recv()
        file = open(self.local_path, 'rb')
        binary = file.read()
        self.data_channel.send(binary)
        self.data_channel.close()
        self.control.recv()
    
    # Copies a file to or from the ftp server depending on args
    def cp(self):
        if self.upload:
            self.stor()
        else:
            self.retr()
    
    # Copies a file to or from the ftp server depending on args, deleting the old file
    def mv(self):
        if self.upload:
            self.stor()
            self.dele(True)
        else:
            self.retr()
            self.dele(False)
        
    # Deletes a file locally or on the ftp server depending on local boolean input
    def dele(self, local):
        if local:
            os.remove(self.local_path)
        else:
            self.control.send("DELE " + self.host_path)
            self.control.recv()
    
        
    # Main Function - checks for args and sets defaults
if __name__ == '__main__':
    
    # Get args
    args = sys.argv
    
    if len(args) == 3:
        ftp = FTPClient(args[1],args[2])
        ftp.run
    elif len(args) == 4:
        ftp = FTPClient(args[1],args[2], args[3])    
        ftp.run()