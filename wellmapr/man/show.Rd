% Generated by roxygen2: do not edit by hand
% Please edit documentation in R/wellmapr.R
\name{show}
\alias{show}
\title{Visualize the given microplate layout.}
\usage{
show(toml_path, attrs = NULL, color = "rainbow")
}
\arguments{
\item{toml_path}{The path to a file describing the layout of one or more plates.  See the
\href{https://wellmap.readthedocs.io/en/latest/file_format.html}{file format documentation}
for details about this file.}

\item{attrs}{A list of attributes from the above TOML file to visualize.  For example, if
the TOML file contains something equivalent to \code{well.A1.conc = 1}, then
\code{conc} would be a valid attribute.  If no attributes are specified, the
default is to display any attributes that have at least two different
values.}

\item{color}{The name of the color scheme to use.  Each different value for each
different attribute will be assigned a color from this scheme.  Any name
understood by either \href{http://colorcet.pyviz.org/}{colorcet} or
\href{https://matplotlib.org/examples/color/colormaps_reference.html}{matplotlib}
can be used.}
}
\description{
It's wise to visualize TOML layouts before doing any analysis, to ensure
that all of the wells are correctly annotated.  The \code{wellmap} command-line
program is a useful tool for doing this, but sometimes it's more convenient
to make visualizations directly from R/Rstudio.  That's what this function
is for.
}
