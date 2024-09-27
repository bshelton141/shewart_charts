import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from branca.colormap import LinearColormap
from matplotlib.dates import DateFormatter
import matplotlib.ticker as ticker
import seaborn as sns
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# To install/update the `shewhart_charts` package in a CDSW session, based on this repository's main branch
!pip3 install -U git+https://github.com/bshelton/shewhart_charts.git@main#egg=shewhart
  
# See what functions are available in the package
from shewhart import __all__ as shewhart_listing
shewhart_listing

from shewhart import shewhart_functions as sf

# Read the documentation of a specific function
help(sf.i_chart_limits)

# Read in the example package data
import shewhart.data_loads as dl

# ------------------------------------------------------------------------------------
# ## Example 1. I-Chart for time-series
# ------------------------------------------------------------------------------------
enc_submits_monthly = dl.enc_submits_monthly()
enc_submits_monthly['rcvd_month'] = pd.to_datetime(enc_submits_monthly['rcvd_month'])

# use the function to get the control limits
enc_i = sf.i_chart_limits(
  dat=enc_submits_monthly,
  focal_val = 'enc_count',
  sort_val = 'rcvd_month',
  multi_strats=False
)

# Plot
sf.shewhart_plot(
  chart_type = 'I',
  dat = enc_i,
  xval = 'rcvd_month',
  yval = 'enc_count',
  prime_controls=False,
  better_direction='none',
  title='Total Encounters Submissions by Month',
  xlabel='Month of Submission',
  ylabel='Volume',
  show_x_ticks=True,
  show_sc_labels=True,
  show_specific_obs=[])



# ------------------------------------------------------------------------------------
# ## Example 2. P-Chart for time-series
# ------------------------------------------------------------------------------------
enc_reject_rate_monthly = dl.enc_reject_rate_monthly()
enc_reject_rate_monthly['month_elig'] = pd.to_datetime(enc_reject_rate_monthly['month_elig']).dt.date

# use the function to get the control limits
enc_reject_rate_p = sf.p_chart_limits(
  dat=enc_reject_rate_monthly,
  numerator_val = 'reject_count',
  denominator_val = 'total_count',
  sort_val = 'month_elig',
  multi_strats=False
)

# Plot
sf.shewhart_plot(
  chart_type = 'P',
  dat = enc_reject_rate_p,
  xval = 'month_elig',
  yval = 'reject_rate',
  prime_controls=True,
  better_direction='lower',
  title='Total Internal Encounters Rejection Rate by Month',
  xlabel='Month of Service',
  ylabel='Rejection Rate',
  show_x_ticks=True,
  show_sc_labels=False,
  show_specific_obs=[])



# ------------------------------------------------------------------------------------
# ## Example 3. P-Chart for funnel 
# ------------------------------------------------------------------------------------
'''
Read in data for a 6-month period of Jul 2023 thru Dec 2023 of internally-rejected 
office place of service encounters ('10', '11', '49', '72') from Transunion submissions,
by PPG.
'''
tran_office_rej_by_ppg = dl.tran_office_rej_by_ppg()


# use the function to get the control limits
tran_office_rej_by_ppg_p = sf.p_chart_limits(
  dat=tran_office_rej_by_ppg,
  numerator_val = 'reject_count',
  denominator_val = 'total_count',
  sort_val = 'total_count',
  multi_strats=False
)

'''
For plotting, limit to just those PPGs that make up at least 95% of total Transunion
office submission volume.
Make sure to do this AFTER using the Shewhart function to create the control limits.
'''
top_ppgs = tran_office_rej_by_ppg_p \
  .sort_values('total_count', ascending=False)
top_ppgs['count_cumperc'] = top_ppgs['total_count'].cumsum()/top_ppgs['total_count'].sum()
top_ppgs = top_ppgs[top_ppgs['count_cumperc'] <= 0.95].ppg_code.drop_duplicates().tolist()

ppg_plot_df = tran_office_rej_by_ppg_p[tran_office_rej_by_ppg_p['ppg_code'].isin(top_ppgs)] \
  .reset_index(drop=True)

  
# Plot  
sf.shewhart_plot(
  chart_type = 'P',
  dat = ppg_plot_df,
  xval = 'ppg_code',
  yval = 'rej_rate',
  prime_controls=True,
  better_direction='lower',
  title='Edifecs Rejection Rates of Professional Office Visits:\nJul thru Dec 2023 by PPG Code',
  xlabel='PPGs Sorted from Least to Most Professional Transunion Submissions',
  ylabel='Rejection Rate',
  show_x_ticks=True,
  show_sc_labels=True,
  show_specific_obs=[])


