#!usr/bin/python3

import serial
from time import sleep
from ASCII_conv_hex import Converter


def recv(ser_temp):
    """
    读数据
    """
    while True:
        data_temp = ser_temp.read_all()
        # 这里可以优化,找到0x68后break
        if data_temp == b'':
            continue
        else:
            break
    # sleep(0.02)
    return data_temp


def execute_cmd(command):
    """
    写命令，将传感器的返回值return
    """
    # 可以一个字节一个字节的发送
    # 也可以一次把整个命令发送,即不用for循环
    # 直接ser.write(command.encode())
    ser.flushOutput()
    ser.flushInput()
    for i in range(len(command)):
        ser.write(command[i].encode())
    sleep(0.01)  # 发现数据不完整，没有传输完成时延长这里的时间
    feedback = recv(ser)
    analyse_reply(feedback)


def BCDtoINT(raw_data):
    """
    将3个字符的BCD原始数据转换成int型并返回
    """
    value = (raw_data[0] & 0x01) * 10000 + ((raw_data[1] & 0xf0) >> 4) * 1000 + \
            (raw_data[1] & 0x0f) * 100 + ((raw_data[2] & 0xf0) >> 4) * 10 + (raw_data[2] & 0x0f)

    if raw_data[0] & 0x10:
        return -value

    else:
        return value


def Attitude_algorithm_9(roll_raw, pitch_raw, yaw_raw,
                         acc_x_raw, acc_y_raw, acc_z_raw,
                         grop_x_raw, grop_y_raw, grop_z_raw):
    roll = BCDtoINT(roll_raw) * 0.01
    pitch = BCDtoINT(pitch_raw) * 0.01
    yaw = BCDtoINT(yaw_raw) * 0.01
    acc_x = BCDtoINT(acc_x_raw) * 0.001
    acc_y = BCDtoINT(acc_y_raw) * 0.001
    acc_z = BCDtoINT(acc_z_raw) * 0.001
    grop_x = BCDtoINT(grop_x_raw) * 0.01
    grop_y = BCDtoINT(grop_y_raw) * 0.01
    grop_z = BCDtoINT(grop_z_raw) * 0.01
    # print("横滚角(ROLL):%f°" % roll)
    print("俯仰角(PITCH):%f°" % pitch)
    '''
    print("航向角(YAW):%f°" % yaw)
    print("X轴加速度(ACCX):%fg" % acc_x)
    print("Y轴加速度(ACCY):%fg" % acc_y)
    print("Z轴加速度(ACCZ):%fg" % acc_z)
    print("X轴角速率(Groy x):%f°/s" % grop_x)
    print("Y轴角速率(Groy y):%f°/s" % grop_y)
    print("Z轴角速率(Groy z):%f°/s" % grop_z)
    '''

def Attitude_algorithm_3(grop_z_raw, acc_y_raw, yaw_raw):
    grop_z = BCDtoINT(grop_z_raw) * 0.01
    acc_y = BCDtoINT(acc_y_raw) * 0.001
    yaw = BCDtoINT(yaw_raw) * 0.01
    print("Z轴角速率(Groy z):%f°/s" % grop_z)
    print("Y轴加速度(ACCY):%fg" % acc_y)
    print("横滚角(ROLL)::%f°" % yaw)


def analyse_reply(reply_data):
    """
    分析从传感器回传的数据
    """
    if reply_data[0] == 0x68:
        if reply_data[3] == 0x0B:
            # 串口波特率设置
            if reply_data[4] == 0x00:
                print("Baud Rate Setup Succeeded!")
            else:
                print("Baud Rate Setup Failure!")

        elif reply_data[3] == 0x28:
            # 方位角清零
            if reply_data[4] == 0x00:
                print("Clear data Succeeded!")
            else:
                print("Clear data Failure!")

        elif reply_data[3] == 0xFD:
            # 数据类型输出设定
            if reply_data[4] == 0x00:
                print("Output Mode Setup Succeeded!")
            else:
                print("Output Mode Setup Failure!")

        elif reply_data[3] == 0X84:
            # 传感器自动输出角度
            data_length = reply_data[1] - 4

            if data_length == 27:
                Attitude_algorithm_9([reply_data[4], reply_data[5], reply_data[6]],
                                     [reply_data[7], reply_data[8], reply_data[9]],
                                     [reply_data[10], reply_data[11], reply_data[12]],
                                     [reply_data[13], reply_data[14], reply_data[15]],
                                     [reply_data[16], reply_data[17], reply_data[18]],
                                     [reply_data[19], reply_data[20], reply_data[21]],
                                     [reply_data[22], reply_data[23], reply_data[24]],
                                     [reply_data[25], reply_data[26], reply_data[27]],
                                     [reply_data[28], reply_data[29], reply_data[30]])

            elif data_length == 9:
                Attitude_algorithm_3([reply_data[4], reply_data[5], reply_data[6]],
                                     [reply_data[7], reply_data[8], reply_data[9]],
                                     [reply_data[10], reply_data[11], reply_data[12]])

            else:
                print("Please check the programme!")
    else:
        return


ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.5)

# 两种方法都可以
setBaudrate_9600 = '\x68\x05\x00\x0B\x02\x12'  # sensor_baudrate
setBaudrate_115200 = Converter.hex_to_ascii('6805000B0515')
clearSensor = Converter.hex_to_ascii('680400282C')  # 方位角清零命令
set9mpu = Converter.hex_to_ascii('680500FD7072')  # 9 轴输出
set_mpu_default = Converter.hex_to_ascii('680500FD7173')  # 标准格式 1 输出（Z 轴角速率+前进（Y 轴）加速度+Z 轴航向角
Get_angle = Converter.hex_to_ascii('6804000408')  # 同时读角度命令

execute_cmd(setBaudrate_115200)
execute_cmd(clearSensor)
sleep(0.02)
execute_cmd(clearSensor)
execute_cmd(set9mpu)
while True:
    execute_cmd(Get_angle)
    # sleep(0.03)
