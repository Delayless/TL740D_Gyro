#!usr/bin/python3

# 先将字符串命令(str:形如'6805000B0212')转换成ASCII值之后
# 再转换成(byte:形如/x60/x98)二进制码才能往串口写,发送给串口
import serial
from time import sleep
import tkinter as tk
from tkinter import messagebox as messagebox
import threading


def recv(ser_temp):
    """
    读数据
    """
    data_temp = b'h'
    ser_temp.read_until(terminator=b'h', size=50)  # 丢弃前面的垃圾值
    # 以0x68为数据头,但不能以b'h'为截止接收标志位,因为可能中间的数据会出现\x68
    data_temp = data_temp + ser_temp.read_until(size=32)  # 默认是遇到换行符终止数据接收

    return data_temp


def execute_cmd(command):
    """
    写命令，将传感器的返回值return
    """
    # 接收到的数据错误时,会重新执行命令
    # 为了不会因为数据一直错误而进入死循环,加了一个执行次数的参数
    # 就算数据接收错误, 也最多只执行五次
    exe_times = 0
    while True:
        ser.flushOutput()     # 清空发送缓存器
        ser.flushInput()      # 清空接收缓存器
        ser.write(command)    # 执行命令
        feedback = recv(ser)  # 接收传感器的回传数据

        exe_flag = analyse_reply(feedback)  # 分析解算回传数据,并返回成功与否标志位
        exe_times = exe_times + 1
        if exe_flag or exe_times >= 5:
            break


def BCDtoINT(raw_data):
    """
    将3个字符的BCD原始数据转换成int型并返回
    按照通讯协议将陀螺仪传感器返回的BCD数据转换成十进制数据
    """
    value = (raw_data[0] & 0x01) * 10000 + ((raw_data[1] & 0xf0) >> 4) * 1000 + \
            (raw_data[1] & 0x0f) * 100 + ((raw_data[2] & 0xf0) >> 4) * 10 + (raw_data[2] & 0x0f)

    if raw_data[0] & 0x10:
        return -value

    else:
        return value


def analyse_reply(reply_data):
    """
    分析从传感器回传的数据
    reply_data是二进制数据,但是对它括号运算符索引的话会自动转换成int类型
    """
    # 数据并不是刚好不多不少的完整一帧
    # 数据长度理论上是33,或者小于33(默认遇到换行符时停止数据接收)
    if len(reply_data) >= 5:
        # reply_hex_data = bytes.hex(reply_data)
        # if reply_hex_data[0:0+2] == '68':
        if reply_data[0] == 0x68:
            if reply_data[3] == 0x8B:
                # 串口波特率设置
                if reply_data[4] == 0x00:
                    messagebox.showinfo('Baud Rate Setup', "串口波特率设置成功!")
                else:
                    messagebox.showinfo('Baud Rate Setup', "串口波特率设置失败,请重新操作!")

            elif reply_data[3] == 0x28:
                # 方位角清零
                if reply_data[4] == 0x00:
                    messagebox.showinfo('Clear data', "方位角清零成功!")
                else:
                    messagebox.showinfo('Clear data', "方位角清零失败,请重新操作!")

            elif reply_data[3] == 0xFD:
                # 数据类型输出设定
                if reply_data[4] == 0x00:
                    messagebox.showinfo('Output Mode Setup', "数据类型输出设定成功!")
                else:
                    messagebox.showinfo('Output Mode Setup', "数据类型输出设定失败,请重新操作!")

            elif reply_data[3] == 0x84:
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
                    return False  # 陀螺仪数据不对
            else:
                messagebox.showinfo("程序中未加入该命令!")
                return True  # 未加入命令的话没必要再执行了

        else:
            return False  # 接收到的数据首不为0x68,重新接收,在这个程序不可能出现这种情况

        return True  # 正常执行完0x68为首的命令后,不需要再重复执行该命令了

    else:
        return False  # 接收到的数据不完整


def Attitude_algorithm_9(roll_raw, pitch_raw, yaw_raw,
                         acc_x_raw, acc_y_raw, acc_z_raw,
                         grop_x_raw, grop_y_raw, grop_z_raw):
    global roll, pitch, yaw, acc_x, acc_y, acc_z, grop_x, grop_y, grop_z
    roll = BCDtoINT(roll_raw) * 0.01
    pitch = BCDtoINT(pitch_raw) * 0.01
    yaw = BCDtoINT(yaw_raw) * 0.01
    acc_x = BCDtoINT(acc_x_raw) * 0.001
    acc_y = BCDtoINT(acc_y_raw) * 0.001
    acc_z = BCDtoINT(acc_z_raw) * 0.001
    grop_x = BCDtoINT(grop_x_raw) * 0.01
    grop_y = BCDtoINT(grop_y_raw) * 0.01
    grop_z = BCDtoINT(grop_z_raw) * 0.01
    GUI_9role.geometry('660x150')
    roll_label = tk.Label(GUI_9role, text="横滚角(ROLL): %f°" % roll)
    pitch_label = tk.Label(GUI_9role, text="俯仰角(PITCH):%f°" % pitch)
    yaw_label = tk.Label(GUI_9role, text="航向角(YAW):%f°" % yaw)
    acc_x_label = tk.Label(GUI_9role, text="X轴加速度(ACCX):%fg" % acc_x)
    acc_y_label = tk.Label(GUI_9role, text="Y轴加速度(ACCY):%fg" % acc_y)
    acc_z_label = tk.Label(GUI_9role, text="Z轴加速度(ACCZ):%fg" % acc_z)
    grop_x_label = tk.Label(GUI_9role, text="X轴角速率(Groy x):%f°/s" % grop_x)
    grop_y_label = tk.Label(GUI_9role, text="Y轴角速率(Groy y):%f°/s" % grop_y)
    grop_z_label = tk.Label(GUI_9role, text="Z轴角速率(Groy z):%f°/s" % grop_z)
    roll_label.place(x=20, y=30)
    pitch_label.place(x=20, y=60)
    yaw_label.place(x=20, y=90)
    acc_x_label.place(x=220, y=30)
    acc_y_label.place(x=220, y=60)
    acc_z_label.place(x=220, y=90)
    grop_x_label.place(x=450, y=30)
    grop_y_label.place(x=450, y=60)
    grop_z_label.place(x=450, y=90)


