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
  
- The ``[bradford]`` block provides information on how to parse and interpret 
  the data, e.g. what format the data is in and what wavelengths were measured.  
  This information can be accessed in analysis scripts via the **extras** 
  argument to `load()`:

  .. code-block:: pycon

    >>> import wellmap
    >>> df, ex = wellmap.load('bradford_assay.toml', extras='bradford')
    >>> ex
    {'format': 'biotek', 'absorbance': '595/450'}

.. example:: bradford_standards.toml bradford_assay.toml