# Plot again, but only annotating two user-defined observations
sf.shewhart_plot(
  chart_type = 'P',
  dat = ppg_plot_df,
  xval = 'ppg_code',
  yval = 'rej_rate',
  prime_controls=True,
  better_direction='lower',
  title='Edifecs Rejection Rates of Professional Office Visits:\nJul thru Dec 2023 by PPG Code',
  xlabel='PPGs Sorted from Least to Most Professional Transunion Submissions',
  ylabel='Rejection Rate',
  show_x_ticks=True,
  show_sc_labels=False,
  show_specific_obs=['HCLA', 'HCLV'])



# ------------------------------------------------------------------------------------
# ## Example 4. I-Chart for time-series with different categories
# ------------------------------------------------------------------------------------
enc_by_formtype_monthly = dl.enc_by_formtype_monthly()
enc_by_formtype_monthly['rcvd_month'] = pd.to_datetime(enc_by_formtype_monthly['rcvd_month'])

# use the function to get the control limits
enc_by_formtype_i = sf.i_chart_limits(
  dat=enc_by_formtype_monthly,
  focal_val = 'enc_count',
  sort_val = 'rcvd_month',
  multi_strats=True,
  strats=['file_fmt_cd']
)

formtypes = enc_by_formtype_i.file_fmt_cd.drop_duplicates().tolist()

# plot
def i_plot_ts_strats(dat, xval, yval):

    fig, axs = plt.subplots(len(formtypes), 1, figsize=(8.5, 11))
    axs = axs.flatten()  # Flatten the 2D array of axes into a 1D array

    for i, formtype in enumerate(formtypes, start=1):
        ax = axs[i-1]
        plot_dat = dat[dat['file_fmt_cd'] == formtype].reset_index(drop=True)

        sns.scatterplot(data=plot_dat, x=xval, y=yval, marker='o', color='blue', s=50, ax=ax, zorder=2) 
        sns.lineplot(data=plot_dat, x=xval, y='lcl', color='gray', linestyle='--', ax=ax)
        sns.lineplot(data=plot_dat, x=xval, y='i_bar', color='gray', linestyle='--', ax=ax)
        sns.lineplot(data=plot_dat, x=xval, y='ucl', color='gray', linestyle='--', ax=ax)

        ax.set_title(formtype, size=12)
        ax.grid(False)

    fig.tight_layout(rect=[0, .15, 1, 1])
    fig.subplots_adjust(hspace=0.5, wspace=0.15)
    plt.show()

i_plot_ts_strats(enc_by_formtype_i, 'rcvd_month', 'enc_count')



# ------------------------------------------------------------------------------------
# ## Example 5. I-Chart for time-series with breaks in the control limits
# ------------------------------------------------------------------------------------
'''
Medi-Cal Pharmacy Benefit Management responsibilities transitioned to DHCS in Jan 2022.
Because of this, our trend of total submitted encounters changed signifcantly (because)
the state is not receiving those encounters for processing, not L.A. Care. To create 
two separate control plots, we can create an indicator in the enc_submits_monthly dataset
and use the indictor as a stratification when running the i_chart_limits() function to 
create the control limits for the two time periods separately.
'''
# Create an indicator where the the control limit break should occur
enc_ncpd_monthly = enc_by_formtype_monthly[enc_by_formtype_monthly['file_fmt_cd'] == 'NCPDP42'].reset_index(drop=True)
enc_by_formtype_monthly['pbm_stopped'] = np.where((enc_by_formtype_monthly['file_fmt_cd'] == 'NCPDP42') & \
                                                  (enc_by_formtype_monthly['rcvd_month'] >= '2022-01-01'),
                                                   1, 0)

# use the function to get the control limits for both data sets
enc_ncpd_i_pbm_break = sf.i_chart_limits(
  dat=enc_by_formtype_monthly,
  focal_val = 'enc_count',
  sort_val = 'rcvd_month',
  multi_strats=True,
  strats=['file_fmt_cd','pbm_stopped']
)


formtypes = enc_by_formtype_i.file_fmt_cd.drop_duplicates().tolist()

