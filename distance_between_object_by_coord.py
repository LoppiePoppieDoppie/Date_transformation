# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 11:31:33 2020

@author: DMatveev
"""

import pandas as pd
import numpy as np

from numba import jit
import datetime




@jit(nopython = True)
def dist_array(rows, cols, lat_obj1, lat_obj2, long_obj1, long_obj2):
    '''
    Calculate distance beween each competitior/OOH object and client store
    
    args:
        rows         - client's objects (stores)
        cols         - object func calculate distance to (competitor's stores or OOH)
        lat_obj1     - client object latitude
        lat_obj2     - competitor object latitude 
        long_obj1    - client object longitude
        long_obj2    - competitor object longitude
        
    return:
        {np.array} filled with distances between objects in meters 
    '''
    res = np.empty((rows, cols))
    for i in range(rows):
        for j in range(cols):
            res[i, j] = np.arccos(np.sin(np.radians(lat_obj1[i])) * np.sin(np.radians(lat_obj2[j])) +\
                                  np.cos(np.radiana(lat_obj1[i])) * np.cos(np.radians(lat_obj2[j])) *\
                        np.cos(np.radians(long_obj1[i] - long_obj2[j]))) * 6371210
    
    return res




@jit(nopython = True)
def binary_array(distance_array, rows, cols, threshold):
    '''
    Mark array elements from previous function with: 
    - 1 if distance between cliet's object and competitor's object is within defined threshold
    - 0 if it not, thus bigger or smaller
    
    args:
        distance_array      - array of distances from previous func
        rows, cols          - shape of matrix, same as in previous func
        threshold           - min and max dist between objects in meters(min, max)
        
    return:
        {np.array} array filled with [0, 1] values 
    '''
    minimum, maximum = threshold[0], threshold[1]
    res = np.empty((rows, cols))
    for i in range(rows):
        for j in range(cols):
            if distance_array[i, j] > minimum and distance_array[i, j] <= maximum:
                res[i, j] = 1
            else:
                res[i, j] = 0
                
    return res




def nearest_monday(open_date, close_date, monday_start = '', monday_end = ''):
    '''
    For each competitor's object or OOH there are open and close date.
    In case ojects wasn't open in monday (it's can be suturday or other day), this func recalculate nearest monday for each object
    max date = 2030-01-01 
    
    args:
        open_date       - date when the competitor's object was opened
        close_date      - date when the competitors's object was closed
        monday_start    - model's period start date where week starts from monday
        monday_end      - model's period end date where week starts from monday
        
    return:
        nearest_open    - {list} each [i] is monday [i] object was opened
        nearest_close   - {list} each [i] is monday [i] object was closed
        monday_week     - {DatetimeIndex} series filled with model daterange(start_model_date, end_model_date)
    '''
    try:
        open_date = pd.to_datetime(open_date, format = '%Y-%m-%d')
        close_date = pd.to_datetime(close_date, format = '%Y-%m-%d')
    except ValueError:
        open_date = pd.to_datetime(open_date, format = '%Y.%m.%d')
        close_date = pd.to_datetime(close_date, format = '%Y.%m.%d')
        
    max_date = pd.Timestamp('2030-01-01')
    monday_week = pd.date_range(start = monday_start, end = monday_end, freq = 'W-MON')
    
    # transform date from gregorian
    open_greg = open_date.apply(lambda x: x.toordinal()).values
    close_greg = close_date.replace(np.nan, max_date).apply(lambda x: x.toordinal()).values
    monday_greg = list(map(lambda x: x.toordinal(), monday_week.tolist()))
    
    # find closest monday for object
    def closest(*args, date_list):
        res0 = [monday_greg[np.abs((i - monday_greg)).argmin()] for i in range(date_list)]
        res = list(map(lambda x: datetime.datetime.fromordinal(x), res0))
        return res
    
    nearest_open = closest(date_list = open_greg)
    nearest_close = closest(date_list = close_greg)
    
    return nearest_open, nearest_close, monday_week




def dist_feature(file_name, client, competitor, competitor_latitude, client_latitude, competitor_longitude, client_longitude, 
                 threshold_tuple, open_date, close_date, model_start_date, model_end_date):
    '''
    from previously defined functions get competitor object open and close dates, and according to binary array fill in list with:
        - 1 for competitor period(open, close) if there are competitors objects opened for [i] client's object
        - 0 for competitor period(open, close) otherwise
        and sum values for same client objects
    
    args:
        file_name                  - name of file with client and competitor/OOH objects, latitude, longitude and open-close dates
        client                     - column of client's objects names 
        competitor                 - column of competitor's objects names
        competitor_latitude        - column of competitor's latitude
        client_latitude            - column of client's latitude
        competitor_longitude       - column of competitor's longitude
        client_longitude           - column of client's longitude
        threshold_tuple            - interval (min_dist, max_dist) between objects you need to calculate feature within in metres
        open_date                  - column with competitor open dates
        close_date                 - column with competitor close dates
        model_start_date           - first model's monday
        model_end_date             - the last monday of model
        
    return:
        {pd.DataFrame} with date, object_name and value
        
    e.g.:
        comp    comp_latitude    comp_longitude    client    client_latitude    client_longitude    comp_open_date    comp_close_date
        1       30.3746659	     60.0453568        store_1   59.9268	        30.3161	             2016-04-04       2019-11-08
        2       30.3144672	     59.9571587        store_2   59.9258	        30.3144                               
        n       30.338264	     59.862598         store_n   60.0264	        30.2229              2016-04-11       2019-06-04
        
                                                                        to
        date          client_store      value   
        2016-03-28    store_1           0
        2016-04-04    store_1           1
        2016-04-11    store_1           2
        2016-04-18    store_1           2
                                                             
    '''
    try:
        df = pd.read_csv('%s.csv'%(file_name), sep = ';', encoding = 'cp1251')
    except FileNotFoundError:
        df = pd.read_excel('%s.xlsx'%(file_name), encoding = 'cp1251')
     
        
    ####################### define all args #######################    
    self_obj, model_obj = df[competitor].dropna(), df[client].dropna()
    # select columns with objects to define array shape
    rows, cols = len(self_obj), len(model_obj)
    # select columns with latitude for each object
    lat_obj1, lat_obj2 = df[competitor_latitude].dropna().values, df[client_latitude].dropna().values
    # select columns with longitude for each object
    long_obj1, long_obj2 = df[competitor_longitude].dropna().values, df[client_longitude].dropna().values
    # select columns with open and close date of the second object
    open_date = df[open_date].dropna()
    close_date = df.iloc[: len(open_date), ]
    
    ####################### init all funcs ####################### 
    open_, close_, monday_ = nearest_monday(open_date, close_date, model_start_date, model_end_date)
    comp_date_arr = np.stack((np.asarray(open_), np.asarray(close_)), axis = 1)
    obj_arr = model_obj.astype('str').tolist()
    dist = dist_array(rows, cols, lat_obj1, lat_obj2, long_obj1, long_obj2)
    binary = binary_array(dist, rows, cols, threshold = threshold_tuple)
    
    ####################### calculate feature ####################### 
    pile = []
    comp_is = np.where(binary == 1)[0]
    store_for = np.where(binary == 1)[1]
    
    for store_idx, comp_idx in zip(store_for, comp_is):
        store_name = obj_arr[store_idx]
        comp_daterange = pd.date_range(start = comp_date_arr[comp_idx][0], end = comp_date_arr[comp_idx][1], freq = 'W-MON')
        comp_is_open_indicator = list(map(lambda x: int(x == True), monday_.isin(comp_daterange)))
        
        res = pd.DataFrame({'date': monday_,
                            'store': [store_name] * len(monday_),
                            'values': comp_is_open_indicator})
        pile.append(res)
    pile['indicator'] = pile['date'].map(str) + pile['store'].map(str)
    final_table = pile.groupby(['indicator', 'date', 'store']).sum().reset_index()
    
    return final_table.drop(['indicator'], axis = 1)
