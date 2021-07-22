#region Header
# %% [markdown]
# # Unit Tests for Simulation.py
# 
# Author: John Kucharski | Date: 06 July 2021
# 
# Status: open 
# Testing: n/a

# %% [markdown]
# ## Dependencies
# %%
import sys
import unittest

import datetime as datetime

import numpy as np

sys.path.insert(0, '/Users/johnkucharski/Documents/source/canteen')
import src.simulation as simulation
#endregion

class Test_Simulation(unittest.TestCase):
    def test_Input_simple_data_default_returns_valid_data(self):
        test_obj = simulation.Input(datetime.datetime(1, 1, 1), 1)
        is_valid = True if (test_obj.date == datetime.datetime(1, 1, 1) and test_obj.volume == 1.0 and test_obj.maps == None) else False
        self.assertTrue(is_valid)
    def test_create_inputs_list_of_volumes_no_other_input_returns_volumes_with_dates_starting_Jan01_0001(self):
        inputs = [0, 0, 0]
        test_obj = simulation.Input.create_inputs(inputs)
        this = True