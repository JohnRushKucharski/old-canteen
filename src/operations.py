#region Header
# %% [markdown]
# # Reservoir
#
# Author: John Kucharski | Date: 28 June 2021
#
# Status: open
# Testing: partial

# testing todos listed on methods below.
#endregion

#region Dependencies
#%%
import sys
from enum import Enum
from typing import List, Dict, Tuple, Callable, Any, Protocol
from dataclasses import dataclass
from abc import ABC, abstractmethod

import datetime

import numpy as np

sys.path.insert(0, '/Users/johnkucharski/Documents/source/canteen')
from src.data import Input
from src.outlet import Outlet
import src.utilities as utilities
#endregion

#%%
class Zone(Enum):
    INACTIVE = 0
    CONSERVATION = 1
    FLOOD = 2
    SURCHARGE = 3
    TOP_OF_DAM = 4

class Operations(Protocol):
    '''
    Provides an interface for classes used to define reservoir operations.
    '''
    def operate(input: Input, outlets: List[Outlet]) -> Dict[str, float]:
        '''
        A function used to operate the reservoir, and required by Simulation objects.
        
        Args:
            Input [data.Input]: data inputs for a single timestep
            outlets [List[Outlet]]: outlets from which releases are made
            
        Returns:
            A Dict[str, float] with reservoir releases (values) labeled with the Outlet.name from which they are made (key).
        '''

class Rule_Curve:
    '''
    This class is used to define target volumes for reservoirs based on the day of the water year.
    '''
    def __init__(self, date_target_pairs: List[Tuple[datetime.date, float]], leap_year: bool = False, 
                 interpolator: Callable[[List[float], List[float]], List[float]] = np.interp) -> None:
        '''Initializes the Rule_Curve class 
        Args:
            date_target_pairs (List[Tuple[date, float]]): list of paired (dates, target volume: float) rules.
            leap_year (bool, optional): True if the water year contains a leap day, False otherwise. Defaults to False.
            interpolator (Callable[[List[float], [List[float]], List[float]]): a function for intepolating between target volumes in the list of dowy_volume_pairs. Defaults to numpy.interp.
        Returns:
            None (instantiates an instance of the Rule_Curve class) 
        '''
        self._interpolator = interpolator
        self._date_target_pairs = date_target_pairs
        self._end_of_water_year = 366 if leap_year else 365
        _targ = [j for _, j in date_target_pairs]
        _days = [utilities.datetime_to_dowy(i) for i, _ in date_target_pairs]
        day_of_water_year_target_pairs = [(_days[i], _targ[i]) for i in range(len(_days))]
        day_of_water_year_target_pairs.sort(key = lambda x: x[0])
        self._day_of_water_year_target_pairs = day_of_water_year_target_pairs
        self._days = [i for i, _ in self.day_of_water_year_target_pairs]
        self._targets = [ j for _, j in self.day_of_water_year_target_pairs]
        self._is_valid, self._messages = self.__validate_rules()
    
    def __validate_rules(self) -> Tuple[bool, List[str]]:
        is_valid, errors = True, []
        for i in range(len(self.day_of_water_year_target_pairs)):
            valid_day, error_day = utilities.is_on_range(self.days[i], 1, self.end_of_water_year, 'rule day_of_the_water_year', 'RuleCuve.__validate_rules()')
            valid_target, error_target = utilities.is_on_range(self.targets[i], 0, np.inf, 'rule target', 'RuleCurve.__validate_rules()')
            if not valid_day or not valid_target:
                is_valid = False
                i, msg = 1, f'The rule {self.rules[i]} contains the following errors: '
                if not valid_day:
                    msg += f'({i}) {error_day}'
                if not valid_target:
                    msg += f'({i}) {error_target}'
                errors.append(msg)
        return is_valid, errors
    
    @property
    def date_target_pairs(self) -> List[Tuple[datetime.datetime, float]]:
        '''Returns datetime, target volume pairs.'''
        return self._date_target_pairs       
    @property
    def day_of_water_year_target_pairs(self) -> List[Tuple[int, float]]:
        '''Returns day of water year, target volume pairs.'''
        return self._day_of_water_year_target_pairs
    @property
    def days(self) -> List[int]:
        '''Returns the days of the water year contained in the rules attributes.'''
        return self._days
    @property
    def targets(self) -> List[float]:
        '''Returns the target volumes containing in the rules attributes.'''
        return self._targets
    @property
    def end_of_water_year(self) -> int:
        '''The integer end of the water year value of 365 or 366.'''
        return self._end_of_water_year
    
    def target_volume(self, dowy: int) -> float:
        ''' Computes the target_volume for a given day of the water year. 
        Args:
            dowy (int): the day of the water year for which the target volume is computed.
        Returns:
            (float): A target volume.
        '''
        is_valid, error = utilities.is_on_range(dowy, 0, self.end_of_water_year)
        if not is_valid:
            raise error
        else:
            n = len(self.day_of_water_year_target_pairs)
            last_day, last_target = self.days[-1], self.targets[-1]
            first_day, first_target = self.days[0], self.targets[0]
            if dowy < first_day: # interpolate_from_previous_water_year
                dowy = self.end_of_water_year - last_day + dowy
                xs, ys = [0, self.end_of_water_year - last_day + first_day], [last_target, first_target]
            elif dowy > last_day: #interpolate_to_next_water_year
                dowy = dowy - last_day
                xs, ys = [0, self.end_of_water_year - last_day + first_day], [last_target, first_target]
            else: #interpolate between rules
                for i in range(n):           
                    if dowy == self.days[i]:
                        return self.targets[i]
                    if dowy < self.days[i]:
                        xs, ys = [self.days[i - 1], self.days[i]], [self.targets[i - 1], self.targets[i]]
                        break
            return self._interpolator(dowy, xs, ys)
    def operate(self, input: Input, outlets: List[Outlet]) -> Dict[str, float]:
        '''
        Makes release to achieve a target elevation based on the input storage and inflow, subject to constraints posed by the outlets.
        
        Args:
            input [Input]: data inputs used for operational rules
            outlets [List[Outlet]]: outlets from which releases are made.
        Returns:
            A Dict[str, float] with releases (values) labeled according the Outlet.name from which they are made.
        ''' 
        # TODO: #8 Test Rule_Cuve.operate() function
        releases = {}
        outlets.sort(key=lambda x: x.location)
        dowy: int = utilities.datetime_to_dowy(input.date)
        storage, release = input.storage + input.inflow, 0
        target_release: float = input.storage + input.inflow - self.target_volume(dowy) 
        for outlet in outlets:
            if target_release > 0 and storage > 0:
                release = min(target_release, outlet.max_release)
                releases[outlet.name] = release
                storage = storage - release
            else:
                releases[outlet.name] = 0
        return releases

