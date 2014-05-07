# -*- coding: utf-8 -*-
'''
Created on May 4, 2014

@author: Tuan
'''
import os
import unittest

from src import SEGMENT_TRAIN
from src.train.language_model_train import LanguageModelTrainer


class Test(unittest.TestCase):


    def setUp(self):
        self.model_trainer = LanguageModelTrainer(SEGMENT_TRAIN)

    def testProcess(self):
        sample_text = ['''
        [Trao đổi] [với] [VnExpress] , [Phó] [tổng thanh tra] [Chính phủ] [Mai Quốc Bình] 
        [cho biết] , [đơn vị] [này] [đã] [báo cáo] [Thủ tướng] [kết luận] [thanh tra] [tại] 
        [Ngân hàng] [nhà nước] . 
        ''']
        self.model_trainer.process(sample_text)
    
    def test_build_language_model(self):
        self.model_trainer.read_training_data()
        self.model_trainer.build_language_model()
        self.model_trainer.save_model(os.path.join(SEGMENT_TRAIN, 't1-60.model'))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testProcess']
    unittest.main()