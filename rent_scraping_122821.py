# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 18:56:31 2021

@author: jogoz
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import numpy as np


apartment_listings = pd.read_csv(r'C:\R Code Directory\Apartment_Data.csv',skipinitialspace=True)
apartment_listings = pd.DataFrame(apartment_listings)
apartment_links = list(apartment_listings['URL '])


og_combs = []
for i in range(len(apartment_links)):
  URL= apartment_links[i]
  print(URL)
  page = ''
  while page == '':
    try:
        page = requests.get(URL)
        break
    except:
        print("Connection refused by the server..")
        print("Let me sleep for 5 seconds")
        print("ZZzzzz...")
        time.sleep(5)
        print("Was a nice sleep, now let me continue...")
        continue
  soup = BeautifulSoup(page.content, 'html.parser')
  for j in range(0,4):
      results = soup.find(id=f'bedroom-type-{j}')
      if results is None:
          pass
      else: 
         job_elems = results.find_all('div', class_='col-xs-12 unit-expanded-card')
         word= "to be notified"
         job_text = str(job_elems)
         if word in job_text:
           continue
         combs1= []
         for job_elem in job_elems:
           title_elem = job_elem.find('span', class_='pricing')
           company_elem = job_elem.find('div', class_='col-xs-4 specs')
           other_amenity= job_elem.find('div', class_='amenities col-xs-12')
           x= title_elem.text.strip()
           y= company_elem.text.strip()
           z= other_amenity.text.strip()
           combs1.append((x, y,z))
         df2 = pd.DataFrame(combs1)
         if df2.empty:
             continue
         df2.columns = ['Price', 'Misc', 'Amenity']
         df2["URL"]= URL
         
         #Get unit ID
         job_elems = results.find_all('div', class_='units')
         your_string = str(job_elems)
         test_str = your_string
         res = [i for i in range(len(test_str)) if test_str.startswith("unitId:", i)]
         x= res
         y=  [x+16 for x in res]
         unit_id_data= []
         for i in range(len(x)):
            x1 = x[i]
            y1 = y[i]
            test = your_string[x1:y1]
            unit_id_data.append(test)
          #Get Building ID Data
         test_str = your_string
         res = [i for i in range(len(test_str)) if test_str.startswith(" buildingId:", i)]
         x= res
         y=  [x+16 for x in res]
         building_id_data= []
         for i in range(len(x)):
            x1 = x[i]
            y1 = y[i]
            test = your_string[x1:y1]
            building_id_data.append(test)
         df2['building_id']= pd.Series(building_id_data)
         df2['unit_id'] = pd.Series(unit_id_data)
         og_combs.append(df2)
og_combs = pd.concat(og_combs)


#Split up and seperate the column with all the unit details
df2 = og_combs
df2 = df2.reset_index(drop=True)
df2.index = df2.index.set_names(['index1'])
df2 = df2.reset_index()



df3 = df2.Misc.str.split(expand=True)
df3 = df3.reset_index(drop=True)
df3.index = df3.index.set_names(['index1'])
df3 = df3.reset_index()

#Rows that are correctly formatted from the start
correct_format_rows = df3[df3[11] == "Floor"]
correct_format_rows = correct_format_rows[correct_format_rows[14] != "Top"]
correct_format_rows = correct_format_rows[~correct_format_rows[14].isin(['Top', 'Above'])]


#Fix listings that have no floor information
available_df = df3[df3[11] == "Available"]
if ~available_df.empty:
    available_df[14] = available_df[12]
    available_df[12] = None
    correct_format_rows = pd.concat([available_df,correct_format_rows])


#Fix listings that have a floor name instead of number
misc_floor = df3[~df3[11].isin(['Floor', 'Available'])]
if ~misc_floor.empty:
    misc_floor[12] = misc_floor[11] + " " + misc_floor[12]
    wrong_available = misc_floor[misc_floor[13] != 'Available']
    if ~wrong_available.empty: 
        wrong_available = wrong_available[wrong_available[13] != 'Floor']
        wrong_available[14] = wrong_available[13]
        misc_floor2 = misc_floor[misc_floor[13] == 'Available']
        misc_floor2 = pd.concat([wrong_available, misc_floor2])
        wrong_available2 = misc_floor[misc_floor[13] == 'Floor']
        if ~wrong_available2.empty:
            wrong_available2[14] = wrong_available2[15]
            misc_floor = pd.concat([wrong_available2, misc_floor2])
        else: 
            misc_floor = misc_floor2
    correct_format_rows = pd.concat([misc_floor,correct_format_rows])
       
    
#Fix listings that have extra words to denote the floor
top_rows = df3[df3[14].isin(['Top', 'Above'])]
if ~top_rows.empty: 
    top_rows = top_rows.drop([13,14,15], axis=1) 
    top_rows.rename(columns = {16:13,17: 14}, 
          inplace = True)
    #top_rows = top_rows.T.reset_index(drop=True).T
    correct_format_rows = pd.concat([top_rows,correct_format_rows])


#Filter for just the columns we want
df3 = correct_format_rows
cols = [0,2,4,7,9,13,15]
df = df3[df3.columns[cols]]
df.columns= ['index1', 'lease_term', "Beds",'Baths','sq.ft','Floor','Move_in_date']


df = pd.merge(df, df2, how="inner", on= "index1")
df = df.drop(['index1'], axis=1)


#Calculate Vacancy
vacancy_df = df.groupby('URL').size()
vacancy_df = vacancy_df.reset_index()
vacancy_df.columns = ['URL', 'empty_apartments']
vacancy_df = pd.merge(vacancy_df, apartment_listings, how = "inner", left_on= 'URL', right_on='URL ')
vacancy_df['est_vacancy'] = vacancy_df['empty_apartments'] / vacancy_df['Units']
vacancy_df['complex_id'] = vacancy_df.index + 1
vacancy_df['complex_id']= vacancy_df['complex_id'].astype(str).str.zfill(4)
vacancy_df = vacancy_df[['est_vacancy', 'URL', 'complex_id']]


#Clean up our dataframe
df =df[df['Floor'] != "Available"]
df =df[~df.Floor.astype('str').str.contains("/")]


df["Price"]= df["Price"].str.replace('[^\w\s]','')
df['Amenity'] = df['Amenity'].str.split()
df = df.drop(['Misc'], axis=1)


df = df[['Price', 'lease_term','Beds', 'Baths', 'sq.ft', 'Floor', 'Move_in_date', 'Amenity',
       'URL', 'building_id', 'unit_id']]

#Add in a date column
df["Day_Recorded"] = pd.to_datetime('today').normalize()

#Clean up building id and unit id
df['building_id'] = df['building_id'].str.replace('buildingId: ', '')
df['building_id'] = df['building_id'].str.replace(',', '')
df['unit_id'] = df['unit_id'].str.replace('unitId: ', '')
df['unit_id'] = df['unit_id'].str.replace('-->', '')
df['unit_id'] = df['unit_id'].str.replace('-', '')
df['unit_id'] = df['unit_id'].str.replace('<', '')


#Add in vacancy data
df = pd.merge(df, vacancy_df, how="left", on= "URL")


df = df.fillna(value=np.nan)

#Create unique ID
df['unique_id'] = df['sq.ft'] + df['Floor'].fillna('') + df['complex_id'] + df['building_id'] + df['unit_id']
df['unique_id']= df['unique_id'].str.replace(' ', '')

#Drop complex id 
df = df.drop(['complex_id'], axis=1)


df['Floor'] = df['Floor'].str.replace('Available', '')


df.to_csv('Rent_Data_Scrape3.csv', mode='a', index=False, header=False)

