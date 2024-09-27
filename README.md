# Python Shewhart Chart Development Functions

This repo's is structured as a Python package that provides Python developers with functions to quickly calculate the appropriate, dynamic control limits when trending data points over time or comparing data points between categories. It also contains a function to visualize the outcomes, giving the user an abstracted approach to color coding and labeling the data visuals.

<br/>

## Contents
- [Shewhart Chart Background](#shewhart_background)
- [Shewhart Chart Types](#shewhart_types)
- [Install and Use the Package](#install_and_use)
- [Contributing to the Package](#contributing)

<br/>

## <a name="shewhart_background"></a>Shewhart Chart Background
Shewhart Charts provide a collective approach for learning about variation within L.A. Care’s processes. They can be applied to both operational and clinical measures, and provide a way of defining the following two types of causes of variation, as defined in the The Health Care Data Guide (2011):

Common Causes: “Those that are inherent in the system (process or product) over time, affect everyone working in the system, and affect all outcomes of the system”.

Special Causes: “Those causes that are not part of the system (process or product) all the time or do not affect everyone, but arise because of specific circumstances”.

Shewhart charts do not identify the drivers of special cause variation, but allows users to quickly identify which components of a process warrant further investigation for understanding.

“[The Health Care Data Guide, Learning from Data Improvement](https://www.amazon.com/Health-Care-Data-Guide-Improvement/dp/1119690137)”, written by Lloyd Provost and Sandra Murray, provides the primary guidance for this repository, and other sources were used to further validate.

<br/>

## <a name="shewhart_types"></a>Shewhart Chart Types

Depending on the type of outcome being measures, there are different types of Shewhart charts that should be applied to the data. The chart below displays some of the frequently used Shewhart chart types, depending on the type of data that is being analyzed. Currently, this package contains functions for calculating the I Chart, P Chart, P' Chart, U Chart, and U' Chart.

![shewhart](https://github.com/user-attachments/assets/ed1eda38-c0a7-4358-b2c1-865ec164988d)


P' and U' Charts are helpful when there is large "normal" variation from observation to observation, as well as when sample sizes and denmoinators are very large (e.g., member months). A more detailed description of when to use the P' and U' charts, as well the underlying calculations that are coded in this package's functions, can be reviewed in David B. Laney's seminal paper on the subject [here](https://sigarra.up.pt/feup/pt/conteudos_service.conteudos_cont?pct_id=38803&pv_cod=5312qaTawyc8).

<br/>

## <a name="install_and_use"></a> Install and Use the Shewhart Package
#### Install
`pip3 install -e git+https://github.com/bshelton141/shewhart_charts.git@main#egg=shewhart`

<br/>

#### Use

The Python code and commands below show how to navigate the Shewhart package, including:
  - Listing all of the package's available functions
  - Using a function's `help` feature
  - A toy example of using a function from the package.

A more extensive tutorial on the package functions can be found in this repositories `shewhart_examples.py` file.
```

# See what functions are available in the package
from shewhart import __all__ as shewhart_listing
shewhart_listing

from shewhart import shewhart_functions as sf

# Read the documentation of a specific function
help(sf.i_chart_limits)

# Run a function
import shewhart.data_loads as dl
enc_submits_monthly = dl.enc_submits_monthly()
df = sf.i_chart_limits(
  dat=enc_submits_monthly,
  focal_val = 'enc_count',
  sort_val = 'rcvd_month',
  multi_strats=False
)

df.head()
```

<br/>

## <a name="contributing"></a>Contributing to the Package
Functions in the `shewhart` Python package are required to have include the following components:

  -  Docstring (help documentation)
     - Description of the function, explaining its usage.
     - Inputs: A bulleted list of the inputs and their decriptions
     - Outputs: A description, of the output fields
     - Example: At least one minimum working example to demonstrate/test the use of the function

  - Error handling and exceptions
    - Raise exceptions on user input errors
    - Include more error checking at runtime on more complicated or resource intensive functions

  - If creating a new function, the function name must be included in the `__init__.py`'s `__all__` list (in alphabetical order) [here](https://dsghe.lacare.org/bshelton/shewhart_charts/blob/main/shewhart/__init__.py).
  
  - All enhancements must go through Pull Request reviews prior to being merged to the `main` branch.

----------------------------------------

## Helpful links on how to write Python functions
 - https://www.tutorialspoint.com/python/python_functions.htm
 - https://en.wikibooks.org/wiki/Python_Programming/Functions

----------------------------------------
