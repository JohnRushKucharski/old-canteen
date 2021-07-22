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
import unittest

import numpy as np

import src.outlet as outlet
#endregion

# %%
class Test_Outlets(unittest.TestCase):
    # %% [markdown]
    # Default outlet good data
    # %%
    def test_default_outlet_returns_default_name(self):
        obj = outlet.Outlet()
        self.assertEqual('default', obj.name)
    def test_default_outlet_returns_location_equals_0(self):
        obj = outlet.Outlet()
        self.assertEqual(0, obj.location)
    def test_default_outlet_max_release_inf_returns_inf(self):
        obj = outlet.Outlet()
        self.assertEqual(np.inf, obj.max_release(np.inf))
    def test_default_outlet_returns_is_valid_equals_True(self):
        obj = outlet.Outlet()
        self.assertEqual(True, obj.is_valid)
    def test_default_outlet_returns_empty_list_of_errors(self):
        obj = outlet.Outlet()
        self.assertListEqual([], obj.errors)

    # %% [markdown]
    # Default but bad location and max_release data tests
    # %%
    def test_location_neg1_returns_is_valid_equals_False(self):
        obj = outlet.Outlet(location = -1)
        self.assertEqual(False, obj.is_valid) 
    def test_location_neg1_returns_error_message(self):
        obj = outlet.Outlet(location = -1)
        z = obj.errors[0]
        self.assertEqual('default outlet: The location input value: -1, of the Outlet.__set_location() method is not on the valid range: [0, inf].', z)
    def test_max_release_neg1_returns_0(self):
        obj = outlet.Outlet()
        self.assertEqual(0, obj.max_release(-1)) 