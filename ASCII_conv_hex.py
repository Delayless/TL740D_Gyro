class Converter:
    @staticmethod
    # 比如这里实参只能是不包含前导符0x的十六进制数(0-F)的字符串,如'6805000B0212'
    # 可以转换成以这些十六进制数为ASCII码值所对应的字符串返回
    def hex_to_ascii(h):
        """
        转换成ASCII码值对应的字符串
        这次使用我是将字符串'6805000B0212'转换,其中的68转换成h
        因为68对应的十进制为104
        104对应的ascii字符为h
        :return str类型: h (,
        """
        list_s = []
        # i每次增长2,len为字符串长度
        for i in range(0, len(h), 2):
            # upper()是转换为大写
            # append()是在方法用于在列表(List)末尾添加新的对象
            list_s.append(chr(int(h[i:i+2].upper(), 16)))

        return ''.join(list_s)

    @staticmethod
    def str_to_hexstr(s):
        list_h = []
        for c in s:
            # ord()返回单个字符的ASCII码值,如字符a返回的是97
            list_h.append(str(hex(ord(c)))[-2:])  # 取hex转换16进制的后两位

        return ''.join(list_h)


"""
a1 = Converter.hex_to_ascii('6805000B0212')
b1 = a1.encode()
decode_b1 = b1.decode()
# 跟上面一样的效果
a2 = '\x68\x05\x00\x0B\x02\x12'
b2 = a2.encode()

d1 = Converter.str_to_hex(a1)
c2 = bytes.fromhex('6805000B0212')
d2 = bytes.hex(c2)

e = a1
print(a1)
"""
a = b'h'
b = b'h\x69'
c = b[1:] == b'i'

a = chr(68)

a = Converter.str_to_hexstr('hi')
a = '680400282C'
b = a.encode()

clear_Sensor_angle = bytes.hex(b'h')
b = clear_Sensor_angle.encode()

a = 'h' + 'ello'
b = a.encode()
c = 'hello'
d = c.encode()
e = b'h\x02\x1f'

i = 2

f = b'\x02\x1f'
g = b'h'
h = g + f

