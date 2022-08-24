#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 10:23:52 2022

@author: jackogozaly
"""

#from itertools import count
import matplotlib
from matplotlib.animation import FuncAnimation
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

#Read in our data
df = pd.read_csv(r'/Users/jackogozaly/Desktop/Python_Directory/Rent_Scraping/Apartment_Data_Clean.csv')

#Filtering and sorting
dc_data = df[df['City'] == 'Washington DC']
dc_data = dc_data.sort_values('Day_Recorded')

#Do a group by avg
plot_df = dc_data.groupby(['Day_Recorded', 'Beds'])['Price'].mean().reset_index(drop=False)
plot_df['Day_Recorded'] = pd.to_datetime(plot_df['Day_Recorded'])
plot_df['Beds'] = plot_df['Beds'].astype(int)

#Display gif in spyder
#%matplotlib qt

#Create our plot
fig, ax = plt.subplots(figsize = (18,14))
fig.set_tight_layout(True)


#Our animate function
def animate(i):
    #Clear axis
    plt.cla()
    #Use five thirty eight theme 
    plt.style.use('fivethirtyeight')
    
    data = plot_df.iloc[:int(i+1)] 
    fig = sns.lineplot(data= data, x= data['Day_Recorded'], y = data['Price'], 
                       hue = 'Beds', ax = ax,
                       ci = None)
    
    
    #Set our axis
    ax.set_xlim(plot_df['Day_Recorded'].min(), plot_df['Day_Recorded'].max())
    ax.set_ylim(0, plot_df['Price'].max())

    
    #Formatting stuff
    fig.set_xlabel("\nDay Recorded")
    fig.set_ylabel("Price\n")
    x_dates = plot_df['Day_Recorded'].dt.strftime('%b-%Y').unique()
    ax.set_xticklabels(labels=x_dates, rotation=30, ha='right')
    ax.set_title(f"Average Rent Price By Bedroom in DC as of {data['Day_Recorded'].max().strftime('%B %Y')}",
                 fontweight="bold")
    sns.despine()


#Call our function and animate
anim = FuncAnimation(fig, animate, frames=len(plot_df),
                                         interval=1,
                                         repeat=True)


#Save our gif
writergif = matplotlib.animation.PillowWriter(fps=30) 
anim.save('/Users/jackogozaly/Desktop/Python_Directory/Rent_Scraping/Test_Gif.gif', writer=writergif)



