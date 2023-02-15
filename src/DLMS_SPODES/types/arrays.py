""" COMMON Arrays """
from types import common_data_types as cdt


class Integer(cdt.Array):
    """ Array of Integer """
    TYPE = cdt.Integer


if __name__ == '__main__':
    a = Integer([1,2,3])
    a = Integer(b'\x01\x02\x0f\x0f\x0f\x03')
    a.append('d')
    b = a.decode()
    a.clear()
    print(b)
