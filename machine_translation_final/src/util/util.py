'''
Created on May 5, 2014

@author: Tuan
'''
from src import BEGIN_TAG, INSIDE_TAG


class Utils(object):
    '''
    All utils method here
    '''
    @staticmethod
    def bracket_to_array_form(sentences):
        '''
        '''
        sentence_words = []
        for sentence in sentences:
            words = [word.split(']') for word in sentence.split('[') if word.strip() != '']
            words = [word[0].split(' ') for word in words]
            sentence_words.append(words)
        
        return sentence_words
    
    @staticmethod
    def word_to_tokens_form (sentence_words):
        '''
        Purpose: flatsentence_wordsword into an array of tokens, with segment tag
    sentence_wordsword is an array of array, with element array are tokens of words
    sentence_wordsword is a nested structure,
        '''
        token_list = []
        for i in xrange(len(sentence_words)):
            word = sentence_words[i]
            for j in xrange(len(word)):
                token = word[j]
                if  j == 0:
                    token_list.append((token, BEGIN_TAG))
                else:
                    token_list.append((token, INSIDE_TAG))
        return token_list