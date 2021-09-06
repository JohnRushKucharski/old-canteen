#region Header
# %% [markdown]
# # Unit Tests for operations.py
# 
# Author: John Kucharski | Date: 28 June 2021
# 
# Status: open 
# Testing: n/a

# %% [markdown]
# ## Dependencies
# %%
import sys
import unittest
import datetime

import numpy as np

sys.path.insert(0, '/Users/johnkucharski/Documents/source/canteen')
from src.outlet import Outlet
import src.reservoir as reservoir
import src.operations as ops
import src.data as data
#endregion

class Test_Operations(unittest.TestCase):  
    #region Rule_Curve class tests
    def test_Rule_Curve_rules_sorted(self):
        obj = ops.Rule_Curve(date_target_pairs= [(datetime.datetime(2021, 9, 27), 0), (datetime.datetime(2021, 10, 1), 0), (datetime.datetime(2021, 9, 29), 1)])
        exp = [(1, 0), (362, 0), (364, 1)]
        self.assertListEqual(obj.day_of_water_year_target_pairs, exp)
    def test_Rule_Cuve_expected_sequence_of_days(self):
        obj = ops.Rule_Curve(date_target_pairs= [(datetime.datetime(2021, 9, 27), 0), (datetime.datetime(2021, 10, 1), 0), (datetime.datetime(2021, 9, 29), 1)])
        exp = [1, 362, 364]
        self.assertListEqual(obj.days, exp)
    def test_Rule_Cuve_expected_sequence_of_targets(self):
        obj = ops.Rule_Curve(date_target_pairs= [(datetime.datetime(2021, 9, 27), 0), (datetime.datetime(2021, 10, 1), 0), (datetime.datetime(2021, 9, 29), 1)])
        exp = [0, 0, 1]
        self.assertListEqual(obj.targets, exp)
    def test_Rule_Cuve_default_end_of_water_year_returns_365(self):
        obj = ops.Rule_Curve(date_target_pairs= [(datetime.datetime(2021, 9, 27), 0), (datetime.datetime(2021, 10, 1), 0), (datetime.datetime(2021, 9, 29), 1)])
        self.assertEquals(obj.end_of_water_year, 365)
    def test_Rule_Cuve_leap_year_end_of_water_year_returns_366(self):
        obj = ops.Rule_Curve(date_target_pairs= [(datetime.datetime(2021, 9, 27), 0), (datetime.datetime(2021, 10, 1), 0), (datetime.datetime(2021, 9, 29), 1)], leap_year=366)
        self.assertEquals(obj.end_of_water_year, 366)
    
    def test_target_volume_on_dowy_returns_expected_target(self):
        obj = ops.Rule_Curve(date_target_pairs= [(datetime.datetime(2021, 9, 27), 0), (datetime.datetime(2021, 10, 1), 0), (datetime.datetime(2021, 9, 29), 1)])
        self.assertEquals(obj.target_volume(1), 0)
    def test_target_volume_dowy_in_wy_rules_returns_expected__interpolated_target(self):
        obj = ops.Rule_Curve(date_target_pairs= [(datetime.datetime(2021, 9, 27), 0), (datetime.datetime(2021, 10, 1), 0), (datetime.datetime(2021, 9, 29), 1)])
        self.assertEquals(obj.target_volume(363), 0.5)   
    def test_target_volume_dowy_current_wy_to_next_wy_returns_expected_interpolated_target(self):
        obj = ops.Rule_Curve(date_target_pairs= [(datetime.datetime(2021, 9, 27), 0), (datetime.datetime(2021, 10, 1), 0), (datetime.datetime(2021, 9, 29), 1)])
        self.assertEquals(obj.target_volume(365), 0.5) 
    def test_target_volume_dowy_last_wy_to_current_wy_returns_expected_interpolated_target(self):
        obj = ops.Rule_Curve(date_target_pairs= [(datetime.datetime(2021, 9, 27), 0), (datetime.datetime(2021, 10, 2), 0), (datetime.datetime(2021, 9, 30), 1)])
        self.assertEquals(obj.target_volume(1), 0.5)           
    #endregion
    
    #region 'set_release' tests
    def test_passive_operations_default_reservoir_0inflow_0storage_returns_0releases(self):  
        input = data.Input(datetime.datetime(2021, 9, 3), inflow = 0, storage = 0)
        outlets = reservoir.Reservoir().outlets
        result = ops.passive_operations(input, outlets)
        self.assertDictEqual(result, {'spill': 0})
    def test_passive_operations_default_reservoir_1inflow_0storage_returns_0releases(self):  
        input = data.Input(datetime.datetime(2021, 9, 3), inflow = 1, storage = 0)
        outlets = reservoir.Reservoir().outlets
        result = ops.passive_operations(input, outlets)
        self.assertDictEqual(result, {'spill': 0})
    def test_passive_operations_default_reservoir_2inflow_0storage_returns_1release(self):  
        input = data.Input(datetime.datetime(2021, 9, 3), inflow = 2, storage = 0)
        outlets = reservoir.Reservoir().outlets
        result = ops.passive_operations(input, outlets)
        self.assertDictEqual(result, {'spill': 1})
    
    # def test_standard_operating_proceedures_rule_curve_target_volume_default_reservoir_with_default_outlet_simple_rules_volume_of_1_returns_release_of_1(self):
    #     simple_rule = [(1, 0), (362, 0), (364, 1)]
    #     default_reservoir = reservoir.Reservoir(outlets=[Outlet()])
    #     target_volume = ops.set_target_volume.rule_cuve(dowy=1, rules=simple_rule)
    #     actual = ops.set_release.standard_operating_proceedure(default_reservoir, volume=1,  demand=1 - target_volume)
    #     self.assertDictEqual(actual, {'default' : 1})
    #endregion
    


    
