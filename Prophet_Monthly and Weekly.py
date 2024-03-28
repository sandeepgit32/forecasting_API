#!/usr/bin/env python
# coding: utf-8

# In[7]:


import numpy as np
import warnings
import itertools
import pandas as pd
import statsmodels.api as sm
import seaborn as sns
import matplotlib.pyplot as plt
from prophet import Prophet
from prophet.plot import add_changepoints_to_plot
import matplotlib.pyplot as plt 
df = pd.read_excel("C:\\Users\\user1\\Documents\\Data for Demo_V4.xlsx")
df = df.sort_values('Order_Date')
df.isnull().sum()
missing_col = ['Sales']
for i in missing_col:
    df.loc[df.loc[:,i].isnull(),i]=df.loc[:,i].mean()
sns.boxplot(data=df,x=df['Sales'])
Q1=df['Sales'].quantile(0.25)
Q3=df['Sales'].quantile(0.75)
IQR=Q3-Q1
print(Q1)
print(Q3)
print(IQR)
Lower_Whisker = Q1-1.5*IQR
Upper_Whisker = Q3+1.5*IQR
print(Lower_Whisker, Upper_Whisker)
df = df[df['Sales'] < Upper_Whisker]
df.head()


# In[8]:


df1 = pd.DataFrame()
df1['ds'] = pd.to_datetime(df['Order_Date'])
df1['y'] = df['Sales']
df1.head()


# In[9]:


m = Prophet()
m.fit(df1)
future = m.make_future_dataframe(periods=12 * 2,
                                 freq='M')  # 'M' for monthly and 'W' stands for weekly frequency.


# In[10]:


forecast = m.predict(future)
forecast[['ds', 'yhat', 'yhat_lower',
          'yhat_upper', 'trend',
          'trend_lower', 'trend_upper']].tail()


# In[11]:


fig1 = m.plot(forecast, include_legend=True)
fig2 = m.plot_components(forecast)


# In[12]:


fig = m.plot(forecast)
a = add_changepoints_to_plot(fig.gca(),
                             m, forecast)

