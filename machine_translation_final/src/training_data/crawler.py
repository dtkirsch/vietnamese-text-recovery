'''
Created on May 3, 2014

@author: Tuan
'''

from Queue import Queue
import codecs
import os
import re
import thread
from threading import Thread
import urllib2

import lxml.html

import xml.etree.ElementTree as ET


TITLE_NEWS = 'title_news'
SHORT_INTRO = 'short_intro'
CONTENT_TEXT = 'content_text'
DATA_EXT = '.data'

class Crawler():
    '''
    Just a plain crawler
    '''

    @staticmethod
    def crawl(url):
        try:
            req = urllib2.Request(url=url)
            streaming = urllib2.urlopen(req)
            crawl_buffer = "";
            for line in streaming:
                crawl_buffer += line
            return crawl_buffer
        except IOError:
            print 'Connection could not be established.\nFail to crawl the file.'
            return False
        except UnicodeError:
            print 'Unicode character. Ignored.'
            return False
    
    def get_articles(self):
        '''-------------------------------------------------
        Crawl using a Thread pool
        ---------------------------------------------------- 
        '''
        self.load_article_linkes()
        self.split_articles_index = 100
        self.no_of_threads = 20
        
        self.parameters = []
        for i in xrange(len(self.article_links) / self.split_articles_index + 1):
            begin = self.split_articles_index * i
            end = min(self.split_articles_index * (i + 1), len(self.article_links))
            split_articles = self.article_links[begin: end]
            self.parameters.append((i, begin, end, split_articles))
        
        self.thread_pool = ThreadPool(self.no_of_threads, self.output_data_directory, 
                                self.article_prefix)
        for i in xrange(len(self.parameters)):
            self.thread_pool.add_task(self.parameters[i])
            
        self.thread_pool.wait_completion()
            
class QueryArticle (Thread):
    def __init__(self, thread_pool, output_data_directory, article_prefix):
        Thread.__init__(self)
        self.thread_pool = thread_pool
        self.output_data_directory = output_data_directory
        self.article_prefix = article_prefix
        
    def run(self):
        while True:
            parameters = self.thread_pool.get_task_parameter()
            self.index = parameters[0]
            self.begin = parameters[1]
            self.end = parameters[2]
            self.split_articles = parameters[3]
            with codecs.open(os.path.join(self.output_data_directory, 
                                          '%s_%s%s' % (self.article_prefix, 
                                                       self.index, DATA_EXT)), 'w') as file_handler:
                root = ET.Element('articles')
                root.attrib['begin'] = str(self.begin)
                root.attrib['end'] = str(self.end)
                for article in self.split_articles:
                    print article
                    article_element = ET.SubElement(root, 'article', {'ref':article})
                    all_contents = self.get_content(article)
                    title_element = ET.SubElement(article_element, TITLE_NEWS )
                    title_element.text = all_contents[TITLE_NEWS]
                    intro_element = ET.SubElement(article_element, SHORT_INTRO )
                    intro_element.text = all_contents[SHORT_INTRO]
                    content_element = ET.SubElement(article_element, CONTENT_TEXT )
                    content_element.text = all_contents[CONTENT_TEXT]
                
                content = str(ET.tostring(root, 'utf-8'))
                text_re = re.compile('>\n\s+([^<>\s].*?)\n\s+</', re.DOTALL)    
                prettyContent = text_re.sub('>\g<1></', content)
                file_handler.write(prettyContent)
            self.thread_pool.task_done()
            
    
    def get_content(self, article_link):
        article_content = Crawler.crawl(article_link)
        root = lxml.html.fromstring(article_content)
        title_news = ''
        short_intro = ''
        content_text = ''
        try:
            title_news = root.find_class('title_news')[0].find('h1').text_content()
            short_intro = root.find_class('short_intro')[0].text_content()
            content_text = ''
            content_elements = root.find_class('fck_detail')[0].find_class('Normal')
            for content_element in content_elements:
                content_text += content_element.text_content()
        except Exception as e:
            print e
        return {TITLE_NEWS: title_news, 
                SHORT_INTRO: short_intro, 
                CONTENT_TEXT: content_text}

class ThreadPool:
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads, output_data_directory, article_prefix):
        self.tasks = Queue(num_threads)
        for _ in xrange(num_threads):
            thread = QueryArticle(self, output_data_directory, 
                                article_prefix)
            thread.start();
    
    def get_task_parameter(self):
        return self.tasks.get()
    
    def add_task(self, parameter):
        """Add a task to the queue"""
        self.tasks.put(parameter)
    
    def task_done(self):
        self.tasks.task_done()
        
    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()