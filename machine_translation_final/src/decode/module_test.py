# -*- coding: utf-8 -*-
'''
Created on May 5, 2014

@author: Tuan
'''
import codecs
import os
import unittest

from src import  DATA_DIRECTORY, FILE_CODEC
from src.decode.decoder import Decoder


class Test(unittest.TestCase):
    
    def setUp(self):
        model_file_name = os.path.join(DATA_DIRECTORY, 't1-60.model')
        input_directory = os.path.join(DATA_DIRECTORY, 'data_test_nondiac')
        output_directory = os.path.join(DATA_DIRECTORY, 'data_test_result')
        emission_file = os.path.join(DATA_DIRECTORY, 'abbreviation.txt')
        self.decoder = Decoder(model_file_name, input_directory, 
                               output_directory, emission_file)

    def test_decode(self):
        text_sample = 'a yeu e rat nhieu'
        text_sample_tokens = text_sample.split(' ')
        decoded_tokens = self.decoder.decode(text_sample_tokens)
        with codecs.open(os.path.join(DATA_DIRECTORY, 'abc.txt'), 'w', FILE_CODEC) as file_handler:
            for decoded_token in decoded_tokens:
                file_handler.write(' '.join(decoded_token))
    
    def test_decode_all(self):
        self.decoder.decode_all()
        
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
