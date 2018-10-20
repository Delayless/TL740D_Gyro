#!usr/bin/python3

import serial
from ASCII_conv_hex import Converter
from time import sleep


def recv(ser_temp):
    while True:
        data_temp = ser_temp.read_all()
        if data_temp == b'':
            continue
        else:
            break
    sleep(0.02)
    return data_temp


ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.5)

while True:
    # command = hextostr([0x55])  # 列表
    # U:The character is 0x55
    # P:temperate = int(recv_data_str, 16) - 45
    # command = 'U'
    command = Converter.to_ascii('5550')
    recv_data_byte = [0, 0]
    for i in range(2):
        ser.write(command[i].encode())
        recv_data_byte[i] = recv(ser)
        sleep(0.01)  # 发现数据不完整，没有传输完成时延长这里的时间

    recv_distance_str = recv_data_byte[0].hex()   # convert to hex
    recv_temperate_str = recv_data_byte[1].hex()   # convert to hex
    print(int(recv_distance_str, 16), "mm  ", end='     ')  # display using Decimal System 十进制显示
    print(int(recv_temperate_str, 16)-45, "degree")
