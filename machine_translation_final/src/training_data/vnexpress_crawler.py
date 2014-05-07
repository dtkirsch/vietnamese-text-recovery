'''
Created on May 3, 2014

@author: Tuan
'''
import codecs
import os

import lxml.html

from src import DATA_DIRECTORY, VNEXPRESS_DATA_DIRECTORY
from src.training_data.crawler import Crawler

class VnExpressCrawler(Crawler):
    '''
    Crawler articles from vnexpress.net
    '''

    def __init__(self):
        self.main_page = "http://vnexpress.net"
        self.article_prefix = 'vnexpress'
        self.article_links_file = os.path.join(DATA_DIRECTORY, 'article_links.txt')
        self.output_data_directory = VNEXPRESS_DATA_DIRECTORY
    
    def get_article_links(self):
        '''-------------------------------------------------
        Get some article links (should be all possible article links)
        However, vnexpress has different format on different subcategory,
        therefore this algorithm only query one certain format
        ---------------------------------------------------- 
        '''
        with codecs.open(self.article_links_file, 'w') as file_handler:
            sub_category_links = self.get_sub_category_links()
            for sub_category_link in sub_category_links:
                article_links = self.get_article_links_from_sub_category(sub_category_link)
                for link in article_links:
                    file_handler.write(link + '\n')
    
    def get_sub_category_links(self):
        '''-------------------------------------------------
        Get all sub_category_links from the main page
        ---------------------------------------------------- 
        '''
        main_page_content = self.crawl(self.main_page)
        """
        Format of the xml file returned
        
        """
        root = lxml.html.fromstring(main_page_content)
        sub_category_link_elements = root.get_element_by_id("footer").find_class("liFollow")
        sub_category_links_raw = [link.find('h2').find('a').attrib["href"] for link in sub_category_link_elements]
        sub_category_links = []
        for link in sub_category_links_raw:
            if link[:7] != 'http://':
                sub_category_links.append(self.main_page + link)
            sub_category_links.append(link)
        return sub_category_links
    
    def get_article_links_from_sub_category(self, sub_category_link):
        '''-------------------------------------------------
        Query some articles links from vnexpress and save them into article_links_file
        ---------------------------------------------------- 
        '''
        article_links = []
        try:
            '''Just try to find the last page'''
            no_of_pages = self.get_last_page(sub_category_link)
            print no_of_pages
            for page in xrange(1, no_of_pages + 1):
                page_suffix = 'page/%s.html' % page
                sub_page_link = sub_category_link + page_suffix
                article_links += self.get_articles_links_single_page(sub_page_link)
            return article_links
        except Exception:
            return []
    
    def get_last_page(self, sub_page_link):
        '''-------------------------------------------------
        Heuristically find the last page of a category
        ---------------------------------------------------- 
        '''
        last_page_initial = 1024
        last_page = self.explore_last_page(sub_page_link, last_page_initial)
        if ( last_page != 1 ):
            '''Second type of page'''
            return last_page
        while (last_page == 1):
            last_page_initial /= 2
            last_page = self.explore_last_page(sub_page_link, last_page_initial)
        return last_page

    def explore_last_page(self, sub_page_link, last_page_value):
        last_page_suffix = 'page/%s.html' %last_page_value
        sub_page_content = self.crawl(sub_page_link + last_page_suffix)
        root = lxml.html.fromstring(sub_page_content)
        last_page = int(root.get_element_by_id('pagination').find_class("active")[0].text)
        return last_page
    
    def get_articles_links_single_page(self, sub_page_link):
        '''-------------------------------------------------
        Get all articles from one page (pagination) from one category
        ---------------------------------------------------- 
        '''
        print sub_page_link
        sub_page_content = self.crawl(sub_page_link)
        root = lxml.html.fromstring(sub_page_content)
        article_link_elements = root.get_element_by_id('news_home').findall('li')
        article_links = [element.find_class('title_news')[0].find('a').attrib["href"] for element in article_link_elements]
        return article_links
    
    def load_article_linkes(self):
        '''-------------------------------------------------
        Load articles links if it is already saved
        ---------------------------------------------------- 
        '''
        with codecs.open(self.article_links_file, 'r') as file_handler:
            self.article_links = []
            for line in file_handler:
                self.article_links.append(line.strip())
