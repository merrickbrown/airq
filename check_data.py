#!/usr/bin/env python3
import pandas as pd
import dataset

db = dataset.connect('sqlite:///data/sqlite/aq.db')

# wb = pd.read_csv('https://raw.githubusercontent.com/brendanrbrown/stor155_sp21/main/data/wb_lifexpec.csv')
# # actually creates the table
# tb = db['testtab']
# tb.insert(wb.to_dict())
print(dir(db))
#wb = pd.read_sql('testab', con = db)

#print(wb.head())
