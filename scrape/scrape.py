# -*- coding: utf-8 -*-
"""
Add description here
"""

from bs4 import BeautifulSoup
import requests
import sqlite3

#%% Step 1: Get the App Key from the Vancouver Sun page
# Open the parking tickets search page from vancouversun.com.
# Grab the app key, and then retrieve the page with results to scrape
url = "http://www.vancouversun.com/parking/basic-search.html"
page = requests.get(url)

# Check if we got the page
page.ok

# Grab the content
content = page.content

# Parse the page using Beautiful Soup to find the app key
soup = BeautifulSoup(content)

# Get the app key. It should be contained in the div layer with id="cxkg",
# which holds a link with href="http://b2.caspio.com/dp.asp?AppKey=[APPKEY]"
# Grab the link to the db page and extract the App Key
AppKey = soup.find("div", id="cxkg").find("a")["href"].split("AppKey=")[1]

#%% Step 2: Navigate to the web data base using the AppKey

# Now we will open a page from the b2.caspio.com page instead of loading 
# all the objects from vancouversun.com

# Construct the URL using the AppKey and the Page Number
url_root = "http://b2.caspio.com/"
url_template = url_root + "dp.asp?AppKey=%s&RecordID=&PageID=2&" + \
    "PrevPageID=1&cpipage=%d&CPISortType=&CPIorderBy="
pageNum = 1

# Construct the URL
url = url_template % (AppKey, pageNum)

# Get the page
page = requests.get(url)

# Did we get the page?
page.ok

#%% Step 3: Parse the page to get all the "Details" links

# Beautify
soup = BeautifulSoup(page.content)

# Now get some data!
# The name of the fields on a details page
dataName = ["date", "time", "license_plate", "province", "vehicle_make", 
            "street_no", "street_name", "street_side", "meter_no", 
            "offence_type", "offence_detail", "bylaw_no", "bylaw_sect", 
            "fine", "fine_early", "impound_requested", "ticket_no"]

# Parse all the links on one page
results = []
for link in soup.find_all("a", text="Details"):
    # Grab the actual link to the extra details page
    detailLink = link.get("href")
    # Get the page
    detailPage = requests.get(url_root + detailLink)
    if(detailPage.ok) :
        # Parse the content
        detailSoup = BeautifulSoup(detailPage.content)
        # Get the fields
        detailText = detailSoup.find_all("span")
        # Append our results list
        results.append([span.getText() for span in detailText])
    else :
        print("Failed to load page")
    


#%% Function for parsing a details page

# New url
url = "http://b2.caspio.com/dp.asp?AppKey=" + AppKey

# The http POST data to get the first page.
payload = { 
    "AppKey" : AppKey,
    "ComparisonType3_1" : "LIKE",
    "MatchNull3_1" : "N",
    "Value3_1" : "",
    "ComparisonType5_1" : ">=",
    "MatchNull5_1" : "N",
    "Value5_1" : "",
    "ComparisonType5_2" : "<=",
    "MatchNull5_2" : "N",
    "Value5_2" : "",
    "ComparisonType6_1" : "=",
    "MatchNull6_1" : "N",
    "Value6_1" : "",
    "FieldName1" : "HTML Block 1",
    "Operator1" : "",
    "NumCriteriaDetails1" : "1",
    "FieldName2" : "HTML Block 4",
    "Operator2" : "",
    "NumCriteriaDetails2" : "1",
    "FieldName3" : "DE_cLicencePlate",
    "Operator3" : "OR",
    "NumCriteriaDetails3" : "1",
    "FieldName4" : "HTML Block 2",
    "Operator4" : "",
    "NumCriteriaDetails4" : "1",
    "FieldName5" : "BlockFull",
    "Operator5" : "AND",
    "NumCriteriaDetails5" : "2",
    "FieldName6" : "DE_cStreetName",
    "Operator6" : "OR",
    "NumCriteriaDetails6" : "1",
    "FieldName7" : "HTML Block 3",
    "Operator7" : "",
    "NumCriteriaDetails7" : "1",
    "PageID" : "2",
    "GlobalOperator" : "AND",
    "NumCriteria" : "7",
    "Search" : "1",
    "PrevPageID" : "1"
    }

# Start a new session
session = requests.Session()

# This gets the first page!
root_url = "http://b2.caspio.com/"
page = session.post(root_url + "dp.asp", data=payload)

# Now to get the other pages, find the "Next Page" link, if it exists
soup = BeautifulSoup(page.content)
nextLink = soup.find("img", attrs={"alt" : "Next"}).find_parent("a")["href"]

nextPage = session.get(root_url + nextLink)

soup = BeautifulSoup(nextPage.content)
