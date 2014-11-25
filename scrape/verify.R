
# Load libraries ----------------------------------------------------------

library("RSQLite")
library("lubridate")
library("dplyr")

# Verify the tickets ------------------------------------------------------
# The old tickets data from previous work. Downloaded from:
# http://www.davidgrant.ca/vancouver_sun_parking_tickets_website_screen_scraper
old_db <- paste0("C:/Users/Jonathan/Dropbox/School/Grad/STAT545A/",
                 "stat545a-hw06/stat545a-2013-hw06_baik-jon/data_01_raw/",
                 "parkingtickets.rds")
old_pt <- readRDS(old_db)

# Load the new tickets that we scraped
db <- "scrape/parkingTickets.db"
con <- dbConnect(SQLite(), dbname=db)
dbListTables(con)
new_pt <- dbReadTable(con, "tickets")

# Compare
dim(old_pt)
dim(new_pt)
# Uh oh...

names(old_pt)
names(new_pt)

head(old_pt)
head(new_pt)

# Need to make a new key for each table.
# Will make a composite key from the date-time and plate.
# Let's use dplyr
old_pt <- tbl_df(old_pt)
new_pt <- tbl_df(new_pt)

# First, process the date-time into a common format.
head(old_pt)
old_pt <- old_pt %>%
  mutate(datetime=ymd_hms(datetime)) %>%
  # Also, rename plate to license_plate
  rename(license_plate=plate)
str(old_pt)

head(new_pt)
new_pt <- new_pt %>%
  mutate(datetime=ymd_hm(paste(date, time)))
str(new_pt)

# Now make a new "key" by combining the date-time and the license plates
# old_pt <- old_pt %>%
#   rename(license_plate=plate) %>%
#   mutate(key=paste(datetime, license_plate))
#
# new_pt <- new_pt %>%
#   mutate(key=paste(datetime, license_plate))

old_pt$key[which(!old_pt$key %in% new_pt$key)]
new_pt$key[which(!new_pt$key %in% old_pt$key)]

dim(unique(new_pt))
dim(unique(old_pt))

# OK, using old pt data, get rows that we are missing in new
missing1 <- anti_join(old_pt, new_pt, by = c("datetime", "license_plate"))
missing1

# And the other way
missing2 <- anti_join(new_pt, old_pt, by = c("datetime", "license_plate"))
missing2
