import unittest
from collections import OrderedDict
from run_nlp import get_values_from_od_of_od, set_values_for_od_of_od


class Test_run_nlp(unittest.TestCase):

    a_dict = {
        'x': {
            'a': [1, 2],
            'b': [3, 4],
            'c': [5, 6]
        },
        'y': {
            'd': [7, 8],
            'e': [9, 10],
            'f': [11, 12]
        },
        'z': {
            'g': [13, 14],
            'h': [15, 16],
            'i': [17, 18]
        },
    }

    b = list(range(1, 19))

    def test_get_values_from_od_of_od(self):
        """ Ensure that get_values_from_od_of_od() works for OrderedDict
        """
        a = OrderedDict([
            ('x', OrderedDict([('a', [1, 2]), ('b', [3, 4]), ('c', [5, 6])])),
            ('y', OrderedDict([('d', [7, 8]), ('e', [9, 10]), ('f', [11,
                                                                     12])])),
            ('z',
             OrderedDict([('g', [13, 14]), ('h', [15, 16]), ('i', [17, 18])])),
        ])

        self.assertEqual(get_values_from_od_of_od(a), self.b)

    def test_get_values_from_od_of_od_2(self):
        """
        Ensure that get_values_from_od_of_od() works for standard Dict in
        python 3.6+  If this test fails, please upgrade python version.
        Scripts will run, but cannot guarantee to be error free.
        """
        self.assertEqual(get_values_from_od_of_od(self.a_dict), self.b)

    def test_set_values_for_od_of_od(self):
        """ Ensure that set_values_for_od_of_od() works
        """
        # b is a list from 18 to 1 inclusive
        a_dict_reverse = {
            'x': {
                'a': [18, 17],
                'b': [16, 15],
                'c': [14, 13]
            },
            'y': {
                'd': [12, 11],
                'e': [10, 9],
                'f': [8, 7]
            },
            'z': {
                'g': [6, 5],
                'h': [4, 3],
                'i': [2, 1]
            },
        }
        b_reverse = list(range(1, 19))[::-1]
        # print(set_values_for_od_of_od(self.a_dict, b_reverse))
        self.assertEqual(set_values_for_od_of_od(self.a_dict, b_reverse),
                         a_dict_reverse)


if __name__ == '__main__':
    unittest.main()
