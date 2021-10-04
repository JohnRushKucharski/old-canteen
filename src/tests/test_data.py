#region Header
# %% [markdown]
# # Unit Tests for data.py
# 
# Author: John Kucharski | Date: 28 Aug 2021
# 
# Status: open 
# Testing: n/a
#endregion

#region Dependencies
# %%
import sys
import unittest
import datetime

import numpy as np

sys.path.insert(0, '/Users/johnkucharski/Documents/source/canteen')
import src.data as data
#endregion

#%%
class Test_Data(unittest.TestCase):
    def test_print_for_default_input(self):
        test_obj = data.Input(datetime.datetime(2021, 8, 28), 10)
        s = test_obj.print()
        self.assertEqual(test_obj.print(), '28 Aug 2021 (inflow: 10, storage: nan, additional inputs: none)')

    def test_to_dict_for_default_input(self):
        test_obj = data.Input(datetime.datetime(2021, 9, 10), 10)
        self.assertEqual(test_obj.to_dict(), {'date': test_obj.date.strftime("%d %b %Y"), 'inflow': 10, 'storage': np.NaN})
    
    def test_to_dict_default_with_additional_inputs(self):
         test_obj = data.Input(datetime.datetime(2021, 9, 10), 10, additional_inputs= {'temp': data.Additional_Input(72), 'salinity': data.Additional_Input(2)})
         self.assertEqual(test_obj.to_dict(), {'date': test_obj.date.strftime("%d %b %Y"), 'inflow': 10, 'storage': np.NaN, 'temp': 72, 'salinity': 2})
    
    def test_to_dict_default_with_additional_input_marked_as_output_is_represed(self):
         test_obj = data.Input(datetime.datetime(2021, 9, 10), 10, additional_inputs= {'temp': data.Additional_Input(72), 'salinity': data.Additional_Input(2, output=True)})
         self.assertEqual(test_obj.to_dict(), {'date': test_obj.date.strftime("%d %b %Y"), 'inflow': 10, 'storage': np.NaN, 'temp': 72})     
