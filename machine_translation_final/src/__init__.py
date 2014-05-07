'''
Created on May 3, 2014

@author: Tuan
'''
import os

'''-------------------------------------'''
'''Directory string form ---------------'''
scriptName = __file__
scriptPath = os.path.abspath(scriptName)
ROOT_DIRECTORY = os.path.dirname(os.path.dirname(scriptPath))
DATA_DIRECTORY = os.path.join(ROOT_DIRECTORY,"data")
VNEXPRESS_DATA_DIRECTORY = os.path.join(DATA_DIRECTORY,"vnexpressData")
SEGMENT_TRAIN = os.path.join(DATA_DIRECTORY,"segment_data_train")

'''-------------------------------------'''
'''Extension string form ---------------'''
NON_DIA_EXT = '.nodiac'
WORD_SEGMENTED_EXT = '.wseg'
DECODED_EXT = '.decode'
FILE_CODEC = 'utf-8'

'''-------------------------------------'''
'''Logical string data -----------------'''
BEGIN_TAG = 'B'
INSIDE_TAG = 'I'
TOKEN_INDEX = 0
TAG_INDEX = 1
VAL_INDEX = 2
TRACE_INDEX = 3

'''-------------------------------------'''
'''Other string data -------------------'''
VN_LANGUAGE = "vn"