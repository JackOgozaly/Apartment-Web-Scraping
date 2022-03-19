# -*- coding: utf-8 -*-
"""
Created on Sat Jan  1 12:34:48 2022

@author: jogoz
"""

import pandas as pd
import re
import numpy as np
pd.options.display.float_format = '{:.2f}'.format



#Version 1 of rent data has no special offer data
v1_rent_data = pd.read_csv(r'C:\Users\jogoz\Rent_Data_Scrape3.csv')

#Version 2 of rent data has special offer info scraped
v2_rent_data = pd.read_csv(r'C:\Users\jogoz\Rent_Data_Scrape4.csv')

#Join in temporary data from my one fuck-up 
v3_rent_data =pd.read_csv(r'C:\Users\jogoz\.spyder-py3\autosave\Rent_Data_Scrape4.csv', header=None)

#Get the proper name and list of columns we want
cols = list(v2_rent_data.columns)

#Fix v3 so it has the column names we want and remove the duplicate date
v3_rent_data.columns = cols
v3_rent_data = v3_rent_data[v3_rent_data['Day_Recorded'] != '2022-01-07']


#Add in the one missing column for v1 and then rearrange cols to match
v1_rent_data['Special_offer'] = np.NaN
v1_rent_data = v1_rent_data[[c for c in cols if c in cols]]

#Combine all our data together
df = pd.concat([v1_rent_data, v2_rent_data, v3_rent_data])


#Correctly format unique id
df['unique_id'] = df['unique_id'].str.strip()
df = df[~df['unique_id'].str.contains('E+',regex=False)]

#True cost of an apartment = (price * lease_term) - special offer

#Challenge: translate special offer text to an actual amount
#Different types of specials: Months free, X off security deposit



special_offer_count = pd.DataFrame(df['Special_offer'].value_counts()).reset_index()
special_offer_count.columns = ['Special_offer', 'Count']


filler_words = ['Transfers excluded.', 'Offer valid on new leases only.', ' with approved credit', ' on Select Apartments', ' on select apartment homes']


def special_offer_cleaner(string): 
    string_og = string
    #Convert to lower case to make text processing easier
    string = string.str.lower()
    #Remove filler phrases that don't impact the special offer
    filler_words = ['transfers excluded.', 'offer valid on new leases only.', ' with approved credit', ' on select apartments', ' on select apartment homes']
    for i in range(len(filler_words)):
        string = string.astype(str).str.replace(filler_words[i], '')
    #Replace written wrods with a numeric
    num_letter = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', '1/2']
    num_num = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '.5']
    for i in range(len(num_letter)):
        string = string.astype(str).str.replace(num_letter[i], num_num[i])
    #Strip whitespace
    string = string.astype(str).str.strip()
    string = pd.DataFrame(string)
    string['original_special_offer'] = string_og
    #Return the string
    return string

#This function cleans up the special offer field
def special_offer_cleaner2 (df): 
    special_offer_list = list(df['Special_offer'])
    og_special_offer_list = list(df['original_special_offer'])
    og_combs = []
    months_off_results = []
    for i in range(len(special_offer_list)): 
        x = special_offer_list[i]
        keywords = ['month off', 'months free', 'off move-in costs', 'weeks off', 'month free']
        
        for keyword in keywords:
            months_off = re.findall(f'((\S+\W){{1,2}}{keyword})', x)
            if months_off:
                months_off = months_off[0]
                months_off= months_off[-1]
            else: 
                months_off = None
            months_off_results.append(months_off)
        og_combs.append((x, months_off_results))
        
    months_off_results = pd.DataFrame(months_off_results)
    months_off_results['keywords'] = keywords * (i+1)
    months_off_results['clean_special_offer'] = np.repeat(special_offer_list, len(keywords))
    months_off_results['original_special_offer'] = np.repeat(og_special_offer_list, len(keywords))
    #Clean up amount column
    months_off_results.columns = ['Amount', 'special_offer_type', 'clean_special_offer', 'original_special_offer']
    months_off_results['Amount'] = months_off_results['Amount'].astype(str).str.replace('$', '')
    months_off_results['Amount'] = months_off_results['Amount'].astype(str).str.replace('"', '')
    #Little more data manipulation to clean it up
    months_off_results= months_off_results.replace('nan', np.NaN)
    months_off_results = months_off_results[months_off_results['Amount'].notnull()]
    months_off_results['Amount'] = months_off_results['Amount'].astype(float)
    #Convert weeks off to months
    months_off_results['Amount'] = np.where(months_off_results['special_offer_type'] == 'weeks off', ((12/52) * months_off_results['Amount']), months_off_results['Amount']  )
    #Simplify special offer type
    months_off_results['special_offer_type'] = months_off_results['special_offer_type'].astype(str).str.replace('month off', 'months free')
    months_off_results['special_offer_type'] = months_off_results['special_offer_type'].astype(str).str.replace('month free', 'months free')
    months_off_results['special_offer_type'] = months_off_results['special_offer_type'].astype(str).str.replace('weeks off', 'months free')
    #Just get the discount in clean columns
    months_off_results['month_discount'] = np.where(months_off_results['special_offer_type'] == 'months free', months_off_results['Amount'], 0)
    months_off_results['move_in_discount'] = np.where(months_off_results['special_offer_type'] == 'off move-in costs', months_off_results['Amount'], 0)
    #Subset Our Data
    months_off_results = months_off_results[['original_special_offer','month_discount','move_in_discount']]
    #Aggregate
    months_off_results = months_off_results.groupby(['original_special_offer'])['month_discount','move_in_discount' ].sum()
    months_off_results= months_off_results.reset_index(drop=False)
    #Return our object
    return months_off_results






