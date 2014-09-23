# -*- coding: utf-8 -*-
"""
Testing
"""
import scrape
import time

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