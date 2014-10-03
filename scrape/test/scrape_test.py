# -*- coding: utf-8 -*-
"""
Testing
"""
import scrape
import logging
import time

def main():
    # Save log to file
    logging.basicConfig(filename='test_scrape.log', filemode='w',
                        level=logging.WARNING)
    # Initialize scraper
    scraper = scrape.TicketScraper()
    
    # 1) Try to get a ticket page
    print("Try to get a page of tickets")
    START = time.time()    
    
    start = time.time()
    tickets = scraper.getTicketsOnPage(1)
    end = time.time()
    
    print(end - start) # Approximately 16 seconds for page 1 (~0.5s/page)
    
    for t in tickets:
        print(t)
    END = time.time()
    
    print("Total time: " + str(END - START))
    
    # Test what happens when we get a bad status code
    scraper.getPage('http://httpbin.org/status/404')
    
    # Test what happens when time out
    
    
if __name__ == '__main__':
    main()