# -*- coding: utf-8 -*-
'''
Created on May 3, 2014

@author: Tuan
'''
import os
import unittest

from src import VNEXPRESS_DATA_DIRECTORY
from src.training_data.vnexpress_crawler import VnExpressCrawler
from src.training_data.vnexpress_standardize import VnExpressStandardizer


class Test(unittest.TestCase):

    def setUp(self):
        self.vnexpress_crawler = VnExpressCrawler()
        self.vnexpress_standardizer = VnExpressStandardizer()

    def test_get_sub_pages(self):
        self.vnexpress_crawler.get_sub_pages()
         
    def test_get_last_page(self):
        self.vnexpress_crawler.get_last_page("http://kinhdoanh.vnexpress.net/tin-tuc/hang-hoa")
     
    def test_get_articles_links_single_page(self):
        self.vnexpress_crawler.get_articles_links_single_page('http://kinhdoanh.vnexpress.net/tin-tuc/hang-hoa/page/1.html')
 
    def test_get_article_links(self):
        self.vnexpress_crawler.get_article_links()
 
    def test_get_articles(self):
        self.vnexpress_crawler.get_articles()

    def test_process(self):
        text = '''Cựu Bộ trưởng Quốc phòng Mỹ đặt ngay một câu hỏi chắc chắn đã làm ông băn khoăn suốt 30 năm.
        "Đến ngày hôm nay, tôi vẫn không biết điều gì đã xảy ra vào ngày 2/8 và ngày 4/8/1964, tại Vịnh Bắc Bộ. Tôi nghĩ chúng ta đã có hai đánh giá sai lầm nghiêm trọng... Liệu sự kiện mà chúng tôi gọi là cuộc tấn công thứ hai vào ngày 4/8/1964, nó có xảy ra không?", ông nói với Tướng Giáp. 
        "Vào ngày 4/8, hoàn toàn chẳng có gì xảy ra cả", Tướng Giáp đáp.
        '''
        new_text = self.vnexpress_standardizer.process(text)
        print new_text

    def test_process_all_contents(self):
        path = os.path.join(VNEXPRESS_DATA_DIRECTORY, 'vnexpress_0.data')
        self.vnexpress_standardizer.process_all_contents(path)
        
    def test_process_all_files(self):
        self.vnexpress_standardizer.process_all_files()
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()