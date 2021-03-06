# -*- coding: utf-8 -*-
"""
Save tickets data into an SQLite data base

@author: Jonathan
"""

import logging
import scrape
import sqlite3
import time
import sys
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description="Scrape parking tickets data")
parser.add_argument("--pages", dest="pages", nargs=2, type=int,
                    metavar=("N1", "N2"),
                    help="Scrape pages between the two given args")
parser.add_argument("--logfile", dest="logfile", type=str,
                    metavar="FILE", help="Name of log file")
args = parser.parse_args()

if __name__ == "__main__":
    # Save log to file
    logfile = args.logfile
    if logfile is None:
        logfile = "tickets2db.log"
    logging.basicConfig(filename=logfile, filemode='w', level=logging.WARNING)
    
    # Initialize the scraper
    scraper = scrape.TicketScraper()
    
    try:
        # Connect to the DB
        con = sqlite3.connect("parkingTickets.db")
        cur = con.cursor()
        
        # Create the table
        table_string = (
            "CREATE TABLE IF NOT EXISTS tickets(" + \
            ",".join(scraper.TICKET_FIELDS) + ")"
            )
        cur.execute(table_string)
        
        # Command for inserting values
        insert_string = (
            "INSERT INTO tickets VALUES(" + 
            ",".join(["?"]*len(scraper.TICKET_FIELDS)) + ")"
            )
        
        # Get the details in given page range
        if args.pages is None:
            print("Getting tickets from pages 1 to " + scraper.MAX_PAGE)
            page_range = range(scraper.MAX_PAGE)
        else:
            # Make sure to subtract 1 because we add 1 later due to the default
            # case when pages are not given as arguments
            if args.pages[1] > scraper.MAX_PAGE:
                page_range = range(args.pages[0]-1, scraper.MAX_PAGE)
            else:
                page_range = range(args.pages[0]-1, args.pages[1])
        
        for page in page_range:
            # Get all tickets on a page, then insert into db
            start = time.time()
            print("Getting tickets on page {} - ".format(page + 1), 
                  flush=True, end="")
            tickets = scraper.getTicketsOnPage(page + 1)
            # Insert to db
            print("Inserting to db - ", flush=True, end="")
            cur.executemany(insert_string, tickets)
            # Commit our changes
            con.commit()
            # Print time
            fin = time.asctime(time.localtime(time.time()))
            print("Time: {:.2f}".format(time.time() - start) + " s - " + fin)
    
    except sqlite3.Error as e:
        if con:
            con.rollback()
        logging.error(e)
        print("Error {}".format(e.args[0]))
        sys.exit(1)
        
    finally:
        # Close the connection after finishing
        if con:
            con.close()
        # Print time
        finish_time = time.asctime(time.localtime(time.time()))
        print("Script finish time: {}".format(finish_time))
        print("At page {} at exit time".format(page + 1))
    
    