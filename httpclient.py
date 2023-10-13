#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    def get_host_port(self, url):
        parsed_url = urllib.parse.urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port if parsed_url.port else 80
        return host, port

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(30)  # set a timeout of 10 seconds for socket operations
        self.socket.connect((host, port))

    def get_code(self, data):
        return int(data.split(" ")[1])

    def get_headers(self, data):
        return data.split("\r\n\r\n")[0]

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        try:
            host, port = self.get_host_port(url)
            self.connect(host, port)

            host, port = self.get_host_port(url)
            self.connect(host, port)
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.3"
            request = f"GET {url} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {user_agent}\r\n\r\n"
            self.sendall(request)
            response = self.recvall(self.socket)
            code = self.get_code(response)
            body = self.get_body(response)
            self.close()  # Close the socket
        except socket.timeout:
            return HTTPResponse(408, "Request Timeout")
        except Exception as e:
            return HTTPResponse(500, str(e))
        

    def POST(self, url, args=None):
        host, port = self.get_host_port(url)
        self.connect(host, port)
        body = urllib.parse.urlencode(args) if args else ""
        request = f"POST {url} HTTP/1.1\r\nHost: {host}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {len(body)}\r\n\r\n{body}"
        self.sendall(request)
        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)
        self.close()  # Close the socket
        return HTTPResponse(code, body)


    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)

    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
