# -*- coding: utf-8 -*-
import time
import scrapy
from selenium import webdriver
from scrapy.selector import Selector
from scrapy.http import Request
from selenium.common.exceptions import NoSuchElementException
from books_crawler.items import BooksCrawlerItem


class BooksSpider(scrapy.Spider):
    name = 'books'
    allowed_domains = ['books.toscrape.com/']

    def start_requests(self):
        self.driver = webdriver.Chrome('/Users/ejikeobineme/Desktop/chromedriver')
        self.driver.get('http://books.toscrape.com')
        
        # gain access to website's xml tree through Selenium.
        sel = Selector(text=self.driver.page_source)
        
        # make a list of selectors for book links.
        books = sel.xpath('//h3/a/@href').extract()

        for book in books:
            url = 'https://books.toscrape.com/' + book
            # send a HTTP request and send response object to parse_book().
            yield Request(url, callback=self.parse_book)

        while True:
            try:
                next_page = self.driver.find_element_by_xpath('//a[text()="next"]')
                time.sleep(3)
                self.logger.info('Sleeping for 3 seconds.')
                next_page.click()

                sel = Selector(text=self.driver.page_source)
                books = sel.xpath('//h3/a/@href').extract()
                for book in books:
                    url = 'https://books.toscrape.com/' + book
                    yield Request(url, callback=self.parse_book)

            except NoSuchElementException:
                self.logger.info('No more pages to load.')
                self.driver.quit()
                break

    def parse_book(self, response):
        items = BooksCrawlerItem()
        title = response.css('h1::text').extract_first()
        url = response.request.url
    
        items['Title'] = title
        items['Url'] = url
        yield items
        
        # title = response.css('h1::text').extract_first()
        # url = response.request.url
        # yield {'title': title, 'url':url}


   