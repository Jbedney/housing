#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# In[ ]:


#conda install -c conda-forge pyinstaller


# In[ ]:


#conda install pandas jupyter


# In[ ]:


#pip install gspread oauth2client df2gspread


# In[ ]:


#pip install requests


# In[ ]:


#pip install lxml


# In[ ]:


scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('filename', scope)
gc = gspread.authorize(credentials)


# In[ ]:


spreadsheet_key = 
book = gc.open_by_key(spreadsheet_key)
worksheet = book.worksheet("Sheet Name")
table = worksheet.get_all_values()


# In[ ]:


df = pd.DataFrame(table[1:], columns=table[0])
properties = df.apply(pd.to_numeric, errors='ignore')


# In[ ]:


#Parameters
insurance = #annually
down_payment = #actual
budget = #quoted
interest_rate = #estimate


# In[ ]:


mortgage = ((properties['Asking Price']-down_payment)/30/12)
interest = mortgage*interest_rate
tax = ((properties['Asking Price']*(properties['Est. Tax Rate']/100))/12)
HOA = properties['HOA'].fillna(0)
properties['Est. Monthly Payment'] = mortgage+interest+tax+HOA+(insurance/12)
properties['Value'] =properties['Est. Monthly Payment']/properties['Sq Ft.']
properties = properties.where(properties['Est. Monthly Payment'] <= budget).dropna(axis=0,subset=['Link'])


# In[ ]:


from scipy.stats import zscore
import numpy as np
numeric_cols = properties.select_dtypes(include=[np.number]).columns
zscores = properties[numeric_cols].apply(zscore)
zscores.head()


# In[ ]:


neighborhood = zscores[['School Rank','NJ']].mean(axis=1)
commute = zscores[['Driving Commute','Transit Commute']].mean(axis=1)
social = zscores[['Nearest Pub']].mean(axis=1)
value = zscores[['Value']].mean(axis=1)
must_haves = zscores[['Dishwasher','Laundry']].mean(axis=1)
nice_to_haves = zscores[['Gym','Balcony','Pool']].mean(axis=1)


# In[ ]:


properties['total_score'] = (neighborhood)+(commute)+(value)+(social)-(must_haves)-(nice_to_haves)
properties['rank'] = properties['total_score'].rank(ascending = True)
properties[["rank","City","Asking Price",'Est. Monthly Payment','Transit Commute','Nearest Pub']].sort_values("rank")