def Attitude_algorithm_3(grop_z_raw, acc_y_raw, yaw_raw):
    global grop_z, acc_y, yaw
    grop_z = BCDtoINT(grop_z_raw) * 0.01
    acc_y = BCDtoINT(acc_y_raw) * 0.001
    yaw = BCDtoINT(yaw_raw) * 0.01
    GUI_3role.geometry('250x150')
    grop_z_label = tk.Label(GUI_3role, text="Z轴角速率(Groy z):%f°/s" % grop_z)
    acc_y_label = tk.Label(GUI_3role, text="Y轴加速度(ACCY):%fg" % acc_y)
    yaw_label = tk.Label(GUI_3role, text="航向角(YAW):%f°" % yaw)
    grop_z_label.place(x=25, y=30)
    acc_y_label.place(x=25, y=60)
    yaw_label.place(x=25, y=90)


def set_3role():
    execute_cmd(set_mpu_default)


def set_9role():
    execute_cmd(set9mpu)


def clear_mpu_data():
    execute_cmd(clear_Sensor_angle)


def read_mpu_data():
    execute_cmd(Get_angle)
    global timer
    timer = threading.Timer(0.04, read_mpu_data)
    timer.start()


ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

setBaudrate_9600 = bytes.fromhex('6805000B0212')    # sensor_baudrate
setBaudrate_115200 = bytes.fromhex('6805000B0515')
# setBaudrate_115200    为bytes类型的b'h\x05\x00\x0b\x05\x15'
# setBaudrate_115200[0] 是int型的104,为68的十进制,ascii码值对应的字符为h
clear_Sensor_angle = bytes.fromhex('680400282C')  # 方位角清零命令
clear_Sensor_acc = bytes.fromhex('680400272C')  # 清除异常加速度
set9mpu = bytes.fromhex('680500FD7072')  # 9 轴输出
set_mpu_default = bytes.fromhex('680500FD7173')  # 标准格式 1 输出（Z 轴角速率+前进（Y 轴）加速度+Z 轴航向角
Get_angle = bytes.fromhex('6804000408')  # 同时读角度命令


GUI_Programme = tk.Tk()
GUI_Programme.title(' TL740D陀螺转角仪')  # 定义窗体标题
GUI_Programme.geometry('220x200')        # 定义窗体的大小，是400X200像素

read_mpu_data_button = tk.Button(GUI_Programme, text='读取陀螺仪数据', comman=read_mpu_data)
read_mpu_data_button.pack(side=tk.TOP)
set_9role_button = tk.Button(GUI_Programme, text='设置9轴输出', comman=set_9role)
set_9role_button.pack(side=tk.TOP)
set_3role_button = tk.Button(GUI_Programme, text='设置标准输出', comman=set_3role)
set_3role_button.pack(side=tk.TOP)
clear_mpu_data_button = tk.Button(GUI_Programme, text='方位角清零', comman=clear_mpu_data)
clear_mpu_data_button.pack(side=tk.TOP)
GUI_Programme.quitButton = tk.Button(GUI_Programme, text='Quit', command=GUI_Programme.quit)
GUI_Programme.quitButton.pack(side=tk.BOTTOM)

global GUI_9role
var_window = tk.IntVar(GUI_Programme, value=0)
if var_window.get() == 0:
    var_window.set(1)
    GUI_9role = tk.Toplevel(GUI_Programme, width=660, height=150)
    GUI_9role.title('9轴输出')
    GUI_9role.attributes('-topmost', 1)  # 窗口总在最前
    var_window.set(0)

global GUI_3role
var_window2 = tk.IntVar(GUI_Programme, value=0)
if var_window2.get() == 0:
    var_window2.set(1)
    GUI_3role = tk.Toplevel(GUI_Programme, width=200, height=150)
    GUI_3role.title('3轴输出')
    GUI_3role.attributes('-topmost', 1)  # 窗口总在最前
    var_window.set(0)


tk.mainloop()
