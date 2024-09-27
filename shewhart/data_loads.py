import pkg_resources
import pandas as pd


def claim_submits_monthly():
    """Return a synthetic dataframe that provides monthly total encounters volumes.
    
    Contains the following fields:
        rcvd_month      68 non-null object
        claim_volume       68 non-null object
    ... (docstring truncated) ...
    """
    # This is a stream-like object. If you want the actual info, call
    # stream.read()
    stream = pkg_resources.resource_stream(__name__, 'data/claim_submits_monthly.csv')
    return pd.read_csv(stream)


def claim_submits_monthly_by_formtype():
    """Return a synthetic dataframe that provides monthly utilization count by medical encounter type.
    
    Contains the following fields:
        rcvd_month      68 non-null object
        formtype     68 non-null object
        claim_volume       68 non-null object
    ... (docstring truncated) ...
    """
    # This is a stream-like object. If you want the actual info, call
    # stream.read()
    stream = pkg_resources.resource_stream(__name__, 'data/claim_submits_monthly_by_formtype.csv')
    return pd.read_csv(stream)


def claim_reject_rate_monthly():
    """Return a synthetic dataframe that provides monthly utilization rejected encounters, total enounters,
       and rejection rate.
    
    Contains the following fields:
        service_month      68 non-null object
        reject_count    68 non-null object
        total_count     68 non-null object
        reject_rate        68 non-null object
    ... (docstring truncated) ...
    """
    # This is a stream-like object. If you want the actual info, call
    # stream.read()
    stream = pkg_resources.resource_stream(__name__, 'data/claim_reject_rate_monthly.csv')
    return pd.read_csv(stream)


def claim_reject_rate_by_clinic():
    """Return a synthetic dataframe for a 6-month period of rejected utilization submissions,
       by synthetic provider group.
    
    Contains the following fields:
        clinic        68 non-null object
        reject_count    68 non-null object
        total_count     68 non-null object
        reject_rate        68 non-null object
    ... (docstring truncated) ...
    """
    # This is a stream-like object. If you want the actual info, call
    # stream.read()
    stream = pkg_resources.resource_stream(__name__, 'data/tran_office_rej_by_ppg.csv')
    return pd.read_csv(stream)


def claim_reject_rate_monthly_by_submitter():
    """Return a synthetic dataframe that provides monthly utilization rejected encounters, total enounters,
       and rejection rate by encounter submission entity.
    
    Contains the following fields:
        service_month      68 non-null object
        submitter       68 non-null object
        reject_count    68 non-null object
        total_count     68 non-null object
        reject_rate        68 non-null object
    ... (docstring truncated) ...
    """
    # This is a stream-like object. If you want the actual info, call
    # stream.read()
    stream = pkg_resources.resource_stream(__name__, 'data/claim_reject_rate_monthly_by_submitter.csv')
    return pd.read_csv(stream)


def util_pmpm():
    """Return a synthetic dataframe that provides monthly utilization and member month counts, as well
       as the calculated per member per month (PMPM) measure.
    
    Contains the following fields:
        service_month     68 non-null object
        util_count       68 non-null object
        mem_count       68 non-null object
        pmpm        68 non-null object
    ... (docstring truncated) ...
    """
    # This is a stream-like object. If you want the actual info, call
    # stream.read()
    stream = pkg_resources.resource_stream(__name__, 'data/util_pmpm.csv')
    return pd.read_csv(stream)
