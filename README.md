# Apartment Price Web Scraping

Hello! This project is my attempt to collect apartment data from Equity Residential apartments and analyze price fluctuations. Equity Residential is the second largest apartment owner in the United States and everyday their prices are updated, sometimes fluctuating dramatically. My goal for this project was to determine when is the best time to sign a lease.  


![grab-landing-page](https://github.com/JackOgozaly/Apartment-Web-Scraping/blob/main/Graphs/Rent_Data.gif?raw=true)

# How It Works

Equity Residential has 284 apartment complexes across the United States and every apartment listing follows a standard-ish format. Everyday, this webscraper collects all the important info from every listing, such as Price, Beds, Baths, etc., and then cleanly puts the data into a dataframe. On averge, there are 3,700 listing collected each day.

![grab-landing-page](https://github.com/JackOgozaly/Apartment-Web-Scraping/blob/main/Graphs/web_scraping_animated.gif?raw=true)

From these fields a unique ID is generated, allowing me to track how Equity Residential's pricing algorithm works. 

# What Makes This Project Special

As far as I'm aware, this is one of the more thorough datasets containing rent data. The biggest feature is the inclusion of a daily estimated vacancy figure. This field allows for a more thorough examination of Equity Residential's pricing algorithm. 
