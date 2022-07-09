import numpy as np
import pandas as pd
import gspread
from scipy.stats import zscore
from oauth2client.service_account import ServiceAccountCredentials


#conda install -c conda-forge pyinstaller


#conda install pandas jupyter


#pip install gspread oauth2client df2gspread


#pip install requests


#pip install lxml

#Parameters
insurance = #annually
down_payment = #actual
budget = #quoted
interest_rate = #estimate

#import data
file_key = #filestring

spreadsheet_key = #spreadsheetkey

scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name(file_key, scope)
gc = gspread.authorize(credentials)

book = gc.open_by_key(spreadsheet_key)
worksheet = book.worksheet("Sheet Name")
table = worksheet.get_all_values()

df = pd.DataFrame(table[1:], columns=table[0])
properties = df.apply(pd.to_numeric, errors='ignore')

mortgage = ((properties['Asking Price']-down_payment)/30/12)
interest = mortgage*interest_rate
tax = ((properties['Asking Price']*(properties['Est. Tax Rate']/100))/12)
HOA = properties['HOA'].fillna(0)
properties['Est. Monthly Payment'] = mortgage+interest+tax+HOA+(insurance/12)
properties['Value'] =properties['Est. Monthly Payment']/properties['Sq Ft.']
properties = properties.where(properties['Est. Monthly Payment'] <= budget).dropna(axis=0,subset=['Link'])

numeric_cols = properties.select_dtypes(include=[np.number]).columns
zscores = properties[numeric_cols].apply(zscore)
zscores.head()


neighborhood = zscores[['School Rank','Crime Data']].mean(axis=1)
commute = zscores[['Driving Commute','Transit Commute']].mean(axis=1)
social = zscores[['Nearest Pub']].mean(axis=1)
value = zscores[['Value']].mean(axis=1)
must_haves = zscores[['Dishwasher','Laundry']].mean(axis=1)
nice_to_haves = zscores[['Gym','Balcony','Pool']].mean(axis=1)

properties['total_score'] = (neighborhood)+(commute)+(value)+(social)-(must_haves)-(nice_to_haves)
properties['rank'] = properties['total_score'].rank(ascending = True)
properties[["rank","City","Asking Price",'Est. Monthly Payment','Transit Commute','Nearest Pub']].sort_values("rank")

