
# Load libraries ----------------------------------------------------------

library("RSQLite")
library("lubridate")
library("plyr")
library("dplyr")
library("ggplot2")

# Data exploration --------------------------------------------------------

# Connect to db
con <- dbConnect(drv="SQLite", "scrape/parkingTickets.db")

# List tables and fields
dbListTables(con)
dbListFields(con, "tickets")

# Get the parking tickets database into memory
pt <- dbReadTable(con, "tickets")

# Structure
str(pt)
names(pt)

# How big?
dim(pt)
head(pt)
tail(pt)


# Data processing ---------------------------------------------------------

# Create a new datetime variable
pt$datetime <- ymd_hm(paste(pt$date, pt$time))

# Convert date into actual dates
pt$date <- ymd(pt$date)

# Parse meter number
pt$meter_no[which(pt$meter_no == pt$meter_no[1])] <- NA_character_

# Some plots --------------------------------------------------------------

# Dates
pt_noByDay <- ddply(pt, .(date), summarize,
                    year = year(unique(date)),
                    month = month(unique(date)),
                    wday = wday(unique(date), label = TRUE),
                    total = length(date))

ggplot(pt_noByDay) +
  geom_line(aes(x=date, y=total)) +
  facet_wrap(~ year, scales = "free_x", nrow = 5)

ggplot(pt_noByDay) +
  geom_bar(aes(x=month, y=total), stat = "identity") +
  facet_wrap(~ year, scales = "free_x")

ggplot(pt_noByDay) +
  geom_bar(aes(x=wday, y=total), stat = "identity") +
  facet_wrap(~ year, scales = "free_x")

# Some summaries of data
