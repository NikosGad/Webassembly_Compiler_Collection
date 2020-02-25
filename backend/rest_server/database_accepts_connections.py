import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(('ucrm_db',5432))
    s.close()
    print("Connected to PostgreSQL")
    exit(0)
except socket.error as ex:
    print("Connection failed with errno {0}: {1}\nWaiting for PostgreSQL...".format(ex.errno, ex.strerror))
    exit(1)