@dataclass
class Rules(ABC):
    '''
    A Operations class that holds a set of rules with the same signature as the operate function.
    '''
    def __init__(self, rules: List[Callable[[Input, Outlet], Dict[str, float]]]):
        self._rules = rules
    
    @property
    def rules(self) -> List[Callable[[Input, Outlet], Dict[str, float]]]:
        return self._rules
    @rules.setter
    def rules(self, rule: Callable[[Input, Outlet], Dict[str, float]]) -> None:
        self._rules.append(rule)        
    
    @abstractmethod
    def operate(self, input: Input, outlets: List[Outlet]) -> Dict[str, float]:
        pass
                
def passive_operations(input: Input, outlets: List[Outlet], factor: float = 1) -> Dict[str, float]:
    '''
    An operations policy that makes the maximum possible release given the storage, inflows (from the input argument) given contraints posed by the outlets.
    
    Args: 
        input [Input]: data inputs for the operations.
        outlets [List[Outlet]]: a list of reservoir outlets from which releases are made.
    Return:
        A Dict[str, float] releases (values) listed according to the Outlet.name (key) from which they are made.
    '''
    releases = {}
    outlets.sort(key=lambda x: x.location)
    stored, released = input.storage + input.inflow, 0
    for outlet in outlets:
        released += outlet.max_release(stored)
        releases[outlet.name] = released
        stored = stored - released
    return releases
        
def standard_operating_proceedures(input: Input, outlets: List[Outlet]) -> Dict[str, float]:
    '''
    Implements standard operationg proceedure reservoir operations rules, meaning the demanded water is released, provided it is available as storage + inflow.
    NOTE: requires demand and reservoir capacity be listed in the inputs argument as input.additional_inputs under the keys: ['demand', 'capacity']
    
    Args:
        input [Input]: data inputs for the operational rules. MUST include the input.additional_inputs: ['demand', 'capacity'].
        outlets [List[Outlet]]: a list of outlets from which releases are made.
    Returns:
        A Dict[str, float]: listing releases (values) according to the Outlet.name (key) from which they are made.
    '''
    # TODO: #9 Test standard_operating_proceedures() function
    releases = {}
    stored, release = input.storage, 0
    demand, capacity = input.additional_inputs['demand'], input.additional_inputs['capacity']
    target = max(demand, stored - capacity) if capacity < stored else min(stored, demand)
    outlets.sort(key=lambda x: x.location)
    for outlet in outlets:
        if target > 0:
            release = min(demand, outlet.max_release(stored))
            releases[outlet.name] = release
            stored = stored - release
        else:
            releases[outlet.name] = release
    return releases           