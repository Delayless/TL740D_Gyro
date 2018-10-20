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
    sleep(0.03)
    return data_temp


def hextostr(int_list):
    """
    将整数列表转换成16进制，并转换成字符串,并连接在一起
    列表中每个值都为一个字节
    :param int_list:整数表示的列表
    :return:
    """
    hexstr = ''
    for item in int_list:
        temp = hex(item)  # 将任意整数转换成16进制表示的字符串，例如100转换为'0x64'
        if len(temp) == 3:
            hexstr = hexstr+'0'+temp[2]  # 一个16进制数以两个字符表示，如0x06对应的字符串为'06'而不是'6';
        else:
            hexstr = hexstr+temp[2]+temp[3]
    # print(hexstr)  # 字符串Unicode 55
    strsend = hexstr.encode()    # 以bytes的形式写到串口
    # print(strsend)                    # bytes '55' print:b'55'
    # hexstr = strsend.decode('utf-8')  # 变回字符串,解码必须与编码方式相同,gb2312 is error
    # print(hexstr)
    return strsend


ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.5)

while True:
    # command = hextostr([0x55])  # 列表
    # U:The character is 0x55
    # P:temperate = int(recv_data_str, 16) - 45
    # command = 'U'
    command = Converter.to_ascii('5550')
    ser.write(command[0].encode())
    ser.write(command[1].encode())
    recv_data_bytes = recv(ser)     # data is <class 'bytes'>  # b'\x02\xc1'
    temp = recv_data_bytes[1]       # <class 'int'>
    print(temp)
    recv_data_str = recv_data_bytes.hex()   # convert to hex

    # print(int(recv_data_str, 16), "mm")  # display using Decimal System 十进制显示
