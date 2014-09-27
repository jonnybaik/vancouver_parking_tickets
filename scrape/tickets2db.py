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

if __name__ == "__main__":
    # Save log to file
    logging.basicConfig(filename='tickets2db.log', filemode='w',
                        level=logging.WARNING)
    # Initialize the scraper
    scraper = scrape.TicketScraper()
    
    try:
        # Connect to the DB
        con = sqlite3.connect("parkingTickets.db")
        cur = con.cursor()
        
        # Create the table
        table_string = (
            "CREATE TABLE tickets(" + \
            ",".join(scraper.TICKET_FIELDS) + ")"
            )
        # cur.execute("DROP TABLE IF EXISTS tickets")
        cur.execute(table_string)
        
        # Command for inserting values
        insert_string = (
            "INSERT INTO tickets VALUES(" + 
            ",".join(["?"]*len(scraper.TICKET_FIELDS)) + ")"
            )
        
        # Get the details on the first page
        for page in range(scraper.MAX_PAGE):
            # Get 30 tickets at a time, then insert into db
            start = time.time()
            print("Getting tickets on page {} - ".format(page + 1), 
                  flush=True, end="")
            tickets = scraper.getTicketsOnPage(page + 1)
            cur.executemany(insert_string, tickets)
            # Commit our changes
            con.commit()
            # Print time
            print("Time: {:.2f}".format(time.time() - start) + " sec")
    
    except sqlite3.Error as e:

        if con:
            con.rollback()
        print("Error {}".format(e.args[0]))
        sys.exit(1)
        
    finally:
        # Close the connection after finishing
        if con:
            con.close()
    
    