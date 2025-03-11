import logging
import os
from itertools import count
import time
import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from DLMS_SPODES.cosem_interface_classes.parameter import Parameter


class TestType(unittest.TestCase):

    def test_init(self):
        par = Parameter(b'123467\x00\x01')
        par.validate()
        self.assertEqual(par.i, 1)
        print(par)

    def test_append_pop(self):
        par = Parameter(b'123467\x008')
        new_par = par.append(1)
        new_par = new_par.append(2)
        new_par = new_par.append(300)
        new_par = new_par.set_piece(1)
        self.assertEqual(new_par.pop(), (1, 300, Parameter(b'123467\x008').extend(1, 2)))
        self.assertEqual(new_par[1], 2)
        print(new_par)
        for el in new_par.elements():
            print(el)

    def test_in(self):
        l = [Parameter(b'12345678'), Parameter(b'12345679')]
        z = Parameter(b'12345678')
        self.assertEqual(z in l, True)

    def test_dict(self):
        l = {Parameter(b'12345678'): 1, Parameter(b'12345679'): 2}
        l.pop(Parameter(b'12345678'))
        self.assertEqual(len(l), 1)

    def test_extend(self):
        par = Parameter(b'012345').set_i(6)
        new_par = par.extend(1, 2)
        self.assertEqual(new_par, Parameter(b'012345\x00\x06\x00\x01\x00\x02'))

    def test_i(self):
        par = Parameter(b'0123456')
        a_par = par.set_i(1, True)
        self.assertEqual(a_par.i, 1)
        a_par = par.set_i(10)
        self.assertEqual(a_par.i, 10)
        print(par in a_par)

    def test_elements(self):
        par = Parameter(b'1234678').set_i(2).extend(1, 2, 3)
        print(tuple(par.elements()))
        for i in par.elements(2):
            print(i)

    def test_piece(self):
        par = Parameter(b'1234678').set_i(2)
        par = par.set_piece(4)
        par = par.clear_piece()
        par.append(1)
        print(par)

    def test_n_element(self):
        par = Parameter(b'1234678').set_i(2).extend(1, 2, 3)
        self.assertEqual(par.n_elements, 3)

    def test_last_element(self):
        par = Parameter(b'1234678').set_i(2).extend(1, 2, 3)
        self.assertEqual(par.last_element, 3)
        par.set_piece(4)
        self.assertEqual(par.last_element, 3)