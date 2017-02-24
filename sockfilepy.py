#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import socket
import struct
import progressbar
from cia_info import ciaTitleSerial

class Express(object):
    def __init__(self, host, filepath):
        super(Express, self).__init__()
        self.host = host
        self.filepath = filepath

    def FileInfo(self, filepath):
        filename = os.path.splitext(filepath)[0]
        filesize = os.path.getsize(filepath)
        print('Filename: ' + filename + '\tFilesize: ' + self.ReadableSize(filesize))
        return filename, filesize

    def ReadableSize(self, size, precision = 2):
        suffixes=[' B', ' KB', ' MB', ' GB']
        suffixIndex = 0
        while size > 1024 and suffixIndex < 4:
            suffixIndex += 1
            size = size/1024.0
        return "%.*f%s"%(precision, size, suffixes[suffixIndex])

    def SendFile(self):
        filename, filesize = self.FileInfo(self.filepath)
        trunksize = 1024 * 256
        filesizebyte = struct.pack('>q', filesize)
        num_files = struct.pack('>i', 1)

        titleid, serial = ciaTitleSerial(self.filepath)
        print('Title ID: ' + titleid + '\tSerial: ' + serial)

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            s.connect((self.host, 5000))
        except Exception as e:
            raise e

        try:
            f = open(self.filepath, 'rb')
            file_buffer = f.read(trunksize)

            progress = progressbar.AnimatedProgressBar(end = os.path.getsize(self.filepath) + len(filesizebyte) + len(num_files),
                                                       width = 70)
            s.send(num_files)

            ack = struct.unpack('b', s.recv(1))[0]
            if ack == 0:
                print('\n\nSend cancelled by remote')
                return

            s.send(filesizebyte)

            while file_buffer:
                totalsent = 0
                while totalsent < len(file_buffer):
                    sent = s.send(file_buffer[totalsent:])
                    if sent == 0:
                        raise Exception("socket broken")

                    progress + sent
                    progress.show_progress()

                    totalsent += sent

                file_buffer = f.read(trunksize)

            f.close()
            s.close()
            print('\n\nFile transfer success.')
        except Exception as e:
            f.close()
            s.close()
            print('\n\nFile transfer failed.')
            raise e

def main():
    if len(sys.argv) != 3 or sys.argv[1] == '-h':
        print('Usage: ' + sys.argv[0] + ' <ip> <file>\n(E.g: ./sockfilepy.py 192.168.1.51 mario.cia)')
        return
    if not (os.path.isfile(sys.argv[2]) and (os.path.splitext(sys.argv[2])[1] == '.cia')):
        print('Sorry, cia file not found.')
        return
    host = sys.argv[1]
    filepath = sys.argv[2]
    Express(host, filepath).SendFile()

if __name__ == '__main__':
    main()
