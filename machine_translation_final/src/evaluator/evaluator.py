# -*- coding: utf-8 -*-
'''
Created on May 5, 2014

@author: Tuan
'''
import codecs
import glob
import json
import os

from src import WORD_SEGMENTED_EXT, FILE_CODEC, NON_DIA_EXT, DECODED_EXT, \
    TOKEN_INDEX, TAG_INDEX
from src.util.util import Utils


class Evaluator():
    '''
    Evaluate the result from decoding
    '''

    def __init__(self, gold_directory, result_directory):
        '''
        Parameters:
            - gold_directory: testing data, have the same format as training data.
                Each line is one segmented sentence: 
                Example: [Thực phẩm] , [trái cây] [siêu thị] [rẻ] [hơn] [chợ] 
            - result_directory: result from decoding, have the same format as training data.
                Example: [Thực] [phẩm] , [trai cây] [siêu thị] [rẻ] [hơn] [chợ]
        '''
        self.gold_directory = gold_directory
        self.result_directory = result_directory
        self.load_data_files()
    
    def load_data_files(self):
        self.gold_data = {}
        self.result_data = {}
        for gold_file_name in glob.glob(os.path.join(self.gold_directory, '*' + 
                                                WORD_SEGMENTED_EXT)):
            with codecs.open(gold_file_name, 'r', FILE_CODEC) as file_handler:
                sentences = []
                for line in file_handler:
                    sentences.append(line.strip())
                sentence_words = Utils.bracket_to_array_form(sentences)
                rel_gold_file_name = gold_file_name.split(os.path.sep)[-1][:-len(WORD_SEGMENTED_EXT)]
                self.gold_data[rel_gold_file_name] = sentence_words
        
        for rel_gold_file_name in self.gold_data:
            result_file_name = os.path.join(self.result_directory,
                                            rel_gold_file_name +
                                            WORD_SEGMENTED_EXT + 
                                            NON_DIA_EXT + DECODED_EXT)
            with codecs.open(result_file_name, 'r', FILE_CODEC) as file_handler:
                sentence_words = json.load(file_handler, FILE_CODEC)
                self.result_data[rel_gold_file_name] = sentence_words
        
    def calculate_precision(self):
        '''-------------------------------------------------
        The metric for calculating of precision:
        Counting the number of token that is at the right tag_position (B or I),
        and have exact diacritic form
        ----------------------------------------------------
        '''
        self.no_of_tokens = 0
        self.no_of_matching_token = 0
        self.no_of_matching_recovering = 0
        self.no_of_matching_segment_tag = 0
        
        for rel_gold_file_name in self.gold_data:
            print rel_gold_file_name
            gold_sentence_words = self.gold_data[rel_gold_file_name]
            result_sentence_words = self.result_data[rel_gold_file_name]
            for gold_sentence_word, result_sentence_words in zip(gold_sentence_words, result_sentence_words):
                '''
                Gold data need to be converted
                '''
                gold_token_list = Utils.word_to_tokens_form(gold_sentence_word)
                '''
                Result data doesn't need to be converted
                '''
                result_token_list = result_sentence_words
                for gold_token, result_token in zip(gold_token_list, result_token_list):
                    self.no_of_tokens += 1
                    
                    same_token = gold_token[TOKEN_INDEX] == result_token[TOKEN_INDEX]
                    same_tag = gold_token[TAG_INDEX] == result_token[TAG_INDEX]
                    if same_token:
                        self.no_of_matching_recovering += 1
                    if same_tag:
                        self.no_of_matching_segment_tag += 1
                    if same_token and same_tag:
                        self.no_of_matching_token += 1
        self.print_result()
        
    def print_result(self):
        print '-----------------------------------------------------------'
        print 'Precision: %s percent' % (100 * self.no_of_matching_token/ self.no_of_tokens)
        print 'Precision of recovering: %s percent' % (100 * self.no_of_matching_recovering/ self.no_of_tokens)
        print 'Precision of segmentation: %s percent' % (100 * self.no_of_matching_segment_tag/ self.no_of_tokens)
        print '-----------------------------------------------------------'