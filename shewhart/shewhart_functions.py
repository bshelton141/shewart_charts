import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from branca.colormap import LinearColormap
from matplotlib.dates import DateFormatter
import matplotlib.ticker as ticker
import seaborn as sns
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()



# ----------------------------------------------------------------------------------------------------
# # I Chart Functions
# ----------------------------------------------------------------------------------------------------
def i_chart_limits(dat, focal_val, sort_val, multi_strats=False, strats=[]):
    '''
    Calculates the I bar average and control limits for the specified data set, along with the returning
    the user's original pandas data frame.
    
    Inputs:
      - dat: a pandas data frame that includes a field of focal observations, as well as a field by
          which to stratify the data (either date/time or another stratification).
      - focal_val: the dat field that is the focus of the analysis.
      - sort_val: the dat field by which to stratify the focal_val observations.
      - multi_strats: ether False or True, default is False. If False, then a single set of I bar 
          limits will be calculated against the whole dat dataframe. If True, then I bar limits
          will be calculated for each stratification specified in the strats field.
      - strats: a list of fields by which to stratify the dat dataframe and create unique I bar limits
          for. Will only be used if multi_strats = True.
          
    Outputs:
      - A pandas dataframe consisting of the original dat fields fed into the function, along with 
          the following columns added:
          - i_bar: The sum of all focal_vals divided by the count of total observations.
          - lcl: The calculated I bar lower control limit of the data set.
          - ucl: The calculated I bar upper control limit of the data set.
          - sc_weight: The "special cause" weight of the specific observation. If the observation's
              value is within its respective lower and upper control limits, then sc_weight will
              be zero. If the observation's value is lower than its respective lower control limit,
              then the sc_weight value will be equal to the lower control limit minus the observation,
              divided by the I bar average minus the lower control limit, multiplied by negative 1.
              If the observation's value is higher than the upper control limit, then the sc_weight
              value will be equal to the the observation minus the upper control limit, divided
              by the upper control limit minus the I bar average.
      
    Example 1:
    from shewhart import shewhart_functions as sf
    import shewhart.data_loads as dl
    
    enc_submits_monthly = dl.enc_submits_monthly()
    sf.i_chart_limits(
      dat=enc_submits_monthly,
      focal_val = 'enc_count',
      sort_val = 'rcvd_month',
      multi_strats=False
    )
      
    Example 2:
    enc_by_formtype_monthly = dl.enc_by_formtype_monthly()
    sf.i_chart_limits(
      dat=enc_by_formtype_monthly,
      focal_val = 'enc_count',
      sort_val = 'rcvd_month',
      multi_strats=True,
      strats=['file_fmt_cd']
    )
    '''
    dat = dat.copy()
    
    original_columns = dat.copy().columns.tolist()
    
    # set the focal value
    dat['val'] = dat[focal_val]
    
    # Set the sorting order
    denom_ascending_arg = True
    
    # Check if strats are provided in a list format, if multi_strats == True
    if multi_strats == True:
        if (len(strats) == 0) | (isinstance(strats, list) == False):
            print('Error: Strats argument empty. Expecting a list of at least 1 field included in the `dat` dataset.')
            return
    
    
    # Create the i_bar, lcl, and ucl
    if multi_strats == False:
        dat = dat.sort_values(sort_val, ascending = denom_ascending_arg).reset_index(drop=True)
        dat['mr0'] = np.absolute(dat['val'] - dat['val'].shift(1))
        
        # Calculate the initial MR bar
        mr0_bar = dat['mr0'].sum() / (len(dat)-1)
        
        # Calculate the upper limit of the moving range
        ul_mr = 3.27*mr0_bar
        
        # Re-calculate MR bar one time by removing any values exceeding the upper limit
        dat2 = dat[dat['mr0'] <= ul_mr]
        mr_bar = dat2['mr0'].sum() / (len(dat2)) # don't need to subtract denom by 1 because the initial record gets filtered out
        
        # Calculate the I bar
        dat['i_bar'] = [dat[focal_val].sum() / len(dat)]*len(dat) 
        
        # Calculate the limits
        dat['lcl'] = dat['i_bar'] - (2.66*mr_bar)
        dat['ucl'] = dat['i_bar'] + (2.66*mr_bar) 
        
    else:
        # Sort the fields appropriately
        i_sort_vals = strats.copy()
        i_sort_vals.append(sort_val)
        i_sort_orders = [True]*len(strats)
        i_sort_orders.append(denom_ascending_arg)
        dat = dat.sort_values(i_sort_vals, ascending=i_sort_orders).reset_index(drop=True)
        
        # Calculate the absolute difference between each record's val and the previous val
        dat['mr0'] = np.absolute(dat['val'] - dat.groupby(strats)['val'].shift(1))
        
        # Calculate the initial MR bar
        mr0_bar_dat = dat.groupby(strats) \
          .agg({'mr0': 'sum', sort_val: 'count'}) \
          .reset_index() \
          .rename(columns={'mr0': 'mr0_sum', sort_val: 'length'})
        mr0_bar_dat['mr0_bar'] = mr0_bar_dat['mr0_sum'] / (mr0_bar_dat['length']-1)
        
        # Calculate the Upper Limit Moving Range with the static 3.27,
        # prescribed in The Health Care Data Guide (2011), Chapter 5
        mr0_bar_dat['ul_mr'] = 3.27*mr0_bar_dat['mr0_bar']
        
        mr0_bar_dat_cols = strats.copy()
        mr0_bar_dat_cols.append('ul_mr')
        dat = dat.merge(mr0_bar_dat[mr0_bar_dat_cols], on=strats, how='inner')
        
        # Re-calculate MR bar one time by removing any values exceeding the upper limit
        dat2 = dat[dat['mr0'] <= dat['ul_mr']]
        mr_bar_dat = dat2.groupby(strats) \
          .agg({'mr0': 'sum', sort_val: 'count'}) \
          .reset_index() \
          .rename(columns={'mr0': 'mr_sum', sort_val: 'length'})
        mr_bar_dat['mr_bar'] = mr_bar_dat['mr_sum'] / (mr_bar_dat['length']) # don't need to subtract denom by 1 because the initial record gets filtered out
        mr_bar_dat_cols = strats.copy()
        mr_bar_dat_cols.append('mr_bar')
        dat = dat.merge(mr_bar_dat[mr_bar_dat_cols], on=strats, how='inner')
        
        # Calculate the I bar
        dat['i_bar'] = \
          dat.groupby(strats)[focal_val].transform('sum') / \
          dat.groupby(strats)[focal_val].transform('count')
        
        # Calculate the limits
        dat['lcl'] = dat['i_bar'] - (2.66*dat['mr_bar'])
        dat['ucl'] = dat['i_bar'] + (2.66*dat['mr_bar'])
        
    # Calculate special cause weights
    dat['sc_weight'] = np.where(
      dat['val'] < dat['lcl'],
      (dat['lcl']-dat['val']) / (dat['i_bar']-dat['lcl']) * -1,
      np.where(
        dat['val'] > dat['ucl'],
        (dat['val']-dat['ucl']) / (dat['ucl']-dat['i_bar']),
        0
      )
    )
    
    return dat[original_columns+['i_bar', 'lcl', 'ucl', 'sc_weight']]
  



