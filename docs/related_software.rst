****************
Related software
****************

There are a handful of other packages that may be helpful when working with 
microplate experiments.  Most of these packages parse plate layouts from 
spreadsheet files.  In contrast, wellmap parses layout information from text 
files using a file format designed specifically for encoding plate layouts.  As 
a result, these files are:

- Less redundant.
- Easier to read.
- Easier to write.

Wellmap also includes a tool for visualizing plate layouts, which makes it easy 
to see if there's a mistake in your layouts.  None of the alternatives provide 
a comparable tool.

plater_
=======
An R library that parses plate layouts from a spreadsheet files into tidy data 
frames.  The documentation is excellent and the library is easy to use.  
Multiple plates are supported, and in some cases the data and the layout can be 
put in the same file.  The biggest drawback (other than using spreadsheets to 
store layout information and not providing a way to visualize layouts) is that 
it cannot be used with python.

plate_map_to_list_
==================
A command-line tool that converts spreadsheet files containing plate layouts 
into tidy CSV or TSV files.  By virtue of being a command-line program, this 
can be used no matter what language your analysis scripts are written in.  
However, the command-line approach depends on generated intermediate files, 
which may clutter up your directories.  More importantly, it's possible for the 
generated files to get out of sync with the original layouts, which could cause 
confusion.  You also have to merge the layout with the experimental data 
yourself, although this is generally a simple operation.

Bioplate_
=========
A python library that can parse plate layouts from spreadsheet files.  However, 
no easy way is provided to merge this layout information with experimental 
data.

Plateo_
=======
A python library focused on simulating robotic pipetting protocols.  It can 
parse plate layouts from spreadsheet files, but does not provide an easy way to 
merge this information with experimental data.

cellHTS_
========
An R library focused on analyzing data from high-throughput RNAi experiments.  
The pipeline involves a bespoke file format for describing plate layouts, but 
it is not suitable for general use.

platetools_
===========
An R library that seems related to microplate layouts.  I can't figure out 
exactly what it does, though; the documentation is inscrutable.

.. _Plateo: https://edinburgh-genome-foundry.github.io/Plateo/index.html
.. _Bioplate: https://hatoris.github.io/BioPlate/basic_usage.html
.. _plater: https://cran.r-project.org/web/packages/plater/vignettes/plater-basics.html
.. _platetools: https://cran.r-project.org/web/packages/platetools/platetools.pdf
.. _cellHTS: http://bioconductor.org/packages/release/bioc/html/cellHTS2.html
.. _plate_map_to_list: https://github.com/craic/plate_maps
