import socket

host = 'localhost'
port = 60000


def s_client():
    """ A simple client """
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the server
    server_address = (host, port)
    print "Connecting to %s port %s" % server_address
    sock.connect(server_address)

    # Send data
    try:
        message = ":731CDF2100007517010101140000000001000100FD00AB026000000082010F00000000FF000000000D"
        print "Sending %s" % message
        sock.sendall(message)
    except socket.errno, e:
        print "Socket error: %s" % str(e)
    except Exception, e:
        print "Other exception: %s" % str(e)
    finally:
        print "Closing connection to the server"
        sock.close()

if __name__ == '__main__':
    s_client()
