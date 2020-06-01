*********************
β-galactosidase assay
*********************

The following layout was used to measure the expression of β-galactosidase in 
different conditions.  Particularly noteworthy are the *fit_start_min* and 
*fit_stop_min* parameters.  In this assay, the concentration of the enzyme is 
deduced from a linear fit of absorbance over time (measured using a plate 
reader).  However, the reaction becomes non-linear as the substrate is 
exhausted, which happens at different times for different conditions (i.e.  
depending on how much enzyme is expressed).  The *fit_start_min* and 
*fit_stop_min* parameters specify which data points are in the linear regime.  
The default is to use the data points between 5–30 min, but several wells use 
different cutoffs to better fit the data.  This is an good example of how the 
fine-grained control provided by :mod:`wellmap` can be used to facilitate 
analysis.

.. example:: beta_gal_assay.toml
