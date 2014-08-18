#! /usr/bin/env python
#-*-encoding=utf-8-*-

import socket 
import os
import pdb
import errno 
import struct
import pwd 
import marshal 


from struct import unpack
from struct import pack
from cStringIO import StringIO 
from time import sleep 
from time import time
from select import *
from fcntl import *


#server ip, port 
SERVER_IP = "127.0.0.1"
SERVER_PORT = 9988

MAX_LISTEN = 1024
REMOTE = ("127.0.0.1", 9905)

cons = {} 
g = globals() 

EAGAIN = errno.EAGAIN


STATUS_HANDSHAKE = 0x1 << 1 
STATUS_REQUEST = 0x1 << 2
STATUS_WAIT_REMOTE = 0x1 << 3
STATUS_DATA = 0x1 << 4

STATUS_SERVER_HANDSHKAE = 0x1 << 5
STATUS_SERVER_REQUEST = 0x1 << 6 
STATUS_SERVER_CONNECTED = 0x1 <<7
STATUS_SERVER_WAIT_REMOTE = 0x1 << 8


def run_as_user(user):
    try:
        db = pwd.getpwnam(user)
    except KeyError:
        raise Exception("user doesn't exists") 
    try:
        os.setgid(db.pw_gid)
    except OSError:        
        raise Exception("change gid failed") 
    try:
        os.setuid(db.pw_uid)
    except OSError:
        raise Exception("change uid failed") 



def daemonize():
    log_file = open("/tmp/encrypted_client.log", "w+", buffering=False)
    try:
        status = os.fork()
    except OSError as e:
        print e
    if not status: 
        os.setsid()
        os.close(0)
        os.close(1)
        os.close(2)
        stdin = open("/dev/null", "r")
        os.dup2(log_file.fileno(), 1)
        os.dup2(log_file.fileno(), 2)
        try:
            status2 = os.fork()
        except OSError as e:
            print e
        if status2:
            exit()
    else:
        exit()        


def read_key(keyfile): 
    f = open(keyfile, "r")
    result = marshal.loads(f.read())
    f.close()
    return result


def set_globals(): 
    g["sock"] = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((SERVER_IP, SERVER_PORT)) 
    sock.listen(MAX_LISTEN) 
    g["sockfd"] = sock.fileno() 
    g["epoll_object"] = epoll()
    epoll_object.register(sockfd, EPOLLIN | EPOLLERR)
    g["SD"], g["DS"] = read_key("key") 
    g["SOCKS_HANDSHAKE_CLIENT"] = "\x05\x01\x00".translate(SD)
    g["SOCKS_HANDSHAKE_SERVER"] = "\x05\x00".translate(SD)
    g["SOCKS_REQUEST_OK_RAW"] = "\x05\x00\x00\x01%s%s" % (socket.inet_aton("0.0.0.0"), pack(">H", 8888))
    g["SOCKS_REQUEST_OK"] = SOCKS_REQUEST_OK_RAW.translate(SD) 


def clean_profile(context): 
    #close client buffer
    context["in_buffer"].close()
    context["out_buffer"].close() 
    #close client socket
    try: 
        context["from_conn"].shutdown(socket.SHUT_RDWR) 
    except Exception as e:
        pass
    try:
        context["from_conn"].close() 
    except Exception as e:
        pass
    try:
        context["to_conn"].shutdown(socket.SHUT_RDWR)
    except Exception as e:
        pass
    try:
        context["to_conn"].close()
    except Exception as e:
        pass
    try:
        epoll_object.unregister(context["from_conn"].fileno()) 
    except Exception as e:
        pass

def clean_queue(context): 
    #close pipe 
    server = True
    try:
        server_fd  = context["to_conn"].fileno()
    except:
        server = False 
    clean_profile(context) 
    del cons[context["fd"]] 
    if server:
        context_server = cons[server_fd]
        clean_profile(context_server) 
        del cons[server_fd]

    
def handle_write_later(context): 
    out_buffer = context["out_buffer"]
    from_conn = context["from_conn"] 
    if out_buffer.tell(): 
        data = out_buffer.getvalue()
        data_count = len(data) 
        try: 
            data_sent = from_conn.send(data) 
        except socket.error as e: 
            if e.errno != EAGAIN: 
                clean_queue(context)
            return 
        if data_sent != data_count: 
            out_buffer.write(data[data_sent:])
        out_buffer.truncate(0)


