import socket
import time
import errno
import select
import logging

#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

sock = None

def socket_thread(p, requests):

    returnFlag = False
    cursor = 0
    while True:
        logger.debug('starting polling...')
        l = p.poll(10000)
        logger.debug('starting polling done...')
        if len(l) ==0:
            logger.debug('polling timeout, returning...')
            returnFlag = True
        #logger.debug('{}'.format(l))
        for t in l:
            #logger.debug('{}'.format(t))
            #sock = t[0]
            event = t[1]
            if(event & select.POLLERR or event & select.POLLHUP):
                logger.debug('pollerr or pollup')
                sock.close()
                returnFlag = True
                continue
            if(event & select.POLLOUT):
                try:
                    if cursor ==0:
                        logger.debug('sending data...')
                        #sock.send(requests)
                        #write(sock,requests)
                        #sock.write(requests)
                        sock.send(requests.encode())
                        
                        # We only want to send one message on this socket, in the future wait only for new incoming messages
                        p.modify(sock, select.POLLIN | select.POLLHUP | select.POLLERR)
                        logger.debug('sending data done...')
                        cursor += 1
                        continue
                    else:
                        pass
                except:
                    raise
                    # pass
            if(event & select.POLLIN):
                try:
                    logger.debug('receiving data...')
                    r = sock.recv(256)
                    logger.debug('receiving data done...')
                    # If recv() returns with 0 the other end closed the connection
                    if len(r) == 0:
                        sock.close()
                        logger.debug('len(r)=0, sock.close()')
                        returnFlag = True
                        continue
                    else:
                        # Do something with the received data...
                        logger.debug("Data received: " + str(r))
                        logger.debug("sock.close() ...")
                        sock.close()
                        logger.debug("sock.close() done ...")
                        returnFlag = True
                        return r.decode('ASCII')
                except:
                    pass
        if returnFlag is True:
            break
    return



def request(requests):
    global sock
    
    logger.debug('setting up socket...')
    # List for storing our sockets
    socket_list = []

    # Set up the first socket in non-blocking mode
    sock = socket.socket()
    sock.setblocking(True)
    sock.settimeout(10)
    # s1.setblocking(False)
    socket_list.append(sock)
    # # Set up the second socket in non-blocking mode
    # s2 = socket.socket()
    # s2.setblocking(False)
    # socket_list.append(s2)

    # Create a new poll object
    p = select.poll()
    # Register the sockets into the poll object, wait for all kind of events
    p.register(sock, select.POLLIN | select.POLLOUT | select.POLLHUP | select.POLLERR)
    # p.register(sock, select.POLLIN | select.POLLOUT | select.POLLHUP | select.POLLERR)
    logger.debug('setting up socket done...')

    for s in socket_list:
        try:
            logger.debug('connecting to the server...')
            out = s.connect(socket.getaddrinfo("192.168.1.51", 6543)[0][-1])
            logger.debug(out)
            logger.debug('connecting to the server done...')
            logger.debug('starting socket_thread...')
            response = socket_thread(p,requests)
            logger.debug('starting socket_thread done...')
            return response
        except socket.timeout:
            logger.debug('Timeout error occurred...')
        except :
            pass
    return

