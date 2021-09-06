#region Header
# %% [markdown]
# # Outlet
# This file provides a data container for stuctures used to make releases from reservoirs.
#
# Author: John Kucharski | Date: 11 June 2021
# 
# Status: open to extension, closed to change [s*O*lid] :)
# Testing: mostly done

# %% [markdown]
# todo:
# * active/inactive boolean switch? note this would introduce a mutable state
# * release(volume: float) -> float method? for tainter gates, weirs etc.

# %% [markdown]
# Dependencies
# %%
import sys
import typing

import numpy as np

sys.path.insert(0, '/Users/johnkucharski/Documents/source/canteen')
import src.utilities as utilities
#endregion




# %%
class Outlet:
    '''
    Data container for release structures (gates, spillways, etc.) at reservoirs.
    '''
    def __init__(self, name: str = 'default', location: float = 0, f_max_release: typing.Callable[[float], float] = None) -> None:
        # w/o validation
        self._name = name
        self._errors = []
        # w/ validation logic
        self._is_valid = True
        self._location = self.__set_location(location)
        self._f_max_release = self.__set_f_max_release(f_max_release)     
    
    @property
    def name(self) -> str:
        return self._name
    @property
    def location(self) -> float:
        return self._location
    def __set_location(self, location: float) -> None:
        is_valid, msg = utilities.is_on_range(location, 0, np.inf, 'location', 'Outlet.__set_location()')
        if not is_valid:
            self._is_valid = is_valid   #False
            self._errors.append(f'{self.name} outlet: {msg.message}')
        return location
    @property
    def f_max_release(self):
        return self._f_max_release
    def __set_f_max_release(self, f_max_release: typing.Callable[[float], float]) -> typing.Callable[[float], float]:
        if f_max_release == None:
            def inner(volume: float) -> float:
                return volume - self.location if volume > self.location else 0
            return inner
        else:
            return f_max_release    
    @property
    def is_valid(self) -> bool:
        return self._is_valid
    @property
    def errors(self) -> typing.List[str]:
        return self._errors
    
    def max_release(self, volume: float) -> float:
        return self.f_max_release(volume)
    
    def print(self, digits: int = 0):
        '''
        Prints a string representation of the outlet object.
        
        Args:
            digits[int]: the number of digits to which the location and max_release parameters should be rounded. 0 by default.
        Returns:
            A string in the format: name(location: value, max_release: value)
        '''
        return f'{self.name}(location: {round(self.location, digits)})'

def select_outlets(names: typing.List[str], outlets: typing.List[Outlet]) -> typing.List[str]:
    items = set()
    for name in names:
        items.update([x for x in outlets if x.name == name])
    return list(items)
def deselect_outlets(names: typing.List[str], outlets: typing.List[Outlet]) -> typing.List[str]:
    items = set()
    for name in names:
        items.update([x for x in outlets if x.name != name])
    return list(items)
def select_outlet(name: str, outlets: typing.List[Outlet]) -> Outlet:
    return [x for x in outlets if x.name == name][0]