# ----------------------------------------------------------------------------------------------------
# # P Chart Functions
# ----------------------------------------------------------------------------------------------------
def p_chart_limits(dat, numerator_val, denominator_val, sort_val, multi_strats=False, strats=[]):
    '''
    Calculates the P bar average, control limits, and P prime control limits for the specified data set, 
    along with returning the user's original pandas data frame.
    
    Inputs:
      - dat: a pandas data frame that includes a field of focal observations, as well as a field by
          which to stratify the data (either date/time or another stratification).
      - numerator_val: the dat field that is used as the numerator in the focal rate calculation.
      - denominator_val: the dat field that is used as the denominator in the focal rate calculation.
      - sort_val: the dat field by which to stratify the observations.
      - multi_strats: ether False or True, default is False. If False, then a single set of P bar 
          limits will be calculated against the whole dat dataframe. If True, then P bar limits
          will be calculated for each stratification specified in the strats field.
      - strats: a list of fields by which to stratify the dat dataframe and create unique P bar limits
          for. Will only be used if multi_strats = True.
          
    Outputs:
      - A pandas dataframe consisting of the original dat fields fed into the function, along with 
          the following columns added:
          - p_bar: The sum of all numerator_val values divided by the sum of all denominator_val values.
          - lcl: The calculated P bar lower control limit of the data set.
          - ucl: The calculated P bar upper control limit of the data set.
          - sc_weight: The "special cause" weight of the specific observation. If the observation's
              value is within its respective lower and upper control limits, then sc_weight will
              be zero. If the observation's value is lower than its respective lower control limit,
              then the sc_weight value will be equal to the lower control limit minus the observation,
              divided by the P bar average minus the lower control limit, multiplied by negative 1.
              If the observation's value is higher than the upper control limit, then the sc_weight
              value will be equal to the the observation minus the upper control limit, divided
              by the upper control limit minus the P bar average.
          - lcl_prime: The calculated P bar prime lower control limit of the data set.
          - ucl_prime: The calculated P bar prime upper control limit of the data set.
          - sc_weight_prime: The prime "special cause" weight of the specific observation. If the observation's
              value is within its respective lower and upper prime control limits, then sc_weight_prime will
              be zero. If the observation's value is lower than its respective lower prime control limit,
              then the sc_weight_prime value will be equal to the lower prime control limit minus the observation,
              divided by the P bar average minus the lower prime control limit, multiplied by negative 1.
              If the observation's value is higher than the upper prime control limit, then the sc_weight_prime
              value will be equal to the the observation minus the upper prime control limit, divided
              by the upper prime control limit minus the P bar average.
      
    Example 1:
    from shewhart import shewhart_functions as sf
    import shewhart.data_loads as dl
    
    enc_reject_rate_monthly = dl.enc_reject_rate_monthly()
    sf.p_chart_limits(
      dat=enc_reject_rate_monthly,
      numerator_val = 'reject_count',
      denominator_val = 'total_count',
      sort_val = 'month_elig',
      multi_strats=False
    )
    
    Example 2:
    tran_office_rej_by_ppg = dl.tran_office_rej_by_ppg()
    sf.p_chart_limits(
      dat=tran_office_rej_by_ppg,
      numerator_val = 'reject_count',
      denominator_val = 'total_count',
      sort_val = 'total_count',
      multi_strats=False
    )
    '''
    dat = dat.copy()
    
    original_columns = dat.copy().columns.tolist()
    
    # set the focal value
    dat['val'] = dat[numerator_val] / dat[denominator_val]
    
    # Set the denominator sorting order
    denom_ascending_arg = True
    
    # Calc the p-bar value
    if multi_strats == False:
        dat['p_bar_numer'] = dat[numerator_val].sum()
        dat['p_bar_denom'] = dat[denominator_val].sum()
    elif (len(strats) == 0) | (isinstance(strats, list) == False):
        print('Error: Strats argument empty. Expecting a list of at least 1 field included in the `dat` dataset.')
        return
    else:
        dat['p_bar_numer'] = dat.groupby(strats)[numerator_val].transform('sum')
        dat['p_bar_denom'] = dat.groupby(strats)[denominator_val].transform('sum')
    
    dat['p_bar'] = dat['p_bar_numer'] / dat['p_bar_denom']
            
    
    # Apply the p-bar to all observations and create Shewhart limits
    dat['p_std'] = ((dat['p_bar']*(1-dat['p_bar'])) / dat[denominator_val])**.5
    
    
    # Create the p-prime stsd
    if multi_strats == False:
        dat = dat.sort_values(sort_val, ascending = denom_ascending_arg).reset_index(drop=True)
        dat['p_zval'] = (dat['val'] - dat['p_bar']) / dat['p_std']
        
        # Calculate the absolute difference between each record's p_zval and the previous p_zval
        dat['mr_p_zval'] = np.absolute(dat['p_zval'] - dat['p_zval'].shift(1))
        
        dat['mr_bar0_num'] = dat['mr_p_zval'].sum()
        dat['mr_bar0_den'] = dat[denominator_val].count()
        dat['mr_bar0'] = dat['mr_bar0_num'] / (dat['mr_bar0_den']-1)
        
        # Calculate the Upper Limit Moving Range with the static 3.27,
        # prescribed in The Health Care Data Guide (2011), Chapter 5, Chapter 8
        dat['ul_mr0'] = 3.27*dat['mr_bar0']
        
        # Screen the moving ranges to be less than the ul_mr0
        dat['mr_bar_num'] = dat[dat['mr_p_zval'] <= dat['ul_mr0']]['mr_p_zval'].sum()
        dat['mr_bar_den'] = dat[dat['mr_p_zval'] <= dat['ul_mr0']][sort_val].count()
        dat['mr_bar'] = dat['mr_bar_num'] / dat['mr_bar_den'] # don't need to subtract denom by 1 because the initial record gets filtered out
        
        # Divide the screened moving range bar by the static 1.128,
        # prescribed in The Health Care Data Guide (2011), Chapter 8
        dat['mr_bar_std'] = dat['mr_bar'] / 1.128
        dat = dat.sort_values(sort_val, ascending=denom_ascending_arg).reset_index(drop=True)
        
        
    else:
        # Create the p-prime parameters
        pprime_sort_vals = strats.copy()
        pprime_sort_vals.append(sort_val)
        pprime_sort_orders = [True]*len(strats)
        pprime_sort_orders.append(denom_ascending_arg)
        dat = dat.sort_values(pprime_sort_vals, ascending=pprime_sort_orders).reset_index(drop=True)
        dat['p_zval'] = (dat['val'] - dat['p_bar']) / dat['p_std']
        dat['mr_p_zval'] = np.absolute(dat['p_zval'] - dat.groupby(strats)['p_zval'].shift(1))


        mr_bar0_num = dat.groupby(strats)['mr_p_zval'].sum().reset_index()
        mr_bar0_den = dat.groupby(strats)[denominator_val].count().reset_index()
        mr_bar0_dat = mr_bar0_num.merge(mr_bar0_den, on=strats, how='inner').reset_index(drop=True) \
          .rename(columns={'mr_p_zval': 'mr_bar0_num', denominator_val: 'mr_bar0_den'})
        mr_bar0_dat['mr_bar0'] = mr_bar0_dat['mr_bar0_num'] / (mr_bar0_dat['mr_bar0_den']-1)
        mr_bar0_dat['ul_mr0'] = 3.27*mr_bar0_dat['mr_bar0']
        mr_bar0_dat_cols = strats.copy()
        mr_bar0_dat_cols.append('ul_mr0')
        dat = dat.merge(mr_bar0_dat[mr_bar0_dat_cols], on=strats, how='inner').reset_index(drop=True)
        
        # Screen the moving ranges to be less than the ul_mr0
        mr_bar_num = dat[dat['mr_p_zval'] <= dat['ul_mr0']].groupby(strats)['mr_p_zval'].sum().reset_index()
        mr_bar_den = dat[dat['mr_p_zval'] <= dat['ul_mr0']].groupby(strats)[sort_val].count().reset_index()
        mr_bar_dat = mr_bar_num.merge(mr_bar_den, on=strats, how='inner').reset_index(drop=True) \
          .rename(columns={'mr_p_zval': 'mr_bar_num', sort_val: 'mr_bar_den'})
        mr_bar_dat['mr_bar'] = mr_bar_dat['mr_bar_num'] / mr_bar_dat['mr_bar_den'] # don't need to subtract denom by 1 because the initial record gets filtered out
                
        # Divide the screened moving range bar by the static 1.128,
        # prescribed in The Health Care Data Guide (2011), Chapter 8
        mr_bar_dat['mr_bar_std'] = mr_bar_dat['mr_bar'] / 1.128
        mr_bar_dat_cols = strats.copy()
        mr_bar_dat_cols.append('mr_bar_std')
        dat = dat.merge(mr_bar_dat[mr_bar_dat_cols], on=strats, how='inner').reset_index(drop=True)
    
    
    # Set the control limits
    dat['lcl'] = dat['p_bar'] - (3*dat['p_std'])
    dat['ucl'] = dat['p_bar'] + (3*dat['p_std'])
    dat['lcl_prime'] = dat['p_bar'] - (3*dat['p_std']*dat['mr_bar_std'])
    dat['ucl_prime'] = dat['p_bar'] + (3*dat['p_std']*dat['mr_bar_std'])        
    
    # Calculate special cause weights
    dat['sc_weight'] = np.where(
      dat['val'] < dat['lcl'],
      (dat['lcl']-dat['val']) / (dat['p_bar']-dat['lcl']) * -1,
      np.where(
        dat['val'] > dat['ucl'],
        (dat['val']-dat['ucl']) / (dat['ucl']-dat['p_bar']),
        0
      )
    )
    
    dat['sc_weight_prime'] = np.where(
      dat['val'] < dat['lcl_prime'],
      (dat['lcl_prime']-dat['val']) / (dat['p_bar']-dat['lcl_prime']) * -1,
      np.where(
        dat['val'] > dat['ucl_prime'],
        (dat['val']-dat['ucl_prime']) / (dat['ucl_prime']-dat['p_bar']),
        0
      )
    )
    
    return dat[original_columns+['p_bar', 'lcl', 'ucl', 'sc_weight', 'lcl_prime', 'ucl_prime', 'sc_weight_prime']]
  



