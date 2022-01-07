# -*- coding: utf-8 -*-
"""
Created on Sat Jan  1 12:34:48 2022

@author: jogoz
"""

import pandas as pd
import re
import numpy as np

v1_rent_data = pd.read_csv(r'C:\Users\jogoz\Rent_Data_Scrape3.csv')


v2_rent_data = pd.read_csv(r'C:\Users\jogoz\Rent_Data_Scrape4.csv')


rent_query = v2_rent_data[v2_rent_data['Beds'] > 0]
rent_query = rent_query[rent_query['sq.ft'] > 650]


#True cost of an apartment = (price * lease_term) - special offer

#Challenge: translate special offer text to an actual amount
#Different types of specials: Months free, X off security deposit



special_offer_count = pd.DataFrame(v2_rent_data['Special_offer'].value_counts()).reset_index()
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
    
    #string = string[string.astype(str).str.contains("deposit special")==False]

    string = pd.DataFrame(string)
    string['original_special_offer'] = string_og
    
    #Return the string
    return string


test_string = pd.DataFrame(special_offer_cleaner(special_offer_count['Special_offer']))

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


function_test = special_offer_cleaner2(test_string)



v2_rent_data = pd.merge(v2_rent_data,function_test, how="left", left_on= 'Special_offer',
                     right_on= 'original_special_offer')

v2_rent_data = v2_rent_data.drop(columns='original_special_offer',
                                 axis=0)

v2_rent_data['month_discount'] = v2_rent_data['month_discount'].fillna(0)
v2_rent_data['move_in_discount'] = v2_rent_data['move_in_discount'].fillna(0)



v2_rent_data['Total_Cost'] = (v2_rent_data['Price'] * (v2_rent_data['lease_term'] - v2_rent_data['month_discount'])) - v2_rent_data['move_in_discount']
v2_rent_data['true_monthly_cost'] = v2_rent_data['Total_Cost']/ v2_rent_data['lease_term']



#%%

