#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import socket
import struct
import progressbar
from cia_info import ciaTitleSerial

def FileInfo(filepath):
    filename = os.path.splitext(filepath)[0]
    filesize = os.path.getsize(filepath)
    print('Filename: ' + filename + '\tFilesize: ' + ReadableSize(filesize))
    return filename, filesize

def ReadableSize(size, precision = 2):
    suffixes=[' B', ' KB', ' MB', ' GB']
    suffixIndex = 0
    while size > 1024 and suffixIndex < 4:
        suffixIndex += 1
        size = size/1024.0
    return "%.*f%s"%(precision, size, suffixes[suffixIndex])

def main():
    if len(sys.argv) != 3 or sys.argv[1] == '-h':
        print('Usage: ' + sys.argv[0] + ' <ip> <file>\n(E.g: ./sockfile-cia.py 192.168.1.51 mario.cia)')
        return
    if not (os.path.isfile(sys.argv[2]) and (os.path.splitext(sys.argv[2])[1] == '.cia')):
        print('Sorry, cia file not found.')
        return
    filename, filesize = FileInfo(sys.argv[2])
    host = sys.argv[1]
    trunksize = 1024 * 128
    filesizebyte = struct.pack('>Q', filesize)

    titleid, serial = ciaTitleSerial(sys.argv[2])
    print('Title ID: ' + titleid + '\tSerial: ' + serial)

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((host, 5000))
    except Exception as e:
        raise e

    try:
        f = open(sys.argv[2], 'rb')
        l = f.read(trunksize)
        progress = progressbar.AnimatedProgressBar(end = os.path.getsize(sys.argv[2]) + len(filesizebyte), width = 70)
        s.send(filesizebyte)
        while l:
            s.send(l)
            l = f.read(trunksize)
            progress + trunksize
            progress.show_progress()
        f.close()
        s.close()
        print('\n\nFile transfer success.')
    except Exception as e:
        f.close()
        s.close()
        print('\n\nFile transfer failed.')
        raise e

if __name__ == '__main__':
    main()