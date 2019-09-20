pd.__version__

import pandas as pd
import numpy as np
import itertools as itr
from functools import reduce
import re

import warnings

warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', 300)
pd.set_option('display.max_rows', 1200)

def read(sheet_name = ''):
    return pd.read_excel('.xlsx', sheet_name = sheet_name, sep = ';', encoding = 'cp1251')

def split_df(brand = ''):
    
    df17 = read('2017')
    df18 = read('2018')
    df19 = read('2019')
    
    df17['identifier'] = df17['Бренд'] + df17['широта'].map(str) + df17['долгота'].map(str)
    df18['identifier'] = df18['Бренд'] + df18['широта'].map(str) + df18['долгота'].map(str)
    df19['identifier'] = df19['Бренд'] + df19['широта'].map(str) + df19['долгота'].map(str)
    
    df17 = df17[df17['Бренд'] == '{}'.format(brand)]
    df18 = df18[df18['Бренд'] == '{}'.format(brand)]
    df19 = df19[df19['Бренд'] == '{}'.format(brand)]
    
    #concat_dfs = pd.concat([df17, df18, df19], join = 'outer', axis = 1)
    merged = pd.merge(pd.merge(df17, df18, on = ['identifier'], how = 'outer'), 
                      df19, on = ['identifier'], how = 'outer').fillna(0) 
    
    merged = merged[['identifier', 'Январь_17', 'Февраль_17', 'Март_17', 'Апрель_17', 'Май_17', 'Июнь_17', 
                     'Июль_17', 'Август_17', 'Сентябрь_17', 'Октябрь_17', 'Ноябрь_17', 'Декабрь_17',
                     'Январь_18', 'Февраль_18', 'Март_18', 'Апрель_18', 'Май_18', 'Июнь_18', 
                     'Июль_18', 'Август_18', 'Сентябрь_18', 'Октябрь_18', 'Ноябрь_18', 'Декабрь_18',
                     'Январь_19', 'Февраль_19', 'Март_19', 'Апрель_19', 'Май_19', 'Июнь_19', 
                     'Июль_19', 'Август_19', 'Сентябрь_19', 'Октябрь_19', 'Ноябрь_19', 'Декабрь_19']]
    
    #date_dict_keys = merged.columns[1:]
    date_dict_keys = list(range(0, 36))
    date_dict_vals = pd.to_datetime(pd.date_range(start = '01-01-2017',
                                                  periods = len(merged.columns) - 1, 
                                                  freq = 'MS'))
    date_dict_vals = [i.date() for i in date_dict_vals]
    date_dict = dict(zip(date_dict_keys, date_dict_vals))
    
    return merged, date_dict

merged, date_dict = split_df('')

def enchantment(df):
    
    # list with column's idx
    date = df.iloc[:, 1: len(df)]
    date['tuple'] = [list(np.where(date.iloc[row] == 1)[0]) for row in range(len(date))]
    # get stard and end of where 1 start and end
    def make_shit(x):   
        s = pd.Series(x)   
        return s.groupby(s.diff().ne(1).cumsum()).agg(['first','last']).values.tolist()

    date['shit'] = date['tuple'].apply(make_shit)
    # replace idx with dates
    date = date.assign(actual_date = date['shit'])
    
    val = pd.Timestamp('2000-01-01 00:00:00', freq = 'MS')
    date['actual_date'] = date['shit']\
                                .apply(lambda x: [[date_dict.get(key, val) for key in y] for y in x])
    # add identifier
    date['identifier'] = merged['identifier']
    
    # if version 25+
    if re.findall(r'\d+', pd.__version__)[1] == '25':
        date_final = date.explode('actual_date')
        date_final[['start_date', 'end_date']] = pd.DataFrame(date_final.pop('actual_date')\
                                                    .values.tolist(), index = date_final.index)
    
    # if lower
    else:
        dt = date.pop('actual_date')
        df = date.loc[date.index.repeat(dr.str.len())]
        df[['date_start','date_end']] = pd.DataFrame(np.concatenate(s), index = df.index)
        df = df.reset_index(drop = True)

    date_final.drop(['tuple', 'shit'], axis = 1, inplace = True)
           
    return date_final

date_df = enchantment(merged)

date_df.to_csv('.csv', sep = ';', encoding = 'cp1251', index = False)
