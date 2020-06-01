#!/usr/bin/env python3

import pytest

@pytest.fixture(autouse=True)
def _docdir(request):

    # Trigger ONLY for the doctests.
    doctest_plugin = request.config.pluginmanager.getplugin("doctest")
    if isinstance(request.node, doctest_plugin.DoctestItem):

        # Figure out which directory to run from.  If there's a directory with 
        # the same name as the file being tested, use that.  Otherwise, use the 
        # directory containing the test file.

        cwd = request.fspath.new(ext='')
        if not cwd.check(dir=True):
            cwd = request.fspath.dirpath()

        with cwd.as_cwd():
            yield

    else:
        # For normal tests, we have to yield, since this is a yield-fixture.
        yield
