# -*- coding: utf-8 -*-
"""
Class for parsing parking tickets data from Vancouver Sun's parking tickets
database. See http://www.vancouversun.com/parking/basic-search.html
"""

from bs4 import BeautifulSoup
import requests
from datetime import datetime as d
import logging
# import sqlite3

# Some

class TicketScraper:
    '''
    Extract parking tickets data from the Vancouver Sun
    '''
    # The total number of pages in the db
    MAX_PAGE = 54380
    # The total number of attempts to load a page
    MAX_TRIES = 3
    # The root url of the db, needed to follow relative links
    URL_ROOT = "http://b2.caspio.com/"
    # Construct the url with appkey %s to page %d in the db
    URL_TEMPLATE = URL_ROOT + "dp.asp?AppKey={}&RecordID=&PageID=2&" + \
        "PrevPageID=1&cpipage={:.0f}&CPISortType=&CPIorderBy="
    # The fields in a ticket, in order as they appear on a ticket page
    TICKET_FIELDS = (
        "date", "time", "license_plate", "province", "vehicle_make", 
        "street_no", "street_name", "street_side", "meter_no", 
        "offence_type", "offence_detail", "bylaw_no", "bylaw_sect", 
        "fine", "fine_early", "impound_requested", "ticket_no"
        )

    def __init__(self):
        # Save log to a file
        self.AppKey = self.getAppKey()

    def getAppKey(self):
        '''
        Initialize the web app on the webpage and grab the App Key to access 
        the online database
        '''
        # Open the parking tickets search page from vancouversun.com.
        # Need to grab an app key from vancouver sun
        START_URL = "http://www.vancouversun.com/parking/basic-search.html"
        
        # Initialize appKey
        appKey = None        
        
        # Try to get the page
        logging.debug("Attempting to grab app key")
        startPage = self.getPage(START_URL)

        # Parse the page if it loaded OK
        if startPage.ok:
            # Parse the page using Beautiful Soup to find the app key
            soup = BeautifulSoup(startPage.content)
    
            # Get the app key. It should be contained in the div layer with
            # id="cxkg", which holds a link with
            # href="http://b2.caspio.com/dp.asp?AppKey=[APPKEY]"
            appKey = soup.find("div", id="cxkg").find("a")["href"]
            appKey = appKey.split("AppKey=")[1]
            logging.debug("App key retrieved")
            return appKey
        # Page didn't load!
        logging.error(
        "Failed to get app key! Page status: {}".format(startPage.status_code)
        )
        # Raise an exception if the page did not load in MAX_TRIES attempts!
        startPage.raise_for_status()
    
    def getPage(self, url):
        '''
        Helper function - try to load a URL MAX_TRIES times
        '''
        for attempt in range(self.MAX_TRIES):
            page = requests.get(url)
            if page.ok:
                break
        return page

    def getTicketsOnPage(self, pageNum):
        '''
        Get all the tickets data on page pageNum in the database
        '''
        # Make sure we have an app key
        if self.AppKey is None:
            ValueError("AppKey not initialized - run getAppKey()!")
        # Make sure we have a valid page number
        if pageNum < 1 or pageNum > self.MAX_PAGE:
            raise ValueError("pageNum must be between 1 and " + 
                             str(self.MAX_PAGE))

        # Construct the url for the db at page pageNum
        url = self.URL_TEMPLATE.format(self.AppKey, pageNum)

        # Try to get the page
        logging.debug("Loading page {:.0f}".format(pageNum))
        dbPage = self.getPage(url)
        
        # If the page loaded, continue
        if dbPage.ok:
            # Soupify
            soup = BeautifulSoup(dbPage.content)
    
            # Links to tickets are <a> tags enclosing the text "Details"
            ticketLinks = soup.find_all("a", text="Details")
            
            # For each link in the array, extract the "href" entry
            ticketLinks = map(lambda x: x.get("href"), ticketLinks)
            
            # Now get all the info for the tickets on this page
            tickets = []
            for linkNum, link in enumerate(ticketLinks) :
                logging.info(
                "Parsing link {:0>2d} of page {}".format(linkNum + 1, pageNum)
                )
                ticketDetails = self.getTicketDetails(link)
                if ticketDetails is not None:
                    tickets.append(ticketDetails)
                else:
                    logging.warning(
                    "Failed to load link {:0>2d} ".format(linkNum + 1), 
                    "on page {}".format(pageNum))
            # Done!
            return tickets
        else:
            logging.warning("Failed to load page {:.0f}".format(pageNum))
            return None
    
    def getTicketDetails(self, ticketLink):
        '''
        Get the ticket data from the url ticketLink
        '''
        # Get the page
        ticketPage = self.getPage(self.URL_ROOT + ticketLink)
        # Initialize the ticket details object
        ticketDetails = None
        
        # Return the ticket details if page loaded OK, otherwise return None
        if ticketPage.ok:
            # Parse the page contents
            soup = BeautifulSoup(ticketPage.content)
            # Get the ticket details
            ticketDetails = [ cell.getText() for cell in soup.find_all("span") ]
            # Parse the date field to make it more searchable
            ticketDetails[0] = \
            d.strptime(ticketDetails[0], "%A, %B %d, %Y").strftime("%Y-%m-%d")
            # Append our results list
        return ticketDetails
