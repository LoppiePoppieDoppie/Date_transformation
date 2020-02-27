import numpy as np
import pandas as pd
import matplotlib.pyplot as plt




def stores_life_plot(df, store_col = '', date_col = '', until_date = ''):
    '''
    Return plot of stores life according to their open and close date.
    Return plot firstly, that can help to decide with date should be first in model.
    Input start date in returned window
    Filter dataframe by time period satisfied stores
    
    args:
        df          - initial dataframe with date-store_code-traffic-etc...
        store_col   - store_code column
        until_date  - last date in model 
    
    return:
        df_final    - {pd.DataFrame} cutted dataframe
    '''
    heap = []
    df[store_col] = df[store_col].astype(str)
    unique_stores = df[store_col].unique()
    until_date = pd.Timestamp(until_date)
    
    for idx, store in enumerate(unique_stores):
        one_store = df[df[store_col] == store]
        date_range = one_store[date_col]
        frame = pd.DataFrame(index = date_range,
                             date = np.transpose([[idx]*len(date_range), np.ones(len(date_range)) + idx*0.1]),
                             columns = ['store_num', 'indicator'])
        heap.append(frame)
    heap = pd.concat(heap)
    
    plt.figure(figsize = (14, 8))
    for i in heap['store_num'].unique():
        store_to_plot = heap[heap['store_num'] == i]
        if store_to_plot.index.max() < until_date:
            plt.plot(store_to_plot['indicator'], 'r')
        else: 
            plt.plot(store_to_plot['indicator'], 'g')
    plt.show()
    
    idx_to_drop = [int(storenum) for storenum in heap['store_num'].unique() if heap[heap['store_num'] == storenum].index.max() < pd.Timestamp(until_date)]
    stores_to_drop = df[store_col].unique()[idx_to_drop].tolist()
    df_dropped = df[~df[store_col].isin(stores_to_drop)]
    date_start = pd.Timestamp(str(input()))
    df_final = df_dropped[(df_dropped[date_col] >= date_start) & (df_dropped[date_col] <= until_date)]
    
    return df_final