# ----------------------------------------------------------------------------------------------------
# # U Chart Functions
# ----------------------------------------------------------------------------------------------------
def u_chart_limits(dat, numerator_val, denominator_val, sort_val, chart_type='time series', multi_strats=False, strats=[]):
    '''
    Calculates the U bar average, control limits, and U prime control limits for the specified data set, 
    along with returning the user's original pandas data frame.
    
    Inputs:
      - dat: a pandas data frame that includes a field of focal observations, as well as a field by
          which to stratify the data (either date/time or another stratification).
      - numerator_val: the dat field that is used as the numerator in the focal rate calculation.
      - denominator_val: the dat field that is used as the denominator in the focal rate calculation.
      - sort_val: the dat field by which to stratify the observations.
      - multi_strats: ether False or True, default is False. If False, then a single set of P bar 
          limits will be calculated against the whole dat dataframe. If True, then P bar limits
          will be calculated for each stratification specified in the strats field.
      - strats: a list of fields by which to stratify the dat dataframe and create unique P bar limits
          for. Will only be used if multi_strats = True.
          
    Outputs:
      - A pandas dataframe consisting of the original dat fields fed into the function, along with 
          the following columns added:
          - u_bar: The sum of all numerator_val values divided by the sum of all denominator_val values.
          - lcl: The calculated U bar lower control limit of the data set.
          - ucl: The calculated U bar upper control limit of the data set.
          - sc_weight: The "special cause" weight of the specific observation. If the observation's
              value is within its respective lower and upper control limits, then sc_weight will
              be zero. If the observation's value is lower than its respective lower control limit,
              then the sc_weight value will be equal to the lower control limit minus the observation,
              divided by the U bar average minus the lower control limit, multiplied by negative 1.
              If the observation's value is higher than the upper control limit, then the sc_weight
              value will be equal to the the observation minus the upper control limit, divided
              by the upper control limit minus the U bar average.
          - lcl_prime: The calculated U bar prime lower control limit of the data set.
          - ucl_prime: The calculated U bar prime upper control limit of the data set.
          - sc_weight_prime: The prime "special cause" weight of the specific observation. If the observation's
              value is within its respective lower and upper prime control limits, then sc_weight_prime will
              be zero. If the observation's value is lower than its respective lower prime control limit,
              then the sc_weight_prime value will be equal to the lower prime control limit minus the observation,
              divided by the U bar average minus the lower prime control limit, multiplied by negative 1.
              If the observation's value is higher than the upper prime control limit, then the sc_weight_prime
              value will be equal to the the observation minus the upper prime control limit, divided
              by the upper prime control limit minus the U bar average.
      
      NOTE: If analzying Per Thousand Member Per Month (PTMPM) values, the data must NOT be in PTMPM format before feeding
        into the this function. It must be in Per Member Per Month (PMPM) format instead. After the control limits
        are calculated, then the user would multiple the focal value, U bar and the control limits by 1000.
      
    Example:
    from shewhart import shewhart_functions as sf
    import shewhart.data_loads as dl
    
    pcp_pmpm = dl.pcp_pmpm_data()
    pcp_pmpm['month_elig'] = pd.to_datetime(pcp_pmpm['month_elig'])
    sf.u_chart_limits(
      dat=pcp_pmpm,
      numerator_val = 'pcp_count',
      denominator_val = 'mem_count',
      sort_val = 'month_elig',
      multi_strats=False
    )
    '''
    dat = dat.copy()
    
    original_columns = dat.copy().columns.tolist()
    
    # set the focal value
    dat['val'] = dat[numerator_val] / dat[denominator_val]
    
    # Set the denominator sorting order
    denom_ascending_arg = True
    
    # Calc the u-bar value
    if multi_strats == False:
        dat['u_bar_numer'] = dat[numerator_val].sum()
        dat['u_bar_denom'] = dat[denominator_val].sum()
    elif (len(strats) == 0) | (isinstance(strats, list) == False):
        print('Error: Strats argument empty. Expecting a list of at least 1 field included in the `dat` dataset.')
        return
    else:
        dat['u_bar_numer'] = dat.groupby(strats)[numerator_val].transform('sum')
        dat['u_bar_denom'] = dat.groupby(strats)[denominator_val].transform('sum')
    
    dat['u_bar'] = dat['u_bar_numer'] / dat['u_bar_denom']
            
    
    # Apply the u-bar to all observations and create Shewhart limits
    dat['u_std'] = (dat['u_bar'] / dat[denominator_val])**.5
    
    
    # Create the u-prime stsd
    if multi_strats == False:
        dat = dat.sort_values(sort_val, ascending = denom_ascending_arg).reset_index(drop=True)
        dat['u_zval'] = (dat['val'] - dat['u_bar']) / dat['u_std']
        dat['mr_u_zval'] = np.absolute(dat['u_zval'] - dat['u_zval'].shift(1))
        
        dat['mr_bar0_num'] = dat['mr_u_zval'].sum()
        dat['mr_bar0_den'] = dat[denominator_val].count()
        dat['mr_bar0'] = dat['mr_bar0_num'] / (dat['mr_bar0_den']-1)
        
        # Calculate the Upper Limit Moving Range with the static 3.27,
        # prescribed in The Health Care Data Guide (2011), Chapter 5, Chapter 8
        dat['ul_mr0'] = 3.27*dat['mr_bar0']
        
        # Screen the moving ranges to be less than the ul_mr0
        dat['mr_bar_num'] = dat[dat['mr_u_zval'] <= dat['ul_mr0']]['mr_u_zval'].sum()
        dat['mr_bar_den'] = dat[dat['mr_u_zval'] <= dat['ul_mr0']][sort_val].count()
        dat['mr_bar'] = dat['mr_bar_num'] / dat['mr_bar_den']
        
        # Divide the screened moving range bar by the static 1.128,
        # prescribed in The Health Care Data Guide (2011), Chapter 8
        dat['mr_bar_std'] = dat['mr_bar'] / 1.128
        
        dat = dat.sort_values(sort_val, ascending=denom_ascending_arg).reset_index(drop=True)
        
    else:
        # Create the u-prime parameters
        uprime_sort_vals = strats.copy()
        uprime_sort_vals.append(sort_val)
        uprime_sort_orders = [True]*len(strats)
        uprime_sort_orders.append(denom_ascending_arg)
        dat = dat.sort_values(uprime_sort_vals, ascending=uprime_sort_orders).reset_index(drop=True)
        dat['u_zval'] = (dat['val'] - dat['u_bar']) / dat['u_std']
        dat['mr_u_zval'] = np.absolute(dat['u_zval'] - dat.groupby(strats)['u_zval'].shift(1))


        mr_bar0_num = dat.groupby(strats)['mr_u_zval'].sum().reset_index()
        mr_bar0_den = dat.groupby(strats)[denominator_val].count().reset_index()
        mr_bar0_dat = mr_bar0_num.merge(mr_bar0_den, on=strats, how='inner').reset_index(drop=True) \
          .rename(columns={'mr_u_zval': 'mr_bar0_num', denominator_val: 'mr_bar0_den'})
        mr_bar0_dat['mr_bar0'] = mr_bar0_dat['mr_bar0_num'] / (mr_bar0_dat['mr_bar0_den']-1)
        
        # Calculate the Upper Limit Moving Range with the static 3.27,
        # prescribed in The Health Care Data Guide (2011), Chapter 5, Chapter 8
        mr_bar0_dat['ul_mr0'] = 3.27*mr_bar0_dat['mr_bar0']
        
        mr_bar0_dat_cols = strats.copy()
        mr_bar0_dat_cols.append('ul_mr0')
        dat = dat.merge(mr_bar0_dat[mr_bar0_dat_cols], on=strats, how='inner').reset_index(drop=True)
        
        # Screen the moving ranges to be less than the ul_mr0
        mr_bar_num = dat[dat['mr_u_zval'] <= dat['ul_mr0']].groupby(strats)['mr_u_zval'].sum().reset_index()
        mr_bar_den = dat[dat['mr_u_zval'] <= dat['ul_mr0']].groupby(strats)[sort_val].count().reset_index()
        mr_bar_dat = mr_bar_num.merge(mr_bar_den, on=strats, how='inner').reset_index(drop=True) \
          .rename(columns={'mr_u_zval': 'mr_bar_num', sort_val: 'mr_bar_den'})
        mr_bar_dat['mr_bar'] = mr_bar_dat['mr_bar_num'] / mr_bar_dat['mr_bar_den'] # don't need to subtract denom by 1 because the initial record gets filtered out
        
        # Divide the screened moving range bar by the static 1.128,
        # prescribed in The Health Care Data Guide (2011), Chapter 8
        mr_bar_dat['mr_bar_std'] = mr_bar_dat['mr_bar'] / 1.128
        
        mr_bar_dat_cols = strats.copy()
        mr_bar_dat_cols.append('mr_bar_std')
        dat = dat.merge(mr_bar_dat[mr_bar_dat_cols], on=strats, how='inner').reset_index(drop=True)
    
    
    # Set the control limits
    dat['lcl'] = dat['u_bar'] - (3*dat['u_std'])
    dat['ucl'] = dat['u_bar'] + (3*dat['u_std'])
    dat['lcl_prime'] = dat['u_bar'] - (3*dat['u_std']*dat['mr_bar_std'])
    dat['ucl_prime'] = dat['u_bar'] + (3*dat['u_std']*dat['mr_bar_std'])        
    
    # Calculate special cause weights
    dat['sc_weight'] = np.where(
      dat['val'] < dat['lcl'],
      (dat['lcl']-dat['val']) / (dat['u_bar']-dat['lcl']) * -1,
      np.where(
        dat['val'] > dat['ucl'],
        (dat['val']-dat['ucl']) / (dat['ucl']-dat['u_bar']),
        0
      )
    )
    
    dat['sc_weight_prime'] = np.where(
      dat['val'] < dat['lcl_prime'],
      (dat['lcl_prime']-dat['val']) / (dat['u_bar']-dat['lcl_prime']) * -1,
      np.where(
        dat['val'] > dat['ucl_prime'],
        (dat['val']-dat['ucl_prime']) / (dat['ucl_prime']-dat['u_bar']),
        0
      )
    )
    
    return dat[original_columns+['u_bar', 'lcl', 'ucl', 'sc_weight', 'lcl_prime', 'ucl_prime', 'sc_weight_prime']]




