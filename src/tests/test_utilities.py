#region Header
# %% [markdown]
# # Unit Tests for Utilities.py
# 
# Author: John Kucharski | Date: 05 May 2021
# 
# Status: open
# Testing: n/a

# %% [markdown]
# ## Dependencies
# %%
import datetime
import unittest

import numpy as np

import src.utilities as utilities
import src.outlet as outlet
#endregion

# %%
class Test_Utilities(unittest.TestCase):  

    # %% [markdown]
    # ## doy_to_dowy() unit tests    
    # %%
    def test_doy_to_dowy_01oct_no_leap_year_returns_1(self):
        '''
        Tests that 01 Oct [274] is converted to the 1st day in the water year           
        '''
        self.assertEqual(utilities.doy_to_dowy(274), 1)
    def test_doy_to_dowy_01oct_leap_year_returns_1(self):
        '''
        Tests that 01 Oct [275 (+1 for 29 Feb)] is converted to the 1st day in the water year           
        '''
        self.assertEqual(utilities.doy_to_dowy(275, True), 1)
    def test_doy_to_dowy_01jan_returns_92(self):
        '''
        Tests that 01 Jan is converted to the 93rd day in the water year
            Oct[31] + Nov[30] + Dec[31] + Jan[1] = 93
        '''
        self.assertEqual(utilities.doy_to_dowy(1), 93)
    def test_doy_to_dowy_28feb_returns_151(self):
        '''
        Tests that 28 Feb [58] is converted to the 151st day in the water year
            92 + Jan[30] + Feb[28] = 92 + 59 = 151
        '''
        actual = utilities.doy_to_dowy(59)
        self.assertEqual(utilities.doy_to_dowy(59), 92 + 59)
    def test_doy_to_dowy_29feb_returns_152(self):
        '''
        Tests that 29 Feb [59] is converted to the 152nd day in the water year
            92 + Jan[30] + Feb[29] = 92 + 60 = 152
        '''
        self.assertEqual(utilities.doy_to_dowy(60, True), 92 + 60)
    def test_doy_to_dowy_30sep_no_leap_year_returns_365(self):
        '''
        Tests that 30 Sep[273] is converted to the 365th day in the water year
        '''
        self.assertEqual(utilities.doy_to_dowy(273), 365)
    def test_doy_to_dowy_30sep_leap_year_returns_366(self):
        '''
        Tests that 30 Sep[274 (+1 for 29 Feb)] is converted to the 365th day in the water year
        '''
        self.assertEqual(utilities.doy_to_dowy(274, True), 366)
    
    # %% [markdown]
    # ## datetime_to_dowy() unit tests
    # %%    
    def test_datetime_to_dowy_01oct_no_leap_year_returns_1(self):
        '''
        Tests that 01 Oct 2021 is converted to the 1st day in the water year 
        '''
        oct01 = datetime.datetime(year = 2021, month = 10, day = 1)
        self.assertEqual(utilities.datetime_to_dowy(oct01), 1)       
    def test_datetime_to_dowy_01oct_leap_year_returns_1(self):
        '''
        Tests that 01 Oct 2020 (+1 for 29 Feb) is converted to the 1st day in the water year           
        '''
        oct01 = datetime.datetime(year = 2020, month = 10, day = 1)
        self.assertEqual(utilities.datetime_to_dowy(oct01), 1)     
    def test_datetime_to_dowy_29feb_returns_152(self):
        '''
        Tests that 29 Feb is converted to the 152 day in the water year
            92 + Jan[30] + Feb[29] = 92 + 60 = 152
        '''
        feb29 = datetime.datetime(year = 2020, month = 2, day = 29)
        self.assertEqual(utilities.datetime_to_dowy(feb29), 152)

    
    # %% [markdown]
    # ## is_on_range unit tests
    # %%
    def test_is_on_range_0_on_neg1_to_pos1_returns_True(self):
        '''
        Tests that 0 on [-1, 1] returns (True, '')
        '''
        retval = utilities.is_on_range(0, -1, 1)
        self.assertTupleEqual(retval, (True, None))
    def test_is_on_range_0_on_neg1_to_posinf_returns_True(self):
        '''
        Tests that 0 on [-1, np.inf] returns (True, '')
        '''
        retval = utilities.is_on_range(0, -1, np.inf)
        self.assertTupleEqual(retval, (True, None))
    def test_is_on_range_0_on_neginf_to_posinf_returns_True(self):
        '''
        Tests that 0 on [-np.inf, np.inf] returns (True, '')
        '''
        retval = utilities.is_on_range(0, -np.inf, np.inf)
        self.assertTupleEqual(retval, (True, None))
    def test_is_on_range_posinf_on_neginf_to_posinf_returns_True(self):
        '''
        Tests that np.inf on [-np.inf, np.inf] returns (True, '')
        '''
        retval = utilities.is_on_range(np.inf, -np.inf, np.inf)
        self.assertTupleEqual(retval, (True, None))
    
    # %%[markdown]
    # ## closures
    # %%
    def test_f_on_domain_on_domain_returns_expected_value(self):
        def simple(x: float) -> float:
            return x
        f = utilities.f_close_on_domain(simple, 0, 1)
        self.assertEqual(f(0.5), 0.5)
    def test_f_on_domain_below_domain_returns_nan(self):
        def simple(x: float) -> float:
            return x
        f = utilities.f_close_on_domain(simple, 0, 1)
        self.assertTrue(np.isnan(f(-1)))
    def test_f_on_domain_above_domain_returns_non(self):
        def simple(x: float) -> float:
            return x
        f = utilities.f_close_on_domain(simple, 0, 1)
        self.assertTrue(np.isnan(f(2)))
        
    def test_f_on_range_on_range_returns_expected_value(self):
        def simple(x: float) -> float:
            return x
        f = utilities.f_close_on_range(simple, 0, 1)
        self.assertEqual(f(0.5), 0.5)
    def test_f_on_range_below_range_returns_nan(self):
        def simple(x: float) -> float:
            return x
        f = utilities.f_close_on_range(simple, 0, 1)
        self.assertTrue(np.isnan(f(-1)))
    def test_f_on_range_above_range_returns_non(self):
        def simple(x: float) -> float:
            return x
        f = utilities.f_close_on_range(simple, 0, 1)
        self.assertTrue(np.isnan(f(2)))
        
    def test_f_on_domain_then_f_on_range_on_domain_above_range_returns_nan(self): 
        def simple(x: float) -> float:
            return x
        f = utilities.f_close_on_domain(simple, 0, 4)
        g = utilities.f_close_on_range(f, 1, 2)
        self.assertTrue(np.isnan(g(3)))
    def test_f_on_domain_then_f_on_range_above_domain_on_range_returns_nan(self): 
        def simple(x: float) -> float:
            return x
        f = utilities.f_close_on_domain(simple, 1, 2)
        g = utilities.f_close_on_range(f, 0, 4)
        self.assertTrue(np.isnan(g(3)))

    def test_f_interpolate_from_data_default_interpolator_min_domain_input_returns_min_on_range(self):
        xs = [0, 1, 2]
        ys = [1, 2, 3]
        f = utilities.f_interpolate_from_data(xs, ys)
        self.assertEqual(f(0), 1)
    def test_f_interpolate_from_data_default_interpolator_interpolated_input_returns_interpolated_result(self):
        xs = [0, 1, 2]
        ys = [1, 2, 3]
        f = utilities.f_interpolate_from_data(xs, ys)
        self.assertEqual(f(0.5), 1.5)
    def test_f_interpolate_from_data_extrapolate_hi_above_range_returns_extrapolated_value(self):
        xs = [0, 1, 2]
        ys = [1, 2, 3]
        f = utilities.f_interpolate_from_data(xs, ys, extrapolate_hi=100)
        self.assertEqual(f(3), 100)
    def test_f_interpolate_from_data_extrapolate_lo_above_range_returns_extrapolated_value(self):
        xs = [0, 1, 2]
        ys = [1, 2, 3]
        f = utilities.f_interpolate_from_data(xs, ys, extrapolate_lo=-100)
        self.assertEqual(f(-0.1), -100)
        
    def test_f_interpolate_from_data_then_f_on_domain_then_f_on_range_input_below_domain_returns_nan(self):
        xs = [0, 1, 2]
        ys = [1, 2, 3]
        f = utilities.f_interpolate_from_data(xs, ys)
        g = utilities.f_close_on_domain(f, 1, 2)
        h = utilities.f_close_on_range(g, 0, 4)
        self.assertTrue(np.isnan(h(0)))
        
    def test_f_interpolate_from_data_then_f_on_domain_then_f_on_range_input_below_range_returns_nan(self):
        xs = [0, 1, 2]
        ys = [1, 2, 3]
        f = utilities.f_interpolate_from_data(xs, ys)
        g = utilities.f_close_on_domain(f, 0, 4)
        h = utilities.f_close_on_range(g, 2, 3)
        self.assertTrue(np.isnan(h(0)))

