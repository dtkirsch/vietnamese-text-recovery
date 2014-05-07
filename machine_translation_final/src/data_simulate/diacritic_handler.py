# -*- coding: utf-8 -*-
'''
Created on May 3, 2014

@author: Tuan
'''
import codecs
from collections import defaultdict
import glob
import itertools
import os
import re

from src import DATA_DIRECTORY, WORD_SEGMENTED_EXT, NON_DIA_EXT, TOKEN_INDEX, \
    FILE_CODEC
from src.util.util import Utils

FILE_AFFIX = "_language_diacritic.map"
NO_OF_NONE_TONE = 14
class DiacriticHandler(object):
    '''
    Class to handle diacritics in syllables.
    Two taskes are: 
    -    remove diacritics from full-form syllables
    -    add diacritics onto non-diacritic syllables
    '''
    
    def __init__(self, language):
        '''
        Currently the only accepted language is Vietnamese
        '''
        self.language = language
        '''
        Format of the file to be read in:
        More diacritic form \t Less diacritic form 
        '''
        self.unicode_map = {}
        '''
        The first 14 lines in the diacritic files
        are for decorating diacritics (diacritics to change
        different vowels and consonants)
        '''
        self.none_tone_unicode_map = {}
        '''
        The other lines are for tone diacritics
        '''
        self.tone_unicode_map = {}
        self.load_code_map(language)
        '''
        Map from any form to the simplest form (non-diacritic at all)
        '''
        self.plain_code_map = {}
        self.create_plain_code_map()
        '''
        Build some different inverted index from simpler form
        '''
        self.inverted_non_tone_map = defaultdict(list)
        self.inverted_tone_map = defaultdict(list)
        self.build_inverted_code_map()
        '''
        Load diphthong and tripthong files:
        '''
        self.load_vowel_cluster()
    
    def load_code_map(self, language):
        '''-------------------------------------------------
        Load from the file, and populate:
            - self.unicode_map
            - self.none_tone_unicode_map
            - self.tone_unicode_map (dict)
        ----------------------------------------------------
        '''
        language_file_name = language + FILE_AFFIX
        language_file_name = os.path.join(DATA_DIRECTORY, language_file_name)
        with codecs.open(language_file_name, 'r', FILE_CODEC) as file_handler:
            counter = 0
            for line in file_handler:
                counter += 1
                more_diaritic_form, less_diaritic_form = line.strip().split('\t')
                self.unicode_map[more_diaritic_form] = less_diaritic_form
                if counter > NO_OF_NONE_TONE:
                    self.tone_unicode_map[more_diaritic_form] = less_diaritic_form
                else:
                    self.none_tone_unicode_map[more_diaritic_form] = less_diaritic_form
                    
    def create_plain_code_map(self):
        '''-------------------------------------------------
        Fself.unicode_map doesn't map a character to its simplest form 
        (non diacritic at all, just map to the next simpler form):
        ứ -> ư -> u
        Recursively build the map from one character to its simplest form
        ----------------------------------------------------
        '''
        for character in self.unicode_map:
            non_diacritic = character;
            while non_diacritic in self.unicode_map:
                non_diacritic = self.unicode_map[non_diacritic]
            self.plain_code_map[character] = non_diacritic
                
    def build_inverted_code_map(self):
        '''-------------------------------------------------
        Inverted map from non diacritic forms to equal or more diacritic form
        - inverted_non_tone_map: from an ASCII character to a non-tone character
        thas has decorating diacritic.
        - inverted_tone_map: from a character to all toned character
        ----------------------------------------------------
        '''
        for more_diaritic_form in self.none_tone_unicode_map:
            self.inverted_non_tone_map[self.none_tone_unicode_map[more_diaritic_form]].append(more_diaritic_form)
        for non_diacritic in self.inverted_non_tone_map:
            self.inverted_non_tone_map[non_diacritic].append(non_diacritic)
        
        for more_diaritic_form in self.tone_unicode_map:
            self.inverted_tone_map[self.tone_unicode_map[more_diaritic_form]].append(more_diaritic_form)
        for less_diacritic in self.inverted_tone_map:
            self.inverted_tone_map[less_diacritic].append(less_diacritic)
    
    def get_acceptable_forms(self, token):
        '''-------------------------------------------------
        Token is assumed to be in non-diacritic forms
        return: (heuristically) all language allowed forms
        ----------------------------------------------------
        '''
        t = self.check_vowels(token)
        if t == None:
            return [token]
        else:
            start, end = t
            
        if end == start + 1:
            return self.one_vowel_cluster(token, start)
        
        if end == start + 2:
            return self.two_vowel_cluster(token, start)
        
        if end == start + 3:
            return self.three_vowel_cluster(token, start)
        
        return [token]
    
    def one_vowel_cluster(self, token, start):
        '''-------------------------------------------------
        Return all full form of a token given its position of vowel cluster (single vowel)
        ----------------------------------------------------
        '''
        diacritic_forms = self.get_diacritic_forms(token)
        toned_forms = [token]
        for diacritic_form in diacritic_forms:
            toned_forms += self.get_tone_forms(diacritic_form, start)
        return list(set(toned_forms))
    
    def two_vowel_cluster(self, token, start):
        '''-------------------------------------------------
        Return all full form of a token given its position of vowel cluster (diphthong)
        ----------------------------------------------------
        '''
        diacritic_forms = self.get_diacritic_forms(token)
        toned_forms = [token]
        for diacritic_form in diacritic_forms:
            if diacritic_form[start:start+2] not in self.diphthong_1 + self.diphthong_2:
                pass
            elif diacritic_form[start:start+2] in self.diphthong_1:
                toned_forms += self.get_tone_forms(diacritic_form, start)
            elif diacritic_form[start:start+2] in self.diphthong_2:
                toned_forms += self.get_tone_forms(diacritic_form, start + 1)
        return list(set(toned_forms))
    
    def three_vowel_cluster(self, token, start):
        '''-------------------------------------------------
        Return all full form of a token given its position of vowel cluster (tripthong)
        ----------------------------------------------------
        '''
        diacritic_forms = self.get_diacritic_forms(token)
        toned_forms = [token]
        for diacritic_form in diacritic_forms:
            if diacritic_form[start:start+3] not in self.tripthong_1 + self.tripthong_2:
                pass
            elif diacritic_form[start:start+3] in self.tripthong_1:
                toned_forms += self.get_tone_forms(diacritic_form, start + 1)
            elif diacritic_form[start:start+3] in self.tripthong_2:
                toned_forms += self.get_tone_forms(diacritic_form, start + 2)
        return list(set(toned_forms))
        
    def check_vowels(self, token):
        '''-------------------------------------------------
        
        ----------------------------------------------------
        '''
        m = re.search('[a|u|o|y|i|u|e]+' , token)
        ms = re.finditer('[a|u|o|y|i|u|e]+' , token)
        '''
        One special case when the initial is consonant gi
        '''
        counter = 0
        for m in ms:
            if counter == 0:
                start = m.start(0)
                end = m.end(0)
            counter += 1
        if counter != 1:
            '''
            There is no vowel to consider or there are more than 1 vowels (foreign words)
            '''
            return None
        
        if token[:2] == 'gi':
            return (start + 1, end)
        return (start, end)
                    
    def get_diacritic_forms(self, token):
        '''-------------------------------------------------
        Token is assumed to be in non-diacritic forms
        return: all plain diacritic forms (no tone)
        ----------------------------------------------------
        '''
        try:
            token = unicode(token)
            diacritic_chars = []
            for character in token:
                if character in self.inverted_non_tone_map:
                    diacritic_chars.append(self.inverted_non_tone_map[character])
                else:
                    diacritic_chars.append([character])
            diacritic_forms = []
            for combination in itertools.product(*diacritic_chars):
                diacritic_forms.append(''.join(combination))
            return diacritic_forms
        except UnicodeDecodeError:
            return [' ']
    
    def get_tone_forms(self, token, character_index):
        '''-------------------------------------------------
        Get all tone forms of a syllable given the position of the main vowel
        ----------------------------------------------------
        '''    
        '''
        Token is assumed to has plain tone (no tone marker)
        '''
        try:
            token = unicode(token)
            tone_chars = self.inverted_tone_map[token[character_index]]
            tone_forms = []
            for tone_char in tone_chars:
                tone_forms.append(token[:character_index] + tone_char + token[character_index + 1:])
            return tone_forms
        except UnicodeDecodeError:
            return [' ']
        except IndexError:
            return [' ']
        
    def remove_diacritics(self, line):
        '''-------------------------------------------------
        Remove diacritics in a text line
        ----------------------------------------------------
        '''
        '''
        Remove diacritics in a lines by finding the matching unicode character
        and 
        '''
        line = unicode(line)
        non_diacritics = ''.join(self.remove_diacritic(character) for character in line)
        return non_diacritics
    
    def remove_diacritic(self, character):
        '''-------------------------------------------------
        Remove diacritics from a character
        ----------------------------------------------------
        '''
        if character in self.plain_code_map:
            return self.plain_code_map[character]
        else:
            return character
    
    def load_vowel_cluster(self):
        '''-------------------------------------------------
        diphthong1 has the first vowel is the main one
        diphthong2 has the second vowel is the main one
        tripthong1 has the second vowel is the main one
        tripthong2 has the third vowel is the main one
        ----------------------------------------------------
        '''
        DIPHTHONG_1 = 'diphthong1.txt'
        DIPHTHONG_2 = 'diphthong2.txt'
        TRIPTHONG_1 = 'tripthong1.txt'
        TRIPTHONG_2 = 'tripthong2.txt'
        diphthong_1_file = os.path.join(DATA_DIRECTORY, DIPHTHONG_1)
        diphthong_2_file = os.path.join(DATA_DIRECTORY, DIPHTHONG_2)
        tripthong_1_file = os.path.join(DATA_DIRECTORY, TRIPTHONG_1)
        tripthong_2_file = os.path.join(DATA_DIRECTORY, TRIPTHONG_2)
        self.diphthong_1 = []
        self.diphthong_2 = []
        self.tripthong_1 = []
        self.tripthong_2 = []
        '''
        Remember to save the file as utf-8 without BOM (using Sublime Text)
        '''
        with codecs.open(diphthong_1_file, 'r', FILE_CODEC) as input_file_handler:
            for line in input_file_handler:
                self.diphthong_1.append(line.strip())
        with codecs.open(diphthong_2_file, 'r', FILE_CODEC) as input_file_handler:
            for line in input_file_handler:
                self.diphthong_2.append(line.strip())
        with codecs.open(tripthong_1_file, 'r', FILE_CODEC) as input_file_handler:
            for line in input_file_handler:
                self.tripthong_1.append(line.strip())
        with codecs.open(tripthong_2_file, 'r', FILE_CODEC) as input_file_handler:
            for line in input_file_handler:
                self.tripthong_2.append(line.strip())
    
    def make_non_diacritic_files(self, input_directory, output_directory):
        '''-------------------------------------------------
        Remove diacritic from all files that have .wseg in a directory
        ----------------------------------------------------
        '''
        for input_file_name in glob.glob(os.path.join(input_directory, '*' + WORD_SEGMENTED_EXT)):
            print input_file_name
            rel_file_name = input_file_name.split(os.path.sep)[-1][:-len(WORD_SEGMENTED_EXT)]
            output_file_name = os.path.join(output_directory, rel_file_name + 
                                            WORD_SEGMENTED_EXT + NON_DIA_EXT)
            self.make_non_diacritic_file(input_file_name, output_file_name)
            
    def make_non_diacritic_file(self, input_file_name, output_file_name):
        '''-------------------------------------------------
        Remove diacritic from one file
        ----------------------------------------------------
        '''
        file_non_diacritics = []
        with codecs.open(input_file_name, 'r', FILE_CODEC) as input_file_handler:
            sentences = []
            for line in input_file_handler:
                sentences.append(line.strip())
            file_sentence_words = Utils.bracket_to_array_form(sentences)
            
            for sentence_words in file_sentence_words:
                token_tag_list = Utils.word_to_tokens_form(sentence_words)
                token_only_list = [t[TOKEN_INDEX] for t in token_tag_list]
                no_seg_form = ' '.join(token_only_list)
                non_diacritic_form = self.remove_diacritics(no_seg_form)
                file_non_diacritics.append(non_diacritic_form)
                
        with codecs.open(output_file_name, 'w', FILE_CODEC) as output_file_handler:
            for non_diacritic_form in file_non_diacritics:
                output_file_handler.write(non_diacritic_form + '\n')
