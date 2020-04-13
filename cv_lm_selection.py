# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 11:50:01 2020

@author: DMatveev
"""

import pandas as pd
import itertools as itr
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import r2_score, mean_squared_error
#import statsmodels.api as sm
import warnings
warnings.filterwarnings('ignore')

############################ make lm models for each config in pool ############################


def model_selection(file_name, date_col, min_date_value, max_date_value, const_features, to_rotate, regex_decode, nfolds, save):
    '''
    test different features combinations by fitting rotating features to linear regression from the pool
    
    args:
        file_name           - {str} name of the file with transformed features
        date_time_col       - {str} [date_time] feature column name. filled with N values (1, 2, 3, ... n_observations)
        max_date_num_col    - {int} last number [date_time] value / n_observation
        const_features      - {list} of constant features that don't have to be rotated !!!Y_val HAVE TO BE FIRST IN LIST!!!
        to_rotate           - {list} list of regular expressions for each media feature to rotate ['SUB_OLV_Imp_d0.?[2-8]', 'SUB_OOH_d0.?[2-8]']
        regex_decode        - {list} list of media to rotate in normal view ['OLV', 'OOH']
        nfolds              - {int} number of splits
        save                - {str} name of file to save with
        
    return:
        res                 - {pd.DataFrame} pivoted look like feature and stats table 
        
    '''
    #read data
    try:
        data = pd.read_csv('%s.csv'%(file_name), sep = ';', encoding = 'cp1251')
    except FileNotFoundError:
        data = pd.read_excel('%s.xlsx'%(file_name), encoding = 'cp1251')
    
    # set modeling period 
    if not (date_col and max_date_value and min_date_value):
        df = data
    else:
        df = data
        try:
            df[date_col] = pd.to_datetime(df[date_col], format = '%Y-%m-%d')
        except ValueError:
            df[date_col] = pd.to_datetime(df[date_col], format = '%d-%m-%Y')
        df = df[(df[date_col] >= min_date_value) & (df[date_col] < max_date_value)]
    
    # rotating and costant features pools
    df_list = [df.filter(regex = regexp) for regexp in to_rotate]
    data_base = df[const_features]
 
    combinations = list(itr.product(*df_list))
    print('combinations: ', len(combinations), '\n', 'minutes:  ', len(combinations) * 320 * 0.001 / 60)
    
    def time_cv(X, nfolds, scorer = ''):
        '''time series cross validation stratagy'''
        tscv = TimeSeriesSplit(n_splits = nfolds)
        score = cross_val_score(lm, X, y, cv = tscv, scoring = '%s'%(scorer))
        return (-score.mean())
    
    # total_summary table filling loop
    total = []
    y = data_base.iloc[:, 0]
    for comb in combinations:  
        X = df[data_base.iloc[:, 1:].columns.tolist() + list(comb)]
        lm = LinearRegression()
        lm.fit(X, y)
        params = np.append(lm.intercept_, lm.coef_)
        predictions = lm.predict(X)
        X_const = pd.concat([X, pd.DataFrame({'const': np.ones(len(X))}).set_index(X.index)], axis = 1)
        
        # Stats
        MSE = sum((y - predictions) ** 2) / len(X_const)
        var_b = MSE * (np.linalg.inv(np.dot(X_const.T, X_const)).diagonal())
        std = np.sqrt(var_b)
        tval = params / std
        pval = np.round([2 * (1 - stats.t.cdf(np.abs(i), (len(X_const) - 1))) for i in tval], 4)
        
        # Metrics
        r2 = r2_score(y, predictions)
        mse_train = mean_squared_error(y, predictions)
        mse_cv = time_cv(X = X_const, scorer = 'neg_mean_squared_error', nfolds = nfolds)
        # Table
        summary = pd.DataFrame({'comb': [comb] * len(X_const.columns.tolist()), 
                                'feature_name': ['const'] + X.columns.tolist(),
                                'coef': params, 
                                'std': np.round(std, 4), 
                                't': np.round(tval, 4), 
                                'pval': pval,
                                'r2': [r2] * len(X_const.columns.tolist()),
                                'mse_train': [mse_train] * len(X_const.columns.tolist()),
                                'mse_cv': [mse_cv] * len(X_const.columns.tolist())
                               })
    
        total.append(summary)
    total = pd.concat(total)
    
    
    def get_feature_regex(regex = ''):
        feature_list = [i for sublist in np.unique(total['feature_name'].str.findall(r'%s'%(regex)))[1: ] for i in sublist]
        return feature_list
    
    media_list = [item for sublist in [get_feature_regex(i) for i in to_rotate] for item in sublist]
    
    ############################ split model configurations table ############################
    stats_table = total.iloc[:, [0, 1, 2, 8]]
    for_pivot = stats_table[stats_table['feature_name'].isin(media_list)]
    comb_col = for_pivot.iloc[:, 0]              # combination's column
    to_replace_table = for_pivot.iloc[:, 1:]    # rotated features table
    
    for regexp, regex_de in zip(to_rotate, regex_decode):
        to_replace_table.replace(regex = {regexp: regex_de}, inplace = True)

    table_for_pivot = pd.concat([comb_col, to_replace_table], axis = 1, sort = False)
    sorted_pivoted = pd.pivot_table(table_for_pivot.sort_values(by = 'mse_cv').iloc[:, :], index = ['comb'], 
                                    columns = ['feature_name'],
                                    values = ['coef', 'mse_cv']).reset_index()
    if len(to_rotate) > 1:
        res = sorted_pivoted.iloc[:, :-(len(to_rotate)-1)]
    elif len(to_rotate) == 1:
        res = sorted_pivoted
    if save:
        res.to_csv('%s.csv'%(save), sep = ';', encoding = 'cp1251')
    
    return res
