# -*- coding: utf-8 -*-
"""
Testing
"""
import scrape
import logging
import time

def main():
    START = time.time()
    # Save log to file
    logging.basicConfig(filename='test_scrape.log', filemode='w',
                        level=logging.WARNING)
    
    scraper = scrape.TicketScraper()
    
    start = time.time()
    tickets = scraper.getTicketsOnPage(1)
    end = time.time()
    
    print(end - start) # Approximately 16 seconds for page 1 (~0.5s/page)
    
    # How about getting a page close to the MAX_PAGE? Does it take longer?
    start = time.time()
    tickets = scraper.getTicketsOnPage(scraper.MAX_PAGE - 1)
    end = time.time()
    
    print(end - start) # Approximately 46 seconds for page 54379 (~1.5s/page)
    
    END = time.time()
    
    print("Total time: " + str(END - START))
    
if __name__ == '__main__':
    main()