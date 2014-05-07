'''
Created on May 4, 2014

@author: Tuan
'''
import codecs
from collections import defaultdict
import glob
import json
import math
import os
import time

from src import WORD_SEGMENTED_EXT, FILE_CODEC, BEGIN_TAG, INSIDE_TAG
from src.util.util import Utils


UNIGRAM_HISTOGRAM = 'unigram_histogram'
BIGRAM_HISTOGRAM = 'bigram_histogram'
UNIGRAM_SUM = 'unigram_sum'
BIGRAM_SUM = 'bigram_sum'
ZERO_GRAM_VAL = 'zero_gram_val'
BI_COEFF = 'bi_coefficient'
UNI_COEFF = 'uni_coefficient'
ZERO_COEFF = 'zero_coefficient'

class LanguageModelTrainer(object):
    '''
    Train language model given a set of training files
    '''

    def __init__(self, training_data_directory=None, **kwargs):
        '''
        Constructor
        '''
        self.training_data_directory = training_data_directory
        
        if ZERO_GRAM_VAL in kwargs:
            self.zero_gram_val = kwargs[ZERO_GRAM_VAL]
        else:
            self.zero_gram_val = 0.0000001
        
        if BI_COEFF in kwargs:
            self.bi_coefficient = kwargs[BI_COEFF]
        else:
            self.bi_coefficient = 0.9
            
        if UNI_COEFF in kwargs:
            self.uni_coefficient = kwargs[UNI_COEFF]
        else:
            self.uni_coefficient = 0.09
        
        if ZERO_COEFF in kwargs:
            self.zero_coefficient = kwargs[ZERO_COEFF]
        else:
            self.zero_coefficient = 0.01
            
    def read_training_data(self):
        self.training_data = {}
        for file_name in glob.glob(os.path.join(self.training_data_directory, '*' + 
                                                WORD_SEGMENTED_EXT)):
            print file_name
            with codecs.open(file_name, 'r', FILE_CODEC) as file_handler:
                sentences = []
                for line in file_handler:
                    sentences.append(line.strip())
                file_sentence_words = Utils.bracket_to_array_form(sentences)
                self.training_data[file_name] = file_sentence_words
    
    def build_language_model(self):
        self.calculate_unigram()
        self.calculate_bigram()
        self.smooth_model()
        
    def calculate_unigram(self):
        self.unigram_histogram = defaultdict(int)
        self.unigram_sum = 0
        for file_name in self.training_data:
            file_sentence_words = self.training_data[file_name]
            for sentence_words in file_sentence_words:
                for i in xrange(len(sentence_words)):
                    word = sentence_words[i]
                    for j in xrange(len(word)):
                        token = word[j]
                        if  j == 0:
                            self.unigram_histogram[(token , BEGIN_TAG)] += 1
                        else:
                            self.unigram_histogram[(token , INSIDE_TAG)] += 1
                        self.unigram_sum += 1
        
    def calculate_bigram(self):
        self.bigram_histogram = defaultdict(int)
        self.bigram_sum = defaultdict(int)
        
        for file_name in self.training_data:
            file_sentence_words = self.training_data[file_name]
            for sentence_words in file_sentence_words:
                token_list = Utils.word_to_tokens_form(sentence_words)
                for i in xrange(len(token_list)):
                    token = token_list[i][0]
                    seg_tag = token_list[i][1]
                    if i == 0:
                        self.bigram_histogram[(None, None, token, seg_tag)] += 1
                        self.bigram_sum[(None, None)] += 1
                    else:
                        prev_token = token_list[i - 1][0]
                        prev_seg_tag = token_list[i - 1][1]
                        self.bigram_histogram[(prev_token, prev_seg_tag, token, seg_tag)] += 1
                        self.bigram_sum[(prev_token, prev_seg_tag)] += 1
    
    def smooth_model(self):
        '''
        Smooth the unigram and bigram a little bit
        '''
        for token, seg_tag in self.unigram_histogram:
            self.unigram_histogram[(token, seg_tag)] += 1
            self.unigram_sum += 1
        for prev_token, prev_seg_tag, token, seg_tag in self.bigram_histogram:
            self.bigram_histogram[(prev_token, prev_seg_tag, token, seg_tag)] += 1
            self.bigram_sum[(prev_token, prev_seg_tag)] += 1
        
    def save_model(self, file_name):
        with codecs.open(file_name, 'w', FILE_CODEC) as file_handler:
            self.create_str_models()
            
            json.dump({UNIGRAM_HISTOGRAM: self.str_unigram_histogram,
                       BIGRAM_HISTOGRAM: self.str_bigram_histogram,
                       UNIGRAM_SUM: self.unigram_sum,
                       BIGRAM_SUM: self.str_bigram_sum},
                      file_handler,
                      encoding=FILE_CODEC)
    
    def create_str_models(self):
        self.str_unigram_histogram = {}
        for key in self.unigram_histogram:
            self.str_unigram_histogram['\t'.join(key)] = self.unigram_histogram[key]
        
        self.str_bigram_histogram = {}
        for key in self.bigram_histogram:
            try:
                self.str_bigram_histogram['\t'.join(key)] = self.bigram_histogram[key]
            except TypeError:
                self.str_bigram_histogram['\t'.join(self.get_modified_key(key))] = \
                                                self.bigram_histogram[key]
            
        self.str_bigram_sum = {}
        for key in self.bigram_sum:
            try:
                self.str_bigram_sum['\t'.join(key)] = self.bigram_sum[key]
            except TypeError:
                self.str_bigram_sum['\t'.join(self.get_modified_key(key))] = \
                                                self.bigram_sum[key]
    
    def get_modified_key(self, key):
        modified_key = []
        for t in key:
            if t == None:
                '''
                None is conversed to space
                '''
                modified_key.append(' ')
            else:
                modified_key.append(t)
        return modified_key
    
    def get_real_key(self, modified_key):
        key = []
        for t in modified_key.split('\t'):
            '''
            Space converted back to Non 
            '''
            if t == ' ':
                key.append(None)
            else:
                key.append(t)
        return tuple(key)
    
    def load_model(self, file_name):
        t = time.time()
        with codecs.open(file_name, 'r', FILE_CODEC) as file_handler:
            models = json.load(file_handler, FILE_CODEC)
            self.str_unigram_histogram = models[UNIGRAM_HISTOGRAM]
            self.str_bigram_histogram = models[BIGRAM_HISTOGRAM]
            self.unigram_sum = models[UNIGRAM_SUM]
            self.str_bigram_sum = models[BIGRAM_SUM]
            print self.unigram_sum
            
            self.unigram_histogram = {}
            self.bigram_histogram = {}
            self.bigram_sum = {}
            for modified_key in self.str_unigram_histogram:
                self.unigram_histogram[self.get_real_key(modified_key)] =\
                         self.str_unigram_histogram[modified_key]
                         
            for modified_key in self.str_bigram_histogram:
                self.bigram_histogram[self.get_real_key(modified_key)] =\
                         self.str_bigram_histogram[modified_key]
                         
            for modified_key in self.str_bigram_sum:
                self.bigram_sum[self.get_real_key(modified_key)] =\
                         self.str_bigram_sum[modified_key]
        
        print 'Time to load model :%s seconds' %(time.time() - t)
        
    def query(self, prev_token, prev_seg, cur_token, cur_seg):
        '''
        prev_token = previous token 
        prev_seg = 'B' | 'I'
        cur_token = current token
        cur_seg = 'B' | 'I'
        return probability P ( current token and segment tag| previous token and segment tag )
        '''
        unigram_val = 0
        if (cur_token, cur_seg) in self.unigram_histogram:
            unigram_val = float(self.unigram_histogram[(cur_token, cur_seg)])\
                         / self.unigram_sum
        bigram_val = 0
        if (prev_token, prev_seg, cur_token, cur_seg) in self.bigram_histogram:
            if (self.bigram_sum[(prev_token, prev_seg)] != 0):
                bigram_val = float(self.bigram_histogram[(prev_token, prev_seg, cur_token, cur_seg)])\
                        / self.bigram_sum[(prev_token, prev_seg)]
        val = unigram_val * self.uni_coefficient + \
         bigram_val * self.bi_coefficient + \
         self.zero_gram_val * self.zero_coefficient
        return val
    
    def query_log(self, prev_token, prev_seg, cur_token, cur_seg):
        return math.log(self.query(prev_token, prev_seg, cur_token, cur_seg))
