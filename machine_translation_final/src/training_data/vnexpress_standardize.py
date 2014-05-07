'''
Created on May 4, 2014

@author: Tuan
'''
import codecs
import glob

import nltk.tokenize
from nltk.tokenize.treebank import TreebankWordTokenizer

from src import VNEXPRESS_DATA_DIRECTORY
from src.training_data.crawler import TITLE_NEWS, SHORT_INTRO, CONTENT_TEXT, \
    DATA_EXT
import xml.etree.ElementTree as ET


STANDARD_EXT = '.std'

class VnExpressStandardizer():
    '''
    Standardize the data in vnexpress into files with
    tokenizing sentences, separating quote, comma and end of sentence dot.
    '''

    def __init__(self):
        self.input_data_directory = VNEXPRESS_DATA_DIRECTORY
        self.output_data_directory = VNEXPRESS_DATA_DIRECTORY
        self.load_files()
    
    def load_files(self):
        self.data_files = glob.glob(self.input_data_directory + '\\*.data')
    
    def process_all_files(self):
        for file_name in self.data_files:
            print file_name
            self.process_all_contents(file_name)
    
    def process_all_contents(self, file_name ):
        with codecs.open(file_name, 'r', 'utf-8') as in_file_handler:
            content_buffer = ''
            for line in in_file_handler:
                content_buffer += line
            root = ET.fromstring(content_buffer)
            articles = root.findall('article')
            all_contents = []
            for article in articles:
                title_news = self.sentence_tokenize(article.find(TITLE_NEWS).text)
                short_intro = self.sentence_tokenize(article.find(SHORT_INTRO).text)
                content_text = self.sentence_tokenize(article.find(CONTENT_TEXT).text)
                all_content = '\n'.join([title_news, short_intro, content_text])
                all_contents.append(all_content)
        
        articles_per_file = 10
        for i in xrange(len(all_contents) / articles_per_file):
            begin = articles_per_file * i
            end = min(articles_per_file * (i + 1), len(all_contents))
            output_file_name = file_name[:-len(DATA_EXT)] + '.%s'%i + STANDARD_EXT
            with codecs.open(output_file_name, 'w', 'utf-8') as out_file_handler:    
                out_file_handler.write('\n'.join(all_contents[begin:end]))
            
    def sentence_tokenize(self, text):
        if text == None:
            return ''
        sentences = nltk.tokenize.sent_tokenize(text.strip())
        new_text = '\n'.join([' '.join(TreebankWordTokenizer().tokenize(sentence.strip())) for sentence in sentences])
        return new_text
        
    