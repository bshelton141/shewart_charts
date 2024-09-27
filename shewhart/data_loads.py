import pkg_resources
import pandas as pd


def enc_submits_monthly():
    """Return a dataframe that provides monthly total encounters volumes.
    
    Contains the following fields:
        rcvd_month      68 non-null object
        enc_count       68 non-null object
        val             68 non-null object
    ... (docstring truncated) ...
    """
    # This is a stream-like object. If you want the actual info, call
    # stream.read()
    stream = pkg_resources.resource_stream(__name__, 'data/enc_submits_monthly.csv')
    return pd.read_csv(stream)


def enc_by_formtype_monthly():
    """Return a dataframe that provides monthly utilization count by medical encounter type.
    
    Contains the following fields:
        rcvd_month      68 non-null object
        file_fmt_cd     68 non-null object
        enc_count       68 non-null object
    ... (docstring truncated) ...
    """
    # This is a stream-like object. If you want the actual info, call
    # stream.read()
    stream = pkg_resources.resource_stream(__name__, 'data/enc_by_formtype_monthly.csv')
    return pd.read_csv(stream)


def enc_reject_rate_monthly():
    """Return a dataframe that provides monthly utilization rejected encounters, total enounters,
       and rejection rate.
    
    Contains the following fields:
        month_elig      68 non-null object
        reject_count    68 non-null object
        total_count     68 non-null object
        rej_rate        68 non-null object
    ... (docstring truncated) ...
    """
    # This is a stream-like object. If you want the actual info, call
    # stream.read()
    stream = pkg_resources.resource_stream(__name__, 'data/enc_reject_rate_monthly.csv')
    return pd.read_csv(stream)


def tran_office_rej_by_ppg():
    """Return a dataframe for a 6-month period of Jul 2023 thru Dec 2023 of internally-rejected 
       office place of service encounters ('10', '11', '49', '72') from Transunion submissions,
       by PPG.
    
    Contains the following fields:
        ppg_code        68 non-null object
        reject_count    68 non-null object
        total_count     68 non-null object
        rej_rate        68 non-null object
    ... (docstring truncated) ...
    """
    # This is a stream-like object. If you want the actual info, call
    # stream.read()
    stream = pkg_resources.resource_stream(__name__, 'data/tran_office_rej_by_ppg.csv')
    return pd.read_csv(stream)


def hdr_bp_cd_status_rej_rate():
    """Return a dataframe that provides monthly utilization rejected encounters, total enounters,
       and rejection rate by encounter submission entity.
    
    Contains the following fields:
        month_elig      68 non-null object
        hdr_bp_cd       68 non-null object
        reject_count    68 non-null object
        total_count     68 non-null object
        rej_rate        68 non-null object
    ... (docstring truncated) ...
    """
    # This is a stream-like object. If you want the actual info, call
    # stream.read()
    stream = pkg_resources.resource_stream(__name__, 'data/hdr_bp_cd_status_rej_rate.csv')
    return pd.read_csv(stream)


def pcp_pmpm_data():
    """Return a dataframe that provides monthly PCP utilization and member month counts, as well
       as the calculated per member per month (PMPM) measure.
    
    Contains the following fields:
        month_elig      68 non-null object
        pcp_count       68 non-null object
        mem_count       68 non-null object
        pcp_pmpm        68 non-null object
    ... (docstring truncated) ...
    """
    # This is a stream-like object. If you want the actual info, call
    # stream.read()
    stream = pkg_resources.resource_stream(__name__, 'data/pcp_pmpm_data.csv')
    return pd.read_csv(stream)