# plot
def i_plot_ts_strats(dat, xval, yval):

    fig, axs = plt.subplots(len(formtypes), 1, figsize=(8.5, 11))
    axs = axs.flatten()  # Flatten the 2D array of axes into a 1D array

    for i, formtype in enumerate(formtypes, start=1):
        ax = axs[i-1]
        plot_dat = dat[dat['file_fmt_cd'] == formtype].reset_index(drop=True)

        sns.scatterplot(data=plot_dat, x=xval, y=yval, marker='o', color='blue', s=50, ax=ax, zorder=2) 
        sns.lineplot(data=plot_dat, x=xval, y='lcl', color='gray', linestyle='--', ax=ax)
        sns.lineplot(data=plot_dat, x=xval, y='i_bar', color='gray', linestyle='--', ax=ax)
        sns.lineplot(data=plot_dat, x=xval, y='ucl', color='gray', linestyle='--', ax=ax)

        ax.set_title(formtype, size=12)
        ax.grid(False)

    fig.tight_layout(rect=[0, .15, 1, 1])
    fig.subplots_adjust(hspace=0.5, wspace=0.15)
    plt.show()

i_plot_ts_strats(enc_ncpd_i_pbm_break, 'rcvd_month', 'enc_count')



# ------------------------------------------------------------------------------------
# ## Example 6. P-Chart for time-series with different categories
# ------------------------------------------------------------------------------------
hdr_bp_cd_status_rej_rate = dl.hdr_bp_cd_status_rej_rate()
hdr_bp_cd_status_rej_rate['month_elig'] = pd.to_datetime(hdr_bp_cd_status_rej_rate['month_elig'])

# use the function to get the control limits
hdr_bp_cd_status_rej_rate_p = sf.p_chart_limits(
  dat=hdr_bp_cd_status_rej_rate,
  numerator_val = 'reject_count',
  denominator_val = 'total_count',
  sort_val = 'month_elig',
  multi_strats=True,
  strats=['hdr_bp_cd']
)

focal_hdr_bp_cds = ['TRAN', 'TZGQ', 'DHS', 'NAVI']
focal_hdr_bp_cd_rates = hdr_bp_cd_status_rej_rate_p \
  [hdr_bp_cd_status_rej_rate_p['hdr_bp_cd'].isin(focal_hdr_bp_cds)]
  
# plot
def p_plot_ts_strats(dat, xval, yval):

    fig, axs = plt.subplots(len(focal_hdr_bp_cds), 1, figsize=(8.5, 11))
    axs = axs.flatten()  # Flatten the 2D array of axes into a 1D array

    for i, hdr_bp_cd in enumerate(focal_hdr_bp_cds, start=1):
        ax = axs[i-1]
        plot_dat = dat[dat['hdr_bp_cd'] == hdr_bp_cd].reset_index(drop=True)

        sns.scatterplot(data=plot_dat, x=xval, y=yval, marker='o', color='blue', s=50, ax=ax, zorder=2) 
        sns.lineplot(data=plot_dat, x=xval, y='lcl_prime', color='gray', linestyle='--', ax=ax)
        sns.lineplot(data=plot_dat, x=xval, y='p_bar', color='gray', linestyle='--', ax=ax)
        sns.lineplot(data=plot_dat, x=xval, y='ucl_prime', color='gray', linestyle='--', ax=ax)

        ax.set_title(hdr_bp_cd, size=12)
        ax.grid(False)

    fig.tight_layout(rect=[0, .15, 1, 1])
    fig.subplots_adjust(hspace=0.5, wspace=0.15)
    plt.show()

p_plot_ts_strats(focal_hdr_bp_cd_rates, 'month_elig', 'rej_rate')


# ------------------------------------------------------------------------------------
# ## Example 7. U-Chart for time-series with different categories
# ------------------------------------------------------------------------------------
pcp_pmpm = dl.pcp_pmpm_data()
pcp_pmpm['month_elig'] = pd.to_datetime(pcp_pmpm['month_elig'])

pcp_pmpm_u = sf.u_chart_limits(
  dat=pcp_pmpm,
  numerator_val = 'pcp_count',
  denominator_val = 'mem_count',
  sort_val = 'month_elig',
  multi_strats=False
)

# Plot  
sf.shewhart_plot(
  chart_type = 'U',
  dat = pcp_pmpm_u,
  xval = 'month_elig',
  yval = 'pcp_pmpm',
  prime_controls=False,
  better_direction='none',
  title='PCP PMPM Trend',
  xlabel='Service Month',
  ylabel='PMPM',
  show_x_ticks=True,
  show_sc_labels=True,
  show_specific_obs=[])