# ----------------------------------------------------------------------------------------------------
# # Plot Function
# ----------------------------------------------------------------------------------------------------
def shewhart_plot(chart_type, dat, xval, yval, title, xlabel, ylabel, 
                  prime_controls=False, better_direction='lower', 
                  show_x_ticks=True, show_sc_labels=False, show_specific_obs=[]):
    '''
    Note: This function assumes that the data set is already sorted appropriately.

    - chart_type: options are either 'I', 'P', or 'U'

    - data: the data set that being used for the control chart. it needs to have been processed through the appropriate
         i_chart_limits(), or p_chart_limits(), or u_chart_limits() function.

    - xval: the value to plot on the x-axis

    - yval: the value to plot on the y-axis

    - xlabel: the x-axis label

    - ylabel: the y-axis label

    - prime_controls: options are either False or True, with default being False. If False, then uses the data set's lcl,
      ucl, and sc_weight values. If True, then uses the data set's lcl_prime, ucl_prime, and sc_weight_prime values.
      For I charts, this must be set to False, as there is no prime value for the I chart.

    - better_direction: options are either 'none', lower' or 'higher', with default being 'none'. If 'none', then all data
      points are blue. If 'lower', then the within range observations are blue, the below the LCL observations are green,
      and the above the UCL observations are red. If 'upper', then the within range observations are blue, the below the 
      LCL observations are red, and the above the UCL observations are green. The red and green values are mapped linearly
      based on the sc_weight (or sc_weight_prime) value of the observations.

    - show_x_ticks: options are True or False, with default being True. Dictates whether or not the x-axis ticks are
      displayed.
      
    - show_sc_labels: options are True of False, with default being False. Dictates whether or not the special cause
      observations' labels are displayed on the plot.
    
    - show_specific_obs: requires a user-specified list of xval values to annotate, with the default being an empyt
      list. Dictates specific observation to annotate on the plot.
    
    
    Example:
    from shewhart import shewhart_functions as sf
    import shewhart.data_loads as dl
    
    # Create I bar limits on a data set
    enc_submits_monthly = dl.enc_submits_monthly()
    i_vals = sf.i_chart_limits(
      dat=enc_submits_monthly,
      focal_val = 'enc_count',
      sort_val = 'rcvd_month',
      multi_strats=False
    )
    
    i_vals['rcvd_month'] = pd.to_datetime(i_vals['rcvd_month'])
    
    # Run this function
    sf.shewhart_plot(
      chart_type = 'I',
      dat = i_vals,
      xval = 'rcvd_month',
      yval = 'enc_count',
      prime_controls=False,
      better_direction='none',
      title='Total Encounters Submissions by Month',
      xlabel='Month of Submission',
      ylabel='Volume',
      show_x_ticks=True,
      show_sc_labels=True,
      show_specific_obs=[]
    )
    
    

    '''
    dat = dat.copy()
    
    figsize=(11,8.5)
    
    if chart_type == 'I':
        focal_bar = 'i_bar'
    elif chart_type == 'P':
        focal_bar = 'p_bar'
    elif chart_type == 'U':
        focal_bar = 'u_bar'        
    
    if prime_controls == False:
        focal_lcl = 'lcl'
        focal_ucl = 'ucl'
        focal_sc_weight = 'sc_weight'
    else:
        focal_lcl = 'lcl_prime'
        focal_ucl = 'ucl_prime'
        focal_sc_weight = 'sc_weight_prime'
            
    if dat[xval].dtype == '<M8[ns]':
        dat[xval] = dat[xval].dt.date  # Format x-axis ticks as dates
    
    if better_direction == 'none':
        lower_color_scale = ['darkred', 'red']
        upper_color_scale = ['darkred', 'red']
    elif better_direction == 'lower':
        lower_color_scale = ['darkgreen', 'green']
        upper_color_scale = ['darkred', 'red']
    else:
        lower_color_scale = ['darkred', 'red']
        upper_color_scale = ['darkgreen', 'green']
        
    lower_colormap = LinearColormap(colors=lower_color_scale, 
                                    vmin=0, 
                                    vmax=max(np.abs(dat[focal_sc_weight].min()),
                                             dat[focal_sc_weight].max()))
    
    def lower_color_tag(row):
        return lower_colormap(np.abs(row[focal_sc_weight]))
    
    dat['lower_severity_color'] = dat.apply(lower_color_tag, axis=1)
  
    
    # Colors based on upper severity
    upper_colormap = LinearColormap(colors=upper_color_scale, 
                                    vmin=0, 
                                    vmax=max(np.abs(dat[focal_sc_weight].min()),
                                             dat[focal_sc_weight].max()))
    
    def upper_color_tag(row):
        return upper_colormap(row[focal_sc_weight])
    
    dat['upper_severity_color'] = dat.apply(upper_color_tag, axis=1)
    
    
    # Choose when to use either the lower or upper severity colors
    dat['plot_color'] = np.where(dat[focal_sc_weight] < 0,
                                 dat['lower_severity_color'],
                                 np.where(dat[focal_sc_weight] > 0,
                                          dat['upper_severity_color'],
                                          'blue'))
    
    # Set color palette for plotting
    custom_palette = sns.color_palette(dat['plot_color'].unique())

    ax=sns.scatterplot(data=dat, x=xval, y=yval, marker='o', 
                       hue='plot_color', palette=custom_palette, zorder=2) 
    sns.lineplot(data=dat, x=xval, y=focal_lcl, color='gray', linestyle='--')
    sns.lineplot(data=dat, x=xval, y=focal_bar, color='gray', linestyle='--')
    sns.lineplot(data=dat, x=xval, y=focal_ucl, color='gray', linestyle='--')
    
    plt.title(title, size=11)
    plt.xlabel(xlabel, size=10)
    plt.ylabel(ylabel, size=10)
    
    if chart_type == 'P':
      percent_formatter = ticker.PercentFormatter(xmax=1, decimals=0)
      ax.yaxis.set_major_formatter(percent_formatter)
    
    if show_x_ticks:
        plt.xticks(rotation=45, ha='right', fontsize=9)
    else:
        plt.xticks([])
    
    plt.yticks(fontsize=9)
    plt.grid(False)
    plt.legend().set_visible(False)
    
    # Add labels to "Outliers" scatterplot values
    if show_sc_labels == True:
        for i in range(len(dat)):
            if dat[focal_sc_weight][i] != 0:
                plt.annotate(f"{dat[xval][i]}",
                             (dat[xval][i], dat[yval][i]), 
                              textcoords="offset points", xytext=(0,-12), ha='center')
    
    # Add labels to user-specified observation values
    if len(show_specific_obs) > 0:
        for i in range(len(dat)):
            if dat[xval][i] in show_specific_obs:
                plt.annotate(f"{dat[xval][i]}",
                             (dat[xval][i], dat[yval][i]), 
                              textcoords="offset points", xytext=(0,-12), ha='center')        
            
    plt.show()
