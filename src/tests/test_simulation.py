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
import typing
import unittest

import datetime as datetime

import numpy as np

sys.path.insert(0, '/Users/johnkucharski/Documents/source/canteen')
import src.simulation as simulation
import src.data as data
#endregion

class Test_Simulation(unittest.TestCase):
    def test_input_to_dict_3defaults(self):
        ins = [
            data.Input(datetime.datetime(2021, 9, 10), 10),
            data.Input(datetime.datetime(2021, 9, 11), 10),
            data.Input(datetime.datetime(2021, 9, 12), 10)
        ]
        s = simulation.Simulation(ins)
        self.assertDictEqual(s.input_to_dict(), { 'date': [i.date.strftime("%d %b %Y") for i in ins], 'inflow': [10, 10, 10], 'storage': [np.NaN, np.NaN, np.NaN]})
    def test_input_to_dict_3plusonewitheadditionalinput(self):
        ins = [
            data.Input(datetime.datetime(2021, 9, 10), 10),
            data.Input(datetime.datetime(2021, 9, 11), 10, additional_inputs= {'temp': data.Additional_Input(72)}),
            data.Input(datetime.datetime(2021, 9, 12), 10)
        ]
        s = simulation.Simulation(ins)
        act = s.input_to_dict()
        exp = { 'date': [i.date.strftime("%d %b %Y") for i in ins], 'inflow': [10, 10, 10], 'storage': [np.nan, np.nan, np.nan], 'temp': [np.nan, 72, np.nan]}
        t = act == exp
        self.assertEqual(print(act), print(exp)) #for some dumb reasons self.assertDictEquals fails even though they are the same.
        
    def test_simulate_default(self):
        ins = [
            data.Input(datetime.datetime(2021, 9, 10), 1, storage=0),
            data.Input(datetime.datetime(2021, 9, 11), 1),
            data.Input(datetime.datetime(2021, 9, 12), 1)
        ]
        s = simulation.Simulation(ins)
        act = s.simulate()
        exp = { 
               'date': [i.date.strftime("%d %b %Y") for i in ins], 
               'inflow': [1, 1, 1], 
               'storage': [0, 1, 1], 
               'spill': [0, 1, 1]}
        self.assertDictEqual(act, exp)
    def test_simulate_default_plus_additional_output(self):
        ins = [
            data.Input(datetime.datetime(2021, 9, 10), 1, 0, additional_inputs = {'x': data.Additional_Input(0)}),
            data.Input(datetime.datetime(2021, 9, 11), 1, additional_inputs= {'x': data.Additional_Input(1)}),
            data.Input(datetime.datetime(2021, 9, 12), 1, additional_inputs={'x': data.Additional_Input(2)})
        ]
        def fn(x: data.Input) -> typing.Dict[str, typing.Any]:
            return x.additional_inputs['x'].value + 1
        s = simulation.Simulation(ins, additional_outputs= {'x': simulation.Additional_Output(fn)})
        act = s.simulate()
        exp = { 
               'date': [i.date.strftime("%d %b %Y") for i in ins], 
               'inflow': [1, 1, 1], 
               'storage': [0, 1, 1], 
               'spill': [0, 1, 1],
               'x': [1, 2, 3]}
        self.assertDictEqual(act, exp)