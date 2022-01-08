# Apartment Price Web Scraping

Hello! This project is my attempt to collect apartment data from Equity Residential apartments and analyze price fluctuations. Equity Residential is the second largest apartment owner in the United States and everyday their prices are updated, sometimes fluctuating dramatically. My goal for this project was to determine when is the best time to sign a lease.  


# How It Works

Equity Residential has 284 apartment complexes across the United States and every apartment listing follows a standard-ish format. Everyday, this webscraper collects all the important info from every listing, such as Price, Beds, Baths, etc., and then cleanly puts the data into a dataframe. On averge, there are 3,700 listing collected each day.

![grab-landing-page](https://github.com/JackOgozaly/Apartment-Web-Scraping/blob/main/web_scraping_animated.gif)

From these fields a unique ID is generated, allowing me to track how Equity Residential's pricing algorithm works. 