def handle_handshake(context): 
    from_conn = context["from_conn"]
    fd = context["fd"] 
    try:
        raw = from_conn.recv(128) 
    except socket.error as e:
        clean_queue(context)
        return
    #maybe RST
    if not raw: 
        clean_queue(context)
        return 
    #connect, or bind
    if not (raw.startswith("\x05\x01") or raw.startswith("\x05\x02")): 
        clean_queue(context)
        return
    #handshake packet or not 
    if len(raw) > 12:
        clean_queue(context)
        return
    #connect our server
    try:        
        request_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        request_sock.setblocking(0)  
        request_fd = request_sock.fileno()
        epoll_object.register(request_fd, EPOLLIN|EPOLLOUT)
    except Exception as e: 
        clean_queue(context)
        return 
    #request context 
    cons[request_fd] = {
            "in_buffer": StringIO(),
            "out_buffer": StringIO(),
            "from_conn": request_sock,
            "to_conn": from_conn,
            "crypted": False, 
            "request": "",
            "status": STATUS_SERVER_CONNECTED, 
            } 
    context["to_conn"] = request_sock
    #next status , CONNECTED
    context["status"] = STATUS_REQUEST
    context["request"] = ""

    try: 
        request_sock.connect(REMOTE)
    except socket.error as e: 
        #close connection if it's a real exception
        if e.errno != errno.EINPROGRESS: 
            clean_queue(context) 


def which_status(context): 
    fd = context["fd"]
    from_conn = context["from_conn"] 
    status = None 
    #we don't read more until we can send them out
    to_conn = context["to_conn"]
    if to_conn: 
        if cons[to_conn.fileno()]["out_buffer"].tell():
            return 
    try:
        text = from_conn.recv(256) 
    except socket.error as e: 
        clean_queue(context)
        return 
    #may RST
    if not text: 
        clean_queue(context)
        return 
    raw = text
    #if this msg if from server, decrypt it
    if not context["crypted"]: 
        raw = text.translate(DS)           
    if raw.startswith("\x05\x00\x00\x01"):
        status = STATUS_SERVER_WAIT_REMOTE
    elif raw.startswith("\x05\x01\x00"):
        status = STATUS_REQUEST 
    elif raw == "\x05\x00": 
        status = STATUS_SERVER_HANDSHKAE 
    else:            
        status = STATUS_DATA 
    return status, text


def handle_server_connected(context): 
    try: 
        context["from_conn"].send(SOCKS_HANDSHAKE_CLIENT) 
    except socket.error: 
        context["out_buffer"].write(SOCKS_HANDSHAKE_CLIENT) 

    context["status"] = STATUS_SERVER_HANDSHKAE 


def handle_server_handshake(context): 
    to_context = cons[context["to_conn"].fileno()]
    try:
        context["to_conn"].send("\x05\x00")
    except socket.error: 
        to_context["out_buffer"].write("\x05\x00") 
    #client may REQUEST 
    context["status"] = STATUS_REQUEST
    to_context["status"] = STATUS_REQUEST
    

def handle_new_request(context, text): 
    to_conn = context["to_conn"]
    to_context = cons[to_conn.fileno()] 
    parse_buffer = StringIO()
    parse_buffer.write(text)
    parse_buffer.seek(4) 
    addr_to = text[3]
    addr_type = ord(addr_to)
    if addr_type == 1:
        addr = socket.inet_ntoa(parse_buffer.read(4))
        addr_to += addr
    elif addr_type == 3: 
        addr_len = parse_buffer.read(1)
        addr = parse_buffer.read(ord(addr_len))
        addr_to += addr_len + addr
    elif addr_type == 4:
        addr = parse_buffer.read(16)
        net = socket.inet_ntop(socket.AF_INET6, addr)
        addr_to += net
    addr_port = parse_buffer.read(2) 
    parse_buffer.close()
    addr_to += addr_port

    try:
        port = unpack(">H", addr_port)
    except struct.error: 
        clean_queue(context)
        return

    remote = (addr, port[0]) 
    print "new request %s: %d" % remote
    context["request"] = remote
    to_context["request"] = remote 
    
    try:        
        to_conn.send(text.translate(SD)) 
    except socket.error as e: 
        if e.errno == EAGAIN:
            to_context["out_buffer"].write(text.translate(SD))  


