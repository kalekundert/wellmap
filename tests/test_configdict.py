#!/usr/bin/env python3

from wellmap import *

def test_empty():
    config = configdict({})
    assert config.meta == {}
    assert config.rows == {}
    assert config.irows == {}
    assert config.cols == {}
    assert config.icols == {}
    assert config.wells == {}
    assert config.user == {}

def test_user():
    config = configdict({'x': 1})
    assert config.meta == {}
    assert config.rows == {}
    assert config.irows == {}
    assert config.cols == {}
    assert config.icols == {}
    assert config.wells == {}
    assert config.user == {'x': 1}

def test_meta():
    config = configdict({'x': 1, 'meta': {'y': 2}})
    assert config.meta == {'y': 2}
    assert config.rows == {}
    assert config.irows == {}
    assert config.cols == {}
    assert config.icols == {}
    assert config.wells == {}
    assert config.user == {'x': 1}

def test_rows():
    config = configdict({'x': 1, 'row': {'y': 2}})
    assert config.meta == {}
    assert config.rows == {'y': 2}
    assert config.irows == {}
    assert config.cols == {}
    assert config.icols == {}
    assert config.wells == {}
    assert config.user == {'x': 1}

def test_irows():
    config = configdict({'x': 1, 'irow': {'y': 2}})
    assert config.meta == {}
    assert config.rows == {}
    assert config.irows == {'y': 2}
    assert config.cols == {}
    assert config.icols == {}
    assert config.wells == {}
    assert config.user == {'x': 1}

def test_cols():
    config = configdict({'x': 1, 'col': {'y': 2}})
    assert config.meta == {}
    assert config.rows == {}
    assert config.irows == {}
    assert config.cols == {'y': 2}
    assert config.icols == {}
    assert config.wells == {}
    assert config.user == {'x': 1}

def test_icols():
    config = configdict({'x': 1, 'icol': {'y': 2}})
    assert config.meta == {}
    assert config.rows == {}
    assert config.irows == {}
    assert config.cols == {}
    assert config.icols == {'y': 2}
    assert config.wells == {}
    assert config.user == {'x': 1}

def test_wells():
    config = configdict({'x': 1, 'well': {'y': 2}})
    assert config.meta == {}
    assert config.rows == {}
    assert config.irows == {}
    assert config.cols == {}
    assert config.icols == {}
    assert config.wells == {'y': 2}
    assert config.user == {'x': 1}

def test_getattr():
    config = configdict({})
    config.meta['x']  = 1;      assert config.meta  == {'x': 1}
    config.rows['x']  = 2;      assert config.rows  == {'x': 2}
    config.irows['x'] = 3;      assert config.irows == {'x': 3}
    config.cols['x']  = 4;      assert config.cols  == {'x': 4}
    config.icols['x'] = 5;      assert config.icols == {'x': 5}
    config.wells['x'] = 6;      assert config.wells == {'x': 6}

def test_setattr():
    config = configdict({})
    config.meta =  {'x': 1};    assert config['meta']['x'] == 1
    config.rows =  {'x': 2};    assert config['row']['x']  == 2
    config.irows = {'x': 3};    assert config['irow']['x'] == 3
    config.cols =  {'x': 4};    assert config['col']['x']  == 4
    config.icols = {'x': 5};    assert config['icol']['x'] == 5
    config.wells = {'x': 6};    assert config['well']['x'] == 6

