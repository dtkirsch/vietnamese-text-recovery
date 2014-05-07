# -*- coding: utf-8 -*
'''
Created on May 5, 2014

@author: Tuan
'''
import os
import unittest

from evaluator import Evaluator
from src import DATA_DIRECTORY

class Test(unittest.TestCase):


    def setUp(self):
        gold_directory = os.path.join(DATA_DIRECTORY, 'segment_data_test')
        result_directory = os.path.join(DATA_DIRECTORY, 'data_test_result')
        self.evaluator = Evaluator(gold_directory, result_directory)


    def test_calculate_precision(self):
        self.evaluator.calculate_precision()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()