def handle_server_wait_remote(context): 
    to_conn = context["to_conn"]
    to_context = cons[to_conn.fileno()] 
    try: 
        to_conn.send(SOCKS_REQUEST_OK_RAW)
    except socket.error:
        to_context["out_buffer"].write(SOCKS_REQUEST_OK_RAW)
        return 
    context["status"] = STATUS_DATA
    to_context["status"] = STATUS_DATA 

def read_to_buffer(con, buf): 
    while True:
        try: 
            data = con.recv(4096)
            if not data:
                break
            buf.write(data) 
        except socket.error as e:
            if e.errno == EAGAIN:
                break 
            raise e


def handle_redirect_data(context, text): 
    from_conn = context["from_conn"]
    to_conn = context["to_conn"]
    to_context = cons[context["to_conn"].fileno()]
    to_out_buffer = to_context["out_buffer"] 
    in_buffer = context["in_buffer"] 
    in_buffer.write(text)  
    try:
        read_to_buffer(from_conn, in_buffer)
    except socket.error as e: 
        clean_queue(context)
        return
    data_count = in_buffer.tell() 
    raw = in_buffer.getvalue()
    if context["crypted"]:
        raw = raw.translate(SD)
    else:
        raw = raw.translate(DS)
    in_buffer.truncate(0) 
    try: 
        data_sent = to_conn.send(raw) 
    except socket.error as e:
        if e.errno == EAGAIN: 
            to_out_buffer.write(raw) 
        else: 
            clean_queue(context)
        return    
    if data_sent != data_count: 
        to_out_buffer.write(raw[data_sent:])


def handle_pollout(context):
    status = context["status"] 
    if status & STATUS_SERVER_CONNECTED: 
        handle_server_connected(context) 
        return
    if context["out_buffer"].tell(): 
        handle_write_later(context) 


def handle_pollin(context): 
    status = context["status"] 
    if status & STATUS_HANDSHAKE: 
        handle_handshake(context)
        return 
    result = which_status(context)
    if not result:
        return
    status, text = result 
    if status & STATUS_SERVER_HANDSHKAE: 
        handle_server_handshake(context)
        return 

    if status & STATUS_REQUEST: 
        handle_new_request(context, text) 
        return

    if status & STATUS_SERVER_WAIT_REMOTE: 
        handle_server_wait_remote(context)
        return 

    if status & STATUS_DATA: 
        handle_redirect_data(context, text)

def handle_connection(): 
    conn, addr = sock.accept() 
    fd = conn.fileno() 
    conn.setblocking(0)
    epoll_object.register(fd, EPOLLIN|EPOLLOUT|EPOLLERR)
    #add fd to queue
    cons[fd] = {
            "in_buffer": StringIO(),
            "out_buffer": StringIO(),
            "from_conn": conn,
            "to_conn": None,
            "crypted": True,
            "request": None,
            "status": STATUS_HANDSHAKE, 
            } 

def handle_socket(event): 
    if event & EPOLLIN:
        handle_connection() 
    if event & EPOLLERR:
        raise Exception("fatal error") 


def poll_wait(): 
    fast = True
    ep_poll = epoll_object.poll
    while True: 
        if fast:
            sleep_time = 0
            fast = False
        else:
            sleep_time = 0.1 
        sleep(sleep_time) 

        for fd, event in ep_poll(1): 
            if fd == sockfd: 
                handle_socket(event) 
                continue
            if fd not in cons: 
                continue 
            context = cons[fd] 
            context["fd"] = fd 
            if event & EPOLLERR:
                clean_queue(context)
                continue 
            if (not (event & EPOLLIN)) and (
                not context["out_buffer"].tell()) and (
                    not context["status"] & STATUS_SERVER_CONNECTED): 
                continue 
            fast = True
            if event & EPOLLOUT:
                handle_pollout(context) 
            if event & EPOLLIN:
                handle_pollin(context) 

if __name__ == "__main__":
    set_globals() 
    #daemonize()
    poll_wait()
