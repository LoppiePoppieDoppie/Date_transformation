# Preprocessing
Scripts for tables transformation

# cv_model_selection.py
Test different features combinations by fitting rotating features to linear regression from the pool and cross-validate models on N folds, thus total quantity is: combinations * N
    
args:
*  file_name           - {str} name of the file with transformed features
*  date_time_col       - {str} [date_time] feature column name. filled with N values (1, 2, 3, ... n_observations)
*  max_date_num_col    - {int} last number [date_time] value / n_observation
*  const_features      - {list} of constant features that don't have to be rotated **!!!Y_val HAVE TO BE FIRST IN LIST!!!**
*  to_rotate           - {list} list of regular expressions for each media feature to rotate ['SUB_OLV_Imp_d0.?[2-8]', 'SUB_OOH_d0.?[2-8]']
*  regex_decode        - {list} list of media to rotate in normal form ['OLV', 'OOH']
*  nfolds              - {int} number of CV splits
*  save                - {str} name of file to save with
        
return:
*  res                 - {pd.DataFrame} pivoted look like feature and stats table 

```
from cv_model_selection import model_selection

model_selection(
                file_name = 'bike_sharing_demand', 
                date_time_col = False, 
                max_date_num_col = False, 
                const_features = ['season', 'holiday', 'weather', 'usd'], 
                to_rotate = ['TV_d?[0-9]', 'OOH_d?[0-9]', 'OLV_d?[0-9]', 'Comp_d?[0-9]'], 
                regex_decode = ['TV', 'OOH', 'OLV', 'Comp'],
                nfolds = 5,
                save = 'filename'
                )
```

# distance_calculation.py
Calculate distance beween each competitior/OOH object and client store
        
*  file_name                  - name of file with client and competitor/OOH objects, latitude, longitude and open-close dates
*  client                     - column of client's objects names 
*  competitor                 - column of competitor's objects names
*  competitor_latitude        - column of competitor's latitude
*  client_latitude            - column of client's latitude
*  competitor_longitude       - column of competitor's longitude
*  client_longitude           - column of client's longitude
*  threshold_tuple            - interval (min_dist, max_dist) between objects you need to calculate feature within in metres
*  open_date                  - column with competitor open dates
*  close_date                 - column with competitor close dates
*  model_start_date           - first model's monday
*  model_end_date             - the last monday of model

Input and output dataframes: 
```
    e.g.:
        comp    comp_latitude    comp_longitude    client    client_latitude    client_longitude    comp_open_date    comp_close_date
        1       30.3746659	     60.0453568        store_1   59.9268	        30.3161	             2016-04-04       2019-11-08
        2       30.3144672	     59.9571587        store_2   59.9258	        30.3144              2016-04-04                
        n       30.338264	     59.862598         store_n   60.0264	        30.2229              2016-04-11       2019-06-04
        
                                                                        to
        date          client_store      value   
        2016-03-28    store_1           0
        2016-04-04    store_1           1
        2016-04-11    store_1           2
        2016-04-18    store_1           2
```

Main func of the script
```
from distance_calculation import dist_feature

dist_feature(file_name = 'dist_filename', 
             client = 'client_store_col_name', 
             competitor = 'competitor_store_col_name', 
             competitor_latitude = 'competitor_latitude_col_name', 
             client_latitude = 'client_latitude_col_name', 
             competitor_longitude = 'competitor_longitude_col_name', 
             client_longitude = 'client_latitude_col_name', 
             threshold_tuple = (0, 200), 
             open_date = 'competitor_store_open_date_col_name', 
             close_date = 'competitor_store_close_date_col_name', 
             model_start_date = '2017-01-02', 
             model_end_date = '2020-02-17'
             )
```
