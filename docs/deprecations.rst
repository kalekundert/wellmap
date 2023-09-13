************
Deprecations
************

This pages lists features that have been slated for removal from wellmap.  The 
goal is to briefly explain the reason for removing each feature, and to show 
how to update old code at a glance.

A `DeprecationWarning` is issued when any of these features is used.  However, 
be aware that python makes an effort to only show such warnings to "developers" 
and not to "users".  See :pep:`565` for details.

From the first release where a feature is deprecated, the deprecated behavior 
is guaranteed to remain available for at least two years.  The feature will be 
removed in the next major release after that.

.. _load-extras-deps:

The *extras* and *report_dependencies* arguments to `wellmap.load()`
====================================================================
Both of these arguments request that the `load()` function return additional 
information about the layout file.  It seems likely that more and more similar 
arguments will be added over time, so to avoid having to keep changing the 
signature of `load()`, these arguments were consolidated into a single 
:class:`~wellmap.Meta` object.  See :issue:`38` for more information.

Old syntax (available until at least November 2025):

.. code::

  df, extras, deps = wellmap.load(
          'path/to/layout.toml',
          extras=True,
          report_dependencies=True,
  )

New syntax (available since version 3.5):

.. code::

  df, meta = wellmap.load('path/to/layout.toml', meta=True)
  extras = meta.extras
  deps = meta.dependencies
