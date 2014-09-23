# -*- coding: utf-8 -*-
"""
Class for parsing parking tickets data from Vancouver Sun's parking tickets
database. See http://www.vancouversun.com/parking/basic-search.html
"""

from bs4 import BeautifulSoup
import requests
import sqlite3

# Some

class TicketScraper:
    '''
    Extract parking tickets data from the Vancouver Sun
    '''
    # Some constants
    # The total number of pages in the db
    MAX_PAGE = 54380
    # The root url of the db, needed to follow relative links
    URL_ROOT = "http://b2.caspio.com/"
    # Construct the url with appkey %s to page %d in the db
    URL_TEMPLATE = URL_ROOT + "dp.asp?AppKey=%s&RecordID=&PageID=2&" + \
        "PrevPageID=1&cpipage=%d&CPISortType=&CPIorderBy="
    # The fields in a ticket, in order as they appear on a ticket page
    TICKET_FIELDS = (
        "date", "time", "license_plate", "province", "vehicle_make", 
        "street_no", "street_name", "street_side", "meter_no", 
        "offence_type", "offence_detail", "bylaw_no", "bylaw_sect", 
        "fine", "fine_early", "impound_requested", "ticket_no"
        )

    def __init__(self):
        self.AppKey = self.getAppKey()

    def getAppKey(self):
        # Open the parking tickets search page from vancouversun.com.
        # Grab the app key, and then retrieve the page with results to scrape
        START_URL = "http://www.vancouversun.com/parking/basic-search.html"
        startPage = requests.get(START_URL)

        # Raise an exception if the page did not load!
        startPage.raise_for_status()

        # Parse the page using Beautiful Soup to find the app key
        soup = BeautifulSoup(startPage.content)

        # Get the app key. It should be contained in the div layer with
        # id="cxkg", which holds a link with
        # href="http://b2.caspio.com/dp.asp?AppKey=[APPKEY]"
        # Grab the link to the db page and extract the App Key
        return soup.find("div", id="cxkg").find("a")["href"].split("AppKey=")[1]

    def getTicketsOnPage(self, pageNum):
        # Make sure we have a valid page number
        if pageNum < 1 | pageNum > self.MAX_PAGE:
            raise ValueError("pageNum must be between 1 and " + self.MAX_PAGE)

        # Construct the url for the db at page pageNum
        url = self.URL_TEMPLATE % (self.AppKey, pageNum)

        # Try to get the page
        print("----- Loading page %d" % (pageNum), end=" ... ", flush=True)
        dbPage = requests.get(url)
        print("Done!", flush=True)

        # Throw exception if page did not load correctly
        dbPage.raise_for_status()

        # Soupify
        soup = BeautifulSoup(dbPage.content)

        # The links to the tickets are <a> tags enclosing the text, "Details"
        ticketLinks = soup.find_all("a", text="Details")
        
        # For each link in the array, extract the "href" entry
        ticketLinks = map(lambda x: x.get("href"), ticketLinks)
        
        # Now get all the info for the tickets on this page
        tickets = []
        for linkNum, link in enumerate(ticketLinks) :
            print("Parsing link %02d of page %d" % (linkNum + 1, pageNum), 
                  end=" ... ", flush=True)
            tickets.append(self.getTicketDetails(link))
            print("Done!", flush=True)
        
        return tickets
    
    def getTicketDetails(self, ticketLink):
        # Get the page
        ticketPage = requests.get(self.URL_ROOT + ticketLink)
        
        # Raise exception if page did not load
        ticketPage.raise_for_status()        

        # Parse the page contents
        soup = BeautifulSoup(ticketPage.content)
        
        # Get the ticket details
        ticketDetails = soup.find_all("span")
        # Append our results list
        return [ span.getText() for span in ticketDetails ]


# Run the ticket scraper
if __name__ == "__main__":    
    scraper = TicketScraper()
    tickets = scraper.getTicketsOnPage(1)