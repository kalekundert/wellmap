**************
Bradford assay
**************

The following layout was used to measure the concentration of purified protein 
mutants using a Bradford assay.  There are a few things worth noting for this 
example:

.. rst-class:: paragraph-list

- The same standard curve can be used for many experiments, so it makes sense 
  to keep those concentrations in a separate file, to be included as necessary.  
  Specifying these concentrations in a single place reduces redundancy and 
  decreases the chance of making mistakes.  
  
- The wells in the standard curve layout are specified using |block| instead of 
  |row| and |col|.  This makes it safe to include the standard curve in other 
  layouts, because the blocks won't grow as more wells are added to the layout.
  
- The ``[bradford]`` table provides information on how to parse the data.  In 
  particular, my lab has two different brands of plate reader, and they produce 
  output in different formats, so the analysis script needs to know which 
  format to expect.  (The absorbance information is also needed to parse the 
  data file, frustratingly, because the BioTek output format is ridiculous.)  
  This information can be accessed in analysis scripts via the **meta** 
  argument to `load()`:

  .. code-block:: pycon

    >>> import wellmap
    >>> df, meta = wellmap.load('bradford_assay.toml', meta=True)
    >>> meta.extras
    {'bradford': {'format': 'biotek', 'absorbance': '595/450'}}

.. example:: bradford_standards.toml bradford_assay.toml
