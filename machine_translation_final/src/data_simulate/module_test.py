# -*- coding: utf-8 -*-
'''
Created on May 3, 2014

@author: Tuan
'''
import os
import unittest

from src import VN_LANGUAGE, DATA_DIRECTORY
from src.data_simulate.diacritic_handler import DiacriticHandler


class Test(unittest.TestCase):
    def setUp(self):
        self.diacritic_handler = DiacriticHandler(VN_LANGUAGE);

    def tearDown(self):
        pass
    
    def test_remove_diacritics(self):
        self.assertEqual("Tuan", self.diacritic_handler.remove_diacritics("Tuấn"))
        self.assertEqual("Toi dang di an", self.diacritic_handler.remove_diacritics("Tôi đang đi ăn"))
        self.assertEqual("Toi nay ngu o dau", self.diacritic_handler.remove_diacritics("Tối nay ngủ ở đâu"))
        self.assertEqual("Dong Da", self.diacritic_handler.remove_diacritics("Đống Đa"))
        self.assertEqual("NGA BA DONG LOC", self.diacritic_handler.remove_diacritics("NGÃ BA ĐỒNG LỘC"))
    
    def test_load_code_map(self):
        self.diacritic_handler.load_code_map(VN_LANGUAGE)
        
    def test_get_diacritic_forms(self):
        diacritic_forms = self.diacritic_handler.get_diacritic_forms('Tuan')
        print len(diacritic_forms)
        for diacritic_form in diacritic_forms:
            print diacritic_form
    
    def test_check_vowels(self):
        self.diacritic_handler.check_vowels('Tuan')
        
    def test_get_acceptable_forms(self):
        forms = self.diacritic_handler.get_acceptable_forms('Tuan')
        self.assertEquals(set([u'T\u1eeban', u'T\u1eefan', u'T\u1ee9an', 
                          u'T\u1eedan', u'T\u1ef1an', u'T\u01b0an', 
                          u'Tu\u1ea7n', u'Tu\u1eabn', u'Tu\u1ea5n', 
                          u'Tu\u1ea9n', u'Tu\u1eadn', u'Tu\xe2n', 
                          u'T\u1ee7an', u'T\u0169an', u'T\u1ee5an', 
                          u'T\xf9an', u'T\xfaan', u'Tuan']), set(forms))
        forms = self.diacritic_handler.get_acceptable_forms('Tun')
        self.assertTrue(set([u'T\u1eebn', u'T\u1eefn', u'T\u1ee9n', 
                              u'T\u1eedn', u'T\u1ef1n', u'T\u01b0n', 
                              u'T\u1ee7n', u'T\u0169n', u'T\u1ee5n', 
                              u'T\xf9n', u'T\xfan', u'Tun']), set(forms) )
        print 'Tueen'
        forms = self.diacritic_handler.get_acceptable_forms('Tueen')
        for form in forms:
            print form
        print 'Tuyet'
        forms = self.diacritic_handler.get_acceptable_forms('Tuyet')
        for form in forms:
            print form
        print 'gioi'
        forms = self.diacritic_handler.get_acceptable_forms('gioi')
        for form in forms:
            print form
    
    def test_make_non_diacritic_file(self):
        input_file = os.path.join(DATA_DIRECTORY, 'segment_data_test' , 'vnexpress_61.0.std.wseg')
        output_file = os.path.join(DATA_DIRECTORY, 'segment_data_test' , 'vnexpress_61.0.std.wseg.nodiac')
        self.diacritic_handler.make_non_diacritic_file(input_file, output_file)
        
    def test_make_non_diacritic_files(self):
        input_directory = os.path.join(DATA_DIRECTORY, 'segment_data_test')
        output_directory = os.path.join(DATA_DIRECTORY, 'data_test_nondiac')
        self.diacritic_handler.make_non_diacritic_files(input_directory, output_directory)
        
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
