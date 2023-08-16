#!/usr/bin/env python3

from socket import *
import ssl
import sys    
import os
from random import randint

# ./3700ftp operation <arg1> <arg2>

# Mostly the same client from proj1, with added data tag
# for the data channel that ftp uses.
class Client:
    
    def __init__(self, host, port, data, tls : bool = False):
        self.port = int(port)
        self.tls = tls
        self.hostname = gethostbyname(host)
        self.data = data
        self.session_id = None
        self.client_socket = None

    # Sends a message to the server encoded with a newline
    # (no newline if data channel)
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
         
    # Special recv for data channel
    def data_recv(self, size):
        if self.data:
            binary = self.client_socket.recv(size)
            return binary
        else:
            raise Exception('Tried to receive data on a non data channel')
    
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
      
    # Close socket
    def close(self):
        self.client_socket.close()
  
#

# Class for processing server responses
class Response:
    rid = 0
    def __init__(self, res):
        Response.rid += 1
        print(res.replace('\r\n',''))
        try:
            self.res = res
            self.code = res[0:3]
            self.msg = res[3:].replace('\r\n','')
        except:
            print('Failed to read response')
      
    # Returns response as string
    def __str__(self):
        return self.res
    
    # Returns true if message is response to "PASV" message
    def has_ip(self):
        return self.code == '227'
        
    # Reads ip and port from response
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
            raise Exception('Not a valid response')
        
    # Helper to translate error level of response
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
 
# MAIN FTP CLIENT
# Starts and stops sockets, and processes operations
class FTPClient:
    VALID_OPS = ['ls','mkdir','rmdir','rm','cp','mv']
    
    # Checks and arranges operation/inputs, 
    def __init__(self, operation, arg1, arg2 = None):
        self.operation = operation
        self.arg1 = arg1
        self.arg2 = arg2
        
        if operation not in FTPClient.VALID_OPS:
            raise Exception("INVALID OPERATION")
        
        if arg1.find('ftp://') != -1:
            ftp_arg = arg1
            self.local_path = arg2
            self.upload = False
        elif arg2.find('ftp://') != -1:
            ftp_arg = arg2
            self.local_path = arg1
            self.upload = True
            
        # Process ftp arg for username, password, hostname, port, path
        s = len('ftp://')
        e = ftp_arg[s:].find(':') + s
        self.username = ftp_arg[s:e]
        s = e + 1
        e = ftp_arg.find('@')
        self.password = ftp_arg[s:e]
        s = ftp_arg.find('@') + 1
        e = ftp_arg[s:].find('/')
        self.hostname = ftp_arg[s:][:e]
        s = e + 1
        e = ftp_arg[s:].find('/') + s
        self.port = 21
        s = e
        self.host_path = ftp_arg[s:]
        
        self.login()
        
    # Checks op and runs correct operation
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
            
        self.close()

    # Attempt to close all sockets
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
     
    # Sends login info and sets up data transfer
    def login(self):
        
        print('Connecting to ', self.hostname, ':', self.port, sep='')
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
        
    # Makes a directory
    def mkdir(self):
        self.control.send("MKD " + self.host_path)
        self.control.recv()   
    # Removes a directory
    def rmdir(self):
        self.control.send("RMD " + self.host_path)
        self.control.recv()
        
    # Sends PASV command and opens corresponding data channel
    def open_data_channel(self):
        self.control.send("PASV")
        response = self.control.recv()
        while not response.has_ip():
            response = self.control.recv()
        ip, port = response.get_ip_port()
        print('Connecting to ', ip, ':', port, sep='')
        self.data_channel = Client(ip, port, data=True)
        self.data_channel.start()
        
    # Lists contents of directory
    def ls(self):
        self.open_data_channel()
        
        self.control.send("LIST " + self.host_path)
        
        print(self.data_channel.recv())
        self.data_channel.close()
    
    # Removes a file from ftp servers with dele method
    def rm(self):
        self.dele(False)
    
    # Retreives a file from ftp server
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
     
    # Stores a file on the ftp server
    def stor(self):
        self.open_data_channel()
        
        self.control.send("STOR " + self.host_path)
        self.control.recv()
        file = open(self.local_path, 'rb')
        binary = file.read()
        self.data_channel.send(binary)
        self.data_channel.close()
        self.control.recv()
    
    # Copies a file from local to ftp or vice versa
    def cp(self):
        if self.upload:
            self.stor()
        else:
            self.retr()
    
    # Moves a file from local to ftp or vice versa, deletes old file after
    def mv(self):
        if self.upload:
            self.stor()
            self.dele(True)
        else:
            self.retr()
            self.dele(False)
        
    # Deletes a file locally or from ftp server
    def dele(self, local):
        if local:
            os.remove(self.local_path)
        else:
            self.control.send("DELE " + self.host_path)
            self.control.recv()
    
        
    # Main Function - checks for args and sets defaults
if __name__ == '__main__':
    
    # Process args
    args = sys.argv
    
    if len(args) == 3:
        ftp = FTPClient(args[1],args[2])
        ftp.run()
    elif len(args) == 4:
        ftp = FTPClient(args[1],args[2], args[3])    
        ftp.run()
    
    