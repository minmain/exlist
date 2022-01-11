#!/usr/bin/python
# -*- coding: utf-8 -*-

#endianness = [
#    ('@', 'native, native'),
#    ('=', 'native, standard'),
#    ('<', 'little-endian'),
#    ('>', 'big-endian'),
#    ('!', 'network'),
#    ]

import binascii
import socket
import struct
import sys
import select
import time

def set_modbus_request(unit, cmd, addr, cnt):
	if addr > 10000:
		addr = addr % 10000 - 1
	# transaction identifier (2), protocol identifier (2), length (2), 
	packet = struct.pack(">HHBBBBHH", 0, 0, 0, 6, unit, cmd, addr, cnt)
	return packet

def set_modbus_write(unit, cmd, addr, val):
	if addr > 10000:
		addr = addr % 10000 - 1
	# transaction identifier (2), protocol identifier (2), length (2), 
	packet = struct.pack(">HHBBBBHH", 0, 0, 0, 6, unit, cmd, addr, val)
	return packet

def usage(myname):
	temp = myname.split('\\')
	tlen = len(temp)
	print "-----  usage  -----"
	print "read : %s r 1 30007 20" % (temp[tlen - 1])
	print "write : %s w 1 40001 0xAADD" % (temp[tlen - 1])
	sys.exit(0)

def send_request(sunit, saddr, scnt):
	scmd = 4
	if (saddr / 10000) == 3 :
		scmd = 4
	elif (saddr / 10000) == 4:
		scmd = 3

	print "send command : %d (%d)" % (scmd, saddr)

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect(ADDR)

	sbuf = set_modbus_request(sunit, scmd, saddr, scnt)
	print repr(sbuf)
	sock.send(sbuf)

	time.sleep (0.05)

	sock.settimeout(3.0)
	rbuf = sock.recv(BUFSIZE)

	sock.close()

	print repr(rbuf)

	rsize = struct.unpack('>B', rbuf[5:6])[0]
	runit = struct.unpack('>B', rbuf[6:7])[0]
	rcmd = struct.unpack('>B', rbuf[7:8])[0]
	rdsize = struct.unpack('>B', rbuf[8:9])[0]
	buf_size = struct.calcsize(rbuf)
	print "recv size : %d" % (rsize)
	print "buf size : %d" % (len(rbuf))
	#print ("[%d] recv size : %d, unit id : %d, cmd : %d, data size : %d" % (len(rbuf), rsize, runit, rcmd, rdsize))

	for i in range(9, len(rbuf)):
		if ( i % 2) :
			b = struct.unpack('>BB', rbuf[i:i+2])
			ret = b[0] * 256 + b[1]
			print "[%02d] %d (%02s)" % ((i - 9)/2 + 1, ret, hex(ret))

#
#
#
def send_write(sunit, saddr, scnt):
	if (saddr / 10000) == 4 :
		scmd = 6
	
	print "send command : %d, read value : %x" % (scmd, scnt)

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect(ADDR)

	sbuf = set_modbus_write(sunit, scmd, saddr, scnt)
	print repr(sbuf)
	sock.send(sbuf)

	time.sleep (0.05)

	sock.settimeout(3.0)
	rbuf = sock.recv(BUFSIZE)

	sock.close()

	print repr(rbuf)

if __name__ == "__main__":

	HOST = '192.168.10.165'
	PORT = 502
	ADDR = (HOST, PORT)
	BUFSIZE = 4096

	alen = len(sys.argv)

	if alen < 2:
		usage(sys.argv[0])
	else:
		rw_mode = sys.argv[1]
		sunit = int(sys.argv[2])
		saddr = int(sys.argv[3])

	scmd = 0

	if ( rw_mode == "r" ):
		scnt = int(sys.argv[4])
		send_request(sunit, saddr, scnt)

	# write modbus
	elif (rw_mode == "w"):
		if len(sys.argv[4]) > 1 and sys.argv[4][0:2] == '0x':
			h = sys.argv[4][2:]
			if len(h) % 2:
				h = "0" + h
			scnt = int(h, 16)
		else:
			scnt = int(sys.argv[4])

		print "read value : %d(%s)" % (scnt, struct.pack('>H', scnt))

		send_write(sunit, saddr, scnt)

		print "write >>>>>>>>>>>>>>>>>>>>>\n"

		time.sleep(0.5)

		send_request(sunit, saddr, 1)

	sys.exit(0)