#Clean up the special offers
special_offer_count = pd.DataFrame(df['Special_offer'].value_counts()).reset_index()
special_offer_count.columns = ['Special_offer', 'Count']
filler_words = ['Transfers excluded.', 'Offer valid on new leases only.', 
                ' with approved credit', ' on Select Apartments', 
                ' on select apartment homes']
test_string = pd.DataFrame(special_offer_cleaner(special_offer_count['Special_offer']))
function_test = special_offer_cleaner2(test_string)



df = pd.merge(df,function_test, how="left", left_on= 'Special_offer',
                     right_on= 'original_special_offer')

df = df.drop(columns='original_special_offer',
                                 axis=0)

df['month_discount'] = df['month_discount'].fillna(0)
df['move_in_discount'] = df['move_in_discount'].fillna(0)


df['Total_Cost'] = (df['Price'] * (df['lease_term'] - df['month_discount'])) - df['move_in_discount']
df['true_monthly_cost'] = df['Total_Cost']/ df['lease_term']

del(filler_words, function_test, special_offer_count, test_string, v1_rent_data, cols, v2_rent_data, v3_rent_data)


#Convert day recorded to date
df['Day_Recorded'] = pd.to_datetime(df['Day_Recorded'])

#Fix move in date to be date
df = df[df['Move_in_date'] != 'Walk-up']
df = df[df['Move_in_date'] != 'Level']
df['Move_in_date'] = pd.to_datetime(df['Move_in_date'])

#Calculate days till move in
df['days_till_available'] = (df['Move_in_date'] - df['Day_Recorded']).dt.days


#Clean up unique ID/ remove whitespace
df['unique_id'] = df['unique_id'].str.strip()

#Min_price
df['min_price'] = df.groupby('unique_id')['Price'].transform('min')
df['min_price_delta'] = df['Price'] - df['min_price']



#Add in City Data
apartment_city_info = pd.read_csv(r'C:\R Code Directory\Apartment_Data.csv',skipinitialspace=True)
apartment_city_info = apartment_city_info[['URL ', 'Apartment Name', 'City', 'Address']]
df = pd.merge(df, apartment_city_info, how = "left", left_on= 'URL', right_on= 'URL ')
df = df.drop(columns= ['URL '])
del(apartment_city_info)




#pd.set_option('display.float_format', '{:.2f}'.format)



#Let's make a dataset that we can create a model off of
model_df = df 
#Special offer information was not recorded before Decemeber 31, so we exclude
model_df = model_df[model_df["Day_Recorded"] > '2021-12-31']
#Omit all rows that don't contain a floor number
model_df = model_df.dropna(axis=0,subset=['Floor'])
model_df['Floor'] = model_df['Floor'].astype(str)



model_df = model_df[model_df['Floor'].str.match('^[\w\d_-]*$')]



model_df = model_df.sort_values(by=["Day_Recorded", 'URL'])


model_df['dif'] = model_df.groupby('unique_id')['Price'].diff().fillna(0).astype(int)

model_df['days_recorded'] = model_df.groupby('unique_id').cumcount()+1

df.to_csv(r'C:\Users\jogoz\Rent_Scrape_Final.csv', index= False)



#let's just examine courthouse plaza 


courthouse_data = df[df['Apartment Name'] == 'Courthouse Plaza Apartments']


import seaborn as sns
import matplotlib.pyplot as plt


plt.figure(figsize = (15,8))
plt.xticks(rotation=45)
sns.lineplot(data=courthouse_data, x="Day_Recorded", y="Price",  hue="unique_id",
             legend=None)



correlation = courthouse_data['est_vacancy'].corr(courthouse_data['min_price_delta'])
print(correlation)


print(model_df['Day_Recorded'].max())


#%%



#%%


test_df = model_df[model_df['unique_id'] == '73630001501303']




#%%

dc_data = df[df['City'] == 'Washington DC']
dc_data = dc_data[dc_data['Beds'] > 0]
dc_data = dc_data[dc_data['Price'] < 1950]
dc_data =  dc_data[dc_data['Day_Recorded']== pd.to_datetime('today').normalize() ]



sns.lineplot(data= dc_data,x="Day_Recorded", y="est_vacancy",  hue="Apartment Name",
             legend= None)




#%%

sns.scatterplot(data=df, x="est_vacancy", y="min_price_delta",
             legend=None)



#%%

rent_query = df[df['unique_id'] == '101410083L110']
rent_query = rent_query[['Price', 'Move_in_date', 'est_vacancy']]
