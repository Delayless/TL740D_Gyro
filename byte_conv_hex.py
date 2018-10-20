import unittest

if __name__ == '__main__':
    a = '55'
    a_bytes = bytes.fromhex(a)
    print(type(a_bytes))  # byte b'\x15'
    aa = a_bytes.hex()
    print('after convert:', type(aa))
    print(aa)   # str 15
    print(int(aa)+6)
