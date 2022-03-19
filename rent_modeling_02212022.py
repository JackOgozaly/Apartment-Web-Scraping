# -*- coding: utf-8 -*-
"""
Created on Sun Feb 20 13:30:06 2022

@author: jogoz
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


#Read in our data
model_data = pd.read_csv(r'C:\Users\jogoz\Rent_Scrape_Final.csv')

#Seperate or date variable so we can one hot encode easier
model_data['Day_Recorded'] = pd.to_datetime(model_data['Day_Recorded'])
model_data['Day_Recorded_Weekday'] = model_data['Day_Recorded'].dt.day_name()
model_data['Day_Recorded_Month'] = model_data['Day_Recorded'].dt.month_name()

#One hot encode
dummy_vars = pd.get_dummies(model_data, columns=['City', 'Day_Recorded_Weekday', 'Day_Recorded_Month'])

#Drop columns that aren't needed
data = dummy_vars.drop(['Price', 'Move_in_date', 'Amenity','URL', 'building_id', 'unit_id',
       'Special_offer', 'Day_Recorded','unique_id',
       'month_discount', 'move_in_discount', 'Total_Cost', 'min_price', 'min_price_delta', 'Apartment Name',
       'Address', 'Floor', 'City_Washington DC', 'Day_Recorded_Weekday_Friday',
       'Day_Recorded_Month_December'], axis=1)

#Set random seed
np.random.seed(0)
#Train Test Split
df_train, df_test = train_test_split(data, train_size = 0.7, test_size = 0.3, random_state = 100)

#X, Y for train
x_train = df_train.drop(['true_monthly_cost'], axis=1)
y_train = df_train['true_monthly_cost']
#X, Y for test
x_test = df_test.drop(['true_monthly_cost'], axis=1)
y_test = df_test['true_monthly_cost']


import statsmodels.api as sm
X_train_lm = sm.add_constant(x_train)

lr_1 = sm.OLS(y_train, x_train).fit()

print(lr_1.summary())



y_pred = lr_1.predict(x_test)


#%%
print(r2_score(y_true = y_test, y_pred = y_pred))

from sklearn.metrics import mean_absolute_error

print(mean_absolute_error(y_true = y_test, y_pred = y_pred, multioutput='raw_values'))



#%%


#To do:
#Clean up the Floor Variable









#%%
# Checking for the VIF values of the variables. 
from statsmodels.stats.outliers_influence import variance_inflation_factor

# Creating a dataframe that will contain the names of all the feature variables and their VIFs
vif = pd.DataFrame()
vif['Features'] = x_train.columns
vif['VIF'] = [variance_inflation_factor(x_train.values, i) for i in range(x_train.shape[1])]
vif['VIF'] = round(vif['VIF'], 2)
vif = vif.sort_values(by = "VIF", ascending = False)
print(vif)


#%%



#%%



X = data.drop(['true_monthly_cost'], axis=1)
y = data['true_monthly_cost']



np.random.seed(0)
df_train, df_test = train_test_split(data, train_size = 0.7, test_size = 0.3, random_state = 100)


regr = linear_model.LinearRegression()
regr.fit(X, y)

print(regr.coef_)

#%%


