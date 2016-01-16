#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import struct
import binascii

def aligne64(block):
    remain = block & 63
    if remain == 0:
        return block
    return block + (64 - remain)

def readTicket(fs, offset, size):
    sigMethod = ''
    sigType = {'RSA_4096_SHA1': 65536, 'RSA_2048_SHA1': 65537, 'Elliptic_Curve_with_SHA1': 65538,
              'RSA_4096_SHA256': 65539, 'RSA_2048_SHA256': 65540, 'ECDSA_with_SHA256': 65541}
    sigSize = {'RSA_4096_SHA1': 512, 'RSA_2048_SHA1': 256, 'Elliptic_Curve_with_SHA1': 60,
              'RSA_4096_SHA256': 512, 'RSA_2048_SHA256': 256, 'ECDSA_with_SHA256': 60}
    sigPadding = {'RSA_4096_SHA1': 60, 'RSA_2048_SHA1': 60, 'Elliptic_Curve_with_SHA1': 64,
              'RSA_4096_SHA256': 60, 'RSA_2048_SHA256': 60, 'ECDSA_with_SHA256': 64}
    sigValue = struct.unpack('>L', fs[offset:offset + 4])[0]
    for Method, Value in sigType.items():
        if Value == sigValue:
            sigMethod = Method
    if sigMethod == '':
        print('Unknown sigMethod')
        return
    sigData = aligne64(sigSize.get(sigMethod) + sigPadding.get(sigMethod))
    ticketDataOffset = offset + sigData
    TitleIDOffset = ticketDataOffset + 156
    try:
        return ''.join(map(lambda b: format(b, '02x'), fs[TitleIDOffset:TitleIDOffset + 8]))
    except Exception as e:
        return binascii.hexlify(fs[TitleIDOffset:TitleIDOffset + 8])

def readContentSerial(fs, offset, size):
    contentSerialOffset = offset + 336
    if sys.version_info > (3, 0):
        return (fs[contentSerialOffset:contentSerialOffset + 16]).strip(b'\x00').decode('ascii')
    else:
        return (fs[contentSerialOffset:contentSerialOffset + 16]).strip(b'\x00')

def ciaTitleSerial(filepath):
    with open(filepath, 'rb') as f:
        fs = f.read()
    certOffset = aligne64(struct.unpack('<L', fs[:4])[0])
    ticketOffset = aligne64(struct.unpack('<L', fs[8:12])[0] + certOffset)
    tmdOffset = aligne64(struct.unpack('<L', fs[12:16])[0] + ticketOffset)
    contentOffset = aligne64(struct.unpack('<L', fs[16:20])[0] + tmdOffset)
    metaOffset = aligne64(struct.unpack('<L', fs[20:24])[0] + contentOffset)
    filesize = os.path.getsize(filepath)
    titleid = readTicket(fs, ticketOffset, struct.unpack('<L', fs[12:16])[0])
    serial = readContentSerial(fs, contentOffset, struct.unpack('<Q', fs[24:32])[0])
    return titleid, serial

if __name__ == '__main__':
    print(ciaTitleSerial('Gundam - The 3D Battle (Japan).cia'))