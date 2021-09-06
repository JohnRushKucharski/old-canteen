#region Header
# %% [markdown]
# # Unit Tests for data.py
# 
# Author: John Kucharski | Date: 28 Aug 2021
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
import src.data as data
#endregion

class Test_Data(unittest.TestCase):
    def test_print_for_default_input(self):
        test_obj = data.Input(datetime.datetime(2021, 8, 28), 10)
        s = test_obj.print()
        self.assertEqual(test_obj.print(), '28 Aug 2021 (inflow: 10, storage: nan, additional inputs: none)')

# %%
