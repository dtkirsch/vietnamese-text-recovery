'''
Created on May 4, 2014

@author: Tuan
'''

import codecs
import glob
import json
import os

from src import VN_LANGUAGE, WORD_SEGMENTED_EXT, NON_DIA_EXT, DECODED_EXT, \
    FILE_CODEC, BEGIN_TAG, INSIDE_TAG, TOKEN_INDEX, TAG_INDEX, VAL_INDEX, \
    TRACE_INDEX
from src.data_simulate.diacritic_handler import DiacriticHandler
from src.emission.emission import EmissionProb
from src.train.language_model_train import LanguageModelTrainer


MAX_NO_OF_AVAILABLE = 100
class Decoder(object):
    '''
    Decode and segment a non-diacritic sentence into diacritic forms
    '''

    def __init__(self, model_file_name, 
                 input_directory = None, 
                 output_directory = None, 
                 emission_file = None):
        '''-------------------------------------------------
        Parameters
        - model_file_name: the absolute path of the model file
        - input_directory: 
        - output_directory:
        - emission_file: abbreviation file indeed:
            The format is fullform \t shortenedform \t probability \t translation
        ------------------------------------------------- 
        '''
        self.input_directory = input_directory
        self.output_directory = output_directory
        self.diacritic_handler = DiacriticHandler(VN_LANGUAGE)
        self.emission_prob = EmissionProb(emission_file)
        self.language_model = LanguageModelTrainer()
        self.language_model.load_model(model_file_name)
        if input_directory != None:
            self.load_input_data()
    
    def decode_all(self):
        '''-------------------------------------------------
        Decode all files from input_directory into output_directory
        ------------------------------------------------- 
        '''
        self.load_input_data()
        for rel_file_name in self.test_data:
            print rel_file_name
            file_sentence_tokens = self.test_data[rel_file_name]
            files_decoded_sentence_tokens = []
            for sentence_tokens in file_sentence_tokens:
                decoded_sentence_tokens = self.decode(sentence_tokens)
                files_decoded_sentence_tokens.append(decoded_sentence_tokens)
            
            output_file_name = os.path.join(self.output_directory, rel_file_name + 
                                                WORD_SEGMENTED_EXT + NON_DIA_EXT + DECODED_EXT)
            with codecs.open(output_file_name, 'w', FILE_CODEC) as file_handler:
                json.dump(files_decoded_sentence_tokens, file_handler, encoding=FILE_CODEC)
                
    def load_input_data(self):
        self.test_data = {}
        for test_file_name in glob.glob(os.path.join(self.input_directory, '*' + 
                                                WORD_SEGMENTED_EXT + NON_DIA_EXT)):
            with codecs.open(test_file_name, 'r') as file_handler:
                file_sentence_tokens = []
                for line in file_handler:
                    file_sentence_tokens.append(line.strip().split(' '))
                rel_file_name = test_file_name.split(os.path.sep)[-1][:-len(WORD_SEGMENTED_EXT + NON_DIA_EXT)]
                self.test_data[rel_file_name] = file_sentence_tokens
                
    def decode(self, sentence_tokens):
        '''-------------------------------------------------
        Decode a sentence to get the most likely diacritic form
        ------------------------------------------------- 
        '''
        
        '''Append NONE as the BEGINNING of the sentence'''
        sentence_tokens = [None] + sentence_tokens
        decode_array = [[(None, None, 0, None)]]
        for i in xrange(1, len(sentence_tokens)):
            non_diacritic_token = sentence_tokens[i]
            full_token_candidates = self.diacritic_handler.get_acceptable_forms(non_diacritic_token)
            full_token_candidates += self.emission_prob.get_full_form(non_diacritic_token)
#             print  non_diacritic_token
#             print len(full_token_candidates)
            if (len(full_token_candidates) > MAX_NO_OF_AVAILABLE):
                full_token_candidates = [non_diacritic_token]
            token_tags = []
            for diacritic_token in full_token_candidates:
                for seg_tag in [BEGIN_TAG, INSIDE_TAG]:
                    max_value = None
                    max_trace = None
                    previous_step_tokens = decode_array[i - 1]
                    for j in xrange(len(previous_step_tokens)):
                        prev_diacritic_token = previous_step_tokens[j][TOKEN_INDEX]
                        prev_seg_tag = previous_step_tokens[j][TAG_INDEX]
                        '''Max value at the previous step'''
                        new_value = decode_array[i - 1][j][VAL_INDEX]
                        '''Transition log probability'''
                        new_value += self.language_model.query_log(prev_diacritic_token, prev_seg_tag,
                                                     diacritic_token, seg_tag)
                        '''Emission log probability'''
                        new_value += self.emission_prob.query_emission_log(diacritic_token, non_diacritic_token)
                        if max_value == None or max_value < new_value:
                            max_value = new_value
                            max_trace = j
                    token_tags.append((diacritic_token, seg_tag, max_value, max_trace))
            decode_array.append(token_tags)
        
        max_value = None
        max_index = None
        for i in xrange(len(decode_array[-1])):
            val = decode_array[-1][i][VAL_INDEX]
            if max_value == None or max_value < val:
                max_value = val
                max_index = i
        
        '''
        Trace back
        '''
        diacritic_sent = []
        
        trace_index = max_index
        for i in xrange(len(decode_array) - 1, 0, -1):
            diacritic_sent.append((decode_array[i][trace_index][TOKEN_INDEX],
                                   decode_array[i][trace_index][TAG_INDEX]))
            trace_index = decode_array[i][trace_index][TRACE_INDEX]
        diacritic_sent.reverse()
        return diacritic_sent
