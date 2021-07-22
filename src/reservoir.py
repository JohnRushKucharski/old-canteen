#region Header
# %% [markdown]
# # Reservoir
#
# Author: John Kucharski | Date: 13 June 2021
#
# Status: open
# Testing: partial
#
# todo:
# * add as a network node
# * state changes, broken gates


# %% [markdown]
# ## Dependencies
# %%
import sys
import typing

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, '/Users/johnkucharski/Documents/source/canteen')
import src.utilities as utilities
import src.outlet as outlet
from src.outlet import Outlet
#endregion

# %%
class Map:
    def __init__(self, name: str, f: typing.Callable[[float], float], inverse_f: typing.Callable[[float], float] = None) -> None:
        self._name = name
        self._f = f
        self._inverse_f = inverse_f

    @property
    def name(self) -> str:
        return self._name
    
    def f(self, volume: float) -> float:
        return self._f(volume)
    def inverse_f(self, y: float) -> float:
        return self._inverse_f(y)


# %%
class Reservoir:
    '''
    Data object for the physical representation of a reservoir, exclusive of its operations and state (e.g. volume)
    '''
    def __init__(self, capacity: float = 1, outlets: typing.List[outlet.Outlet] = 'spill', maps: typing.Set[Map] = None,  name = 'default') -> None:
        self._name = name
        self._errors = []
        self._messages = []
        self._is_valid = True
        # w/ validation logic
        self._capacity = self.__set_capacity(capacity)
        self._outlets = self.__set_outlets(outlets)
        self._maps = self.__set_maps(maps)
    
    @property
    def name(self) -> str:
        return self._name
    @property
    def capacity(self) -> float:
        return self._capacity
    def __set_capacity(self, k: float) -> float:
        is_valid, error = utilities.is_on_range(k, 0, np.inf, 'Reservoir.capacity')
        if not is_valid:
            self._is_valid = False
            self._errors.append(error.message)
        return k
    @property
    def outlets(self) -> typing.List[outlet.Outlet]:
        return self._outlets
    def __set_outlets(self, outlets: typing.List[outlet.Outlet]) -> typing.List[outlet.Outlet]:
        lst = []
        if outlets == 'spill':
            # no outlet provided make default outlet
            lst.append(Outlet(location=self.capacity, name='spill'))
        
        else:        
            # set to id duplicates
            names = [x.name for x in outlets]
            dupes = set([x for x in names if names.count(x) > 1])
            # loop over provided outlets
            _sorted = sorted(outlets, key = lambda x: (-x.location, x.name))
            for i in range(0, len(_sorted)):
                # check for duplicate names
                if _sorted[i].name in dupes:           
                    # make sure "new" name is not duplicate
                    name = f'{_sorted[i].name}_@{_sorted[i].location}_0'
                    if name in dupes:
                        while name in dupes:
                        
                            i = -1
                            s = name[i:]
                            # get number from end of name
                            while s.isnumeric():
                        
                                i = i - 1
                                s = name[i:]
                            # incrment 's' = number at end of name                     
                            name = f'{name[:i + 1]}{int(name[i + 1:]) + 1}'
                    dupes.add(name)
                    lst.append(Outlet(name, _sorted[i].location))
                    self._messages.append(f'Outlet: {_sorted[i].print()} name was changed to: {name}.')
                else:
                    lst.append(_sorted[i])
                
        # check for errors
        for outlet in lst:
            # if an outlet is not valid the reservoir is not valid
            if not outlet.is_valid:
                self._is_valid = False
                self._errors.extend(outlet._errors)
        return lst
    @property
    def maps(self) -> typing.Dict[str, Map]:
        return self._maps 
    def __set_maps(self, maps: typing.Set[Map]) -> typing.Dict[str, Map]:
        if maps == None:
            return None
        else:
            d = {}
            names: typing.Set[str] = {}
            for map in maps:
                if map.name in names:
                    raise AttributeError(f'The map name: {map.name} is duplicated in the set of maps, causing an error.')
                else:
                    d[map.name] = map
            return d 
    @property
    def is_valid(self) -> bool:
        return self._is_valid
    @property
    def messages(self) -> typing.List[str]:
        return self._messages
    @property
    def errors(self) -> typing.List[str]:
        return self._errors  
    
    def f(self, key: str, volume: float) -> float:
        '''
        Calls the function for a named variable that maps volume to the named variable, based on the provided name key and volume.
        '''
        if key in self.maps:
            return self.maps[key].f(volume)
        else:
            raise AttributeError(f'The requested variable: {key}, is not in the dictionary of mapped variables.') 
    def plot_map(self, key: str, xy_pairs: typing.Tuple[typing.List[float], typing.List[float]] = None) -> None:
        fig, ax = plt.subplots(figsize = (10, 15))
        ax.set_title(f'Reservoir volume-{key} relationship')
        ax.set_xlabel('volume')
        ax.set_ylabel(key)
        if xy_pairs == None:
            xs: typing.List[float] = np.arange(0, self.capacity, self.capacity / 10)
            ys: typing.List[float] = [self.f(key, x) for x in xs]
            ax.plot(xs, ys)
        else:
            ax.scatter(xy_pairs[0], xy_pairs[1], edgecolors='grey', facecolors='none', label='observations')
            ax.plot(xy_pairs[0], [self.f(key, x) for x in xy_pairs[0]])
        plt.legend(frameon=False)
        plt.show()     
              
    def print(self, digits = 0):
        '''
        Prints a string representation of the Reservoir object.
        
        Args:
            digits[int]: the number of digits to which the capacity and outlet parameter attributes should be rounded. 0 by default.
        Returns:
            A string in the format: name(capacity: value, outlets: [name(location: value, max_release: value), ... ])
        '''
        s = f'{self.name}(capacity: {round(self.capacity, digits)}, outlets: ['
        for i in range(0, len(self.outlets)):
            if i < len(self.outlets) - 1:
                s += f'{self.outlets[i].print(digits)}, '
            else:
                s += f'{self.outlets[i].print(digits)}], '
        s += f'mapped variables: ['
        if self.maps == None:
            s+= f'None]'
        else:
            for i, (k, _) in enumerate(self.maps.items()):
                if i < len(self.maps) - 1:
                    s += f'{k}, '
                else:
                    s += f'{k}]'
        s += ')'
        return s
        
    @staticmethod
    def build_set_of_mapped_variables(names: typing.List[str], maps: typing.List[typing.Callable[[float], float]]) -> typing.Set[Map]:
        '''
        A helper function that can be used to generate a dictionary containing variable names and functions that mapping reservoir volume to those variables.
        '''
        if not len(names) == len(maps):
            raise AttributeError(f'{len(names)} names and {len(maps)} were provided. The dictionary cannot be created without a one-to-one relationship between names and mapping functions.')
        else:
            s = {}
            for i in len(names):
                s.append(Map(names[i], maps[i]))
            return s