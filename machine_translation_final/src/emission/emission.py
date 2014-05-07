'''
Created on May 4, 2014

@author: Tuan
'''
import codecs
from collections import defaultdict
import math

from src import FILE_CODEC


class EmissionProb(object):
    '''
    Emission probability should be calculated by training 
    on some real non-diacritic data. However, for this project,
    emission will be 1 for most of cases, or some 
    given random values for some abbreviations.
    '''

    def __init__(self, emision_model_file = None):
        '''
        - emission_file: abbreviation file indeed:
            The format is fullform \t shortenedform \t probability \t translation
        '''
        self.emision_model_file = emision_model_file
        self.emission_prob = {}
        self.map = defaultdict(list)
        self.inverted_map = defaultdict(list)
        self.contract_prob = defaultdict(float)
        self.load_emision_model_file();
        
    def load_emision_model_file(self):
        print self.emision_model_file
        with codecs.open(self.emision_model_file, 'r', FILE_CODEC) as file_handler:
            for line in file_handler:
                full_form, contract_form, value, translation = line.strip().split('\t')
                self.emission_prob[(full_form, contract_form)] = float(value)
                self.contract_prob[full_form] += float(value)
                self.map[full_form].append(contract_form)
                self.inverted_map[contract_form].append(full_form) 
    
    def get_full_form(self, contract_form ):
        '''-------------------------------------------------
        
        ---------------------------------------------------- 
        '''
        if contract_form in self.inverted_map:
            return self.inverted_map[contract_form]
        return []
    
    def query_emission_log(self, full_form, contract_form ):
        '''-------------------------------------------------
        
        ---------------------------------------------------- 
        '''
        if 'emission_prob' in self.__dict__:
            if (full_form, contract_form) in self.emission_prob:
                return math.log(self.emission_prob[(full_form, contract_form)])
            if full_form in self.map:
                return 1 - self.contract_prob[full_form]
        return 0