#region Header
# %% [markdown]
# # Unit Tests for Outlet.py
# 
# Author: John Kucharski | Date: 14 June 2021
# 
# Status: open 
# Testing: n/a

# %% [markdown]
# ## Dependencies
# %%
import sys
import unittest

import numpy as np

sys.path.insert(0, '/Users/johnkucharski/Documents/source/canteen')
import src.outlet as outlet
import src.reservoir as reservoir
import src.utilities as utilities
#endregion

# %%
class Test_Map(unittest.TestCase):
    def test_map_simple_inputs_returns_expected_attributes(self):
        def f_simple(x: float) -> float:
            return x
        obj = reservoir.Map(name='simple', f=f_simple)
        self.assertEqual(obj.name, 'simple')
    def test_f_input_equals_output_returns_input(self):
        def f_simple(x: float) -> float:
            return x
        obj = reservoir.Map(name='simple', f=f_simple)
        self.assertEqual(obj.f(1), 1)
    def test_f_with_domain_closure_0_to_inf_input_equals_neg1_returns_nan(self):
        def f_simple(x: float) -> float:
            return x
        f = utilities.f_close_on_domain(f_simple, 0, np.inf)
        obj = reservoir.Map(name='simple', f=f)
        self.assertTrue(np.isnan(obj.f(-1)))
    def test_f_with_domain_and_range_closures_below_range_returns_nan(self):
        def f_simple(x: float) -> float:
            return x - 1
        f = utilities.f_close_on_range(f_simple, 0, np.inf)
        g = utilities.f_close_on_domain(f, 0, np.inf)
        obj = reservoir.Map(name='simple', f=g)
        self.assertTrue(np.isnan(obj.f(0)))
    def test_f_interpolation_closure_linear_interp_in_between_input_returns_interpolated_result(self):
        f = utilities.f_interpolate_from_data([0, 1, 2], [1, 2, 3])
        obj = reservoir.Map(name='simple', f=f)
        self.assertEqual(obj.f(0.5), 1.5)
 
# %%
class Test_Reservoir(unittest.TestCase):
    # %% [markdown]
    # default Reservoir good data tests.
    # %%
    def test_default_reservoir_returns_default_name(self):
        obj = reservoir.Reservoir()
        self.assertEqual('default', obj.name)
    def test_default_reservoir_returns_default_capacity(self):
        obj = reservoir.Reservoir()
        self.assertEqual(1, obj.capacity)
    def test_default_reservoir_returns_default_outlet(self):
        obj = reservoir.Reservoir()
        self.assertEqual(outlet.Outlet(location=1, name = 'spill').print(), obj.outlets[0].print())
    def test_default_reservoir_returns_non_maps(self):
        obj = reservoir.Reservoir()
        self.assertEqual(None, obj.maps)
    def test_print_default_reservoir_returns_expected_str(self):
        obj = reservoir.Reservoir()
        self.assertEqual('default(capacity: 1, outlets: [spill(location: 1)], mapped variables: [None])', obj.print())
    
    
    # %% [markdown]
    # outlets Tests
    # %%
    def test_default_reservoir_with_multiple_outlets_sorted_properly(self):
        obj = reservoir.Reservoir(outlets = [ outlet.Outlet(location = 1, name = 'A'), outlet.Outlet(name = 'B'), outlet.Outlet(name = 'A')])
        exp = [outlet.Outlet(location = 1, name = 'A_@1_0').print(), outlet.Outlet(name = 'A_@0_0').print(), outlet.Outlet(name = 'B').print()]
        act = []
        # test based on print statement
        for i in range(0, len(obj.outlets)):
            act.append(obj.outlets[i].print())
        self.assertListEqual(exp, act)
    def test_default_reservoir_two_outlets_with_same_name_renamed_properly(self):
        obj = reservoir.Reservoir(outlets = [ outlet.Outlet(name = 'A'), outlet.Outlet(name = 'A')])
        exp = [outlet.Outlet(name = 'A_@0_0').print(), outlet.Outlet(name = 'A_@0_1').print()]
        act = []
        for i in range(0, len(obj.outlets)):
            act.append(obj.outlets[i].print())
        self.assertListEqual(exp, act)
    def test_default_reservoir_with_bad_outlet_returns_is_valid_equals_false(self):
        obj = reservoir.Reservoir(outlets = [ outlet.Outlet(location = -1)])
        self.assertEqual(False, obj.is_valid)
    
    # %% [markdown]
    # maps Tests
    # %%
    def test_f_default_resevoir_with_simple_map_1_input_volume_returns_1(self):
        def simple(volume: float) -> float:
            return volume
        m = {reservoir.Map('simple', simple)}
        obj = reservoir.Reservoir(maps=m)
        self.assertEqual(1, obj.f('simple', 1))
    def test_f_default_resevoir_with_simple_map_and_valid_range_closue_neg1_input_volume_returns_nan(self):
        def simple(volume: float) -> float:
            return volume
        obj = reservoir.Reservoir(maps={reservoir.Map('simple', utilities.f_close_on_range(simple, 0, np.inf))})
        self.assertTrue(np.isnan(obj.f('simple', -1)))
    def test_f_default_reservoir_with_npinterp_map_and_interpolation_closure_50_input_volume_linear_interpolation_0_to_100_returns_50(self):
        obj = reservoir.Reservoir(maps={reservoir.Map('npinterp', utilities.f_interpolate_from_data([0, 100], [0, 100]))})
        self.assertEqual(50.0, obj.f('npinterp', 50))
    def test_f_default_reservoir_with_npinterp_map_and_interpolation_closure_neg1_input_volume_linear_interpolation_0_to_100_returns_nan(self):
        obj = reservoir.Reservoir(maps={reservoir.Map('npinterp', utilities.f_interpolate_from_data([0, 100], [0, 100]))})
        self.assertTrue(np.isnan(obj.f('npinterp', -1)))
    def test_print_default_reservoir_with_simple_map_returns_expected_str(self):
        def simple(volume: float) -> float:
            return volume
        obj = reservoir.Reservoir(maps={reservoir.Map('simple', simple)})
        self.assertEqual('default(capacity: 1, outlets: [spill(location: 1)], mapped variables: [simple])', obj.print()) 
    def test_print_default_reservoir_with_two_maps_returns_expected_str(self):
        def simple(volume: float):
            return volume
        def simpleplus1(volume: float):
            return volume + 1
        obj = reservoir.Reservoir(maps={reservoir.Map('simple', simple), reservoir.Map('simpleplus1', simpleplus1)})
        print_line = f'default(capacity: 1, outlets: [spill(location: 1)], mapped variables: '
        var1, var2 = '[simple, simpleplus1])', '[simpleplus1, simple])'
        # z = obj.print()
        # is_valid = True if obj.print() == (print_line + var1) or obj.print() == (print_line + var2) else False
        self.assertEqual(obj.print(), f'{print_line}{var2}')
        #self.assertTrue(is_valid)