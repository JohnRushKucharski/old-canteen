from __future__ import annotations
#region Header
# %% [markdown]
# # Utilities
# This file contains utilities functions of the canteen project, mostly in the form of unit conversions.
#
# Author: John Kucharski | Date: 05 May 2021
#
# Status: not done
# Testing: partial

# %% [markdown]
# ## Todo:
#

# %% [markdown]
# ## Dependencies 
# %%
import typing

import datetime
import calendar
import dataclasses

import numpy as np
#endregion

#region Conversions
#region time
# %% [markdown]
# ## water year
# %%
def doy_to_dowy(julian_day: int, is_leap_year: bool = False) -> int:
    '''
    Converts a julian day to the day of the water year.
    
    Args:
        julian_day [int]: the julian day to be converted.
        is_leap_year [bool]: True if the julian day is from a water year, False otherwise.
        
    Returns:
        An integer day of the water year.
    '''
    if is_leap_year:
        oct_01: int = 275
    else:
        oct_01: int = 274
    
    if julian_day < oct_01:
        dowy = julian_day + 92
    else:
        dowy = julian_day - (oct_01 - 1)
    return dowy
def datetime_to_dowy(datetimeobj: datetime.datetime) -> int:
    doy = datetimeobj.timetuple().tm_yday
    leapyear = calendar.isleap(datetimeobj.year)
    return doy_to_dowy(doy, leapyear)       

# %%[markdown]
# ## days
def days_to_hrs(x: float) -> float:
    '''
    Calculates the number of hours in x days
    
    Args:
        days (float): number of days
        
    Returns:
        number of hours (float)
    '''
    return x * 24
def days_to_sec(x:float) -> float:
    '''
    Calculates the number of seconds in x days
    
    Args:
        x (float): number of days
        
    Returns:
        number of seconds (float)
    '''
    return x * days_to_hrs(1) * hrs_to_sec(1)

# %%[markdown]
# ## hours
def hrs_to_days(x:float) -> float:
    '''
    Calculates the number of days in x hours
    
    Args:
        hrs (float): number of hours
        
    Returns:
        number of days (float)
    '''
    return x / 24
def hrs_to_min(x: float) -> float:
    '''
    Calculates the number of minutes in x hours
    
    Args:
        x (float): number of hours
        
    Returns:
        number of minutes (float)
    '''
    return x * 60
def hrs_to_sec(x: float) -> float:
    '''
    Calculates the number of seconds in x hours
    
    Args:
        x (float): number of hours
        
    Returns:
        number of seconds (float) in x hours
    '''
    return x * hrs_to_min(1) * min_to_sec(1) 

# %%[markdown]
# ## minutes
def min_to_hrs(x: float) -> float:
    '''
    Calculates the number of days in x minutes
    
    Args:
        x (float): number of minutes
        
    Returns:
        number of hours (float)
    '''
    return x / 60
def min_to_sec(x: float) -> float:
    '''
    Calculates the number of seconds in x minutes
    
    Args:
        x (float): number of minutes
    
    Returns:
        number of seconds (float)
    '''
    return x * 60

# %%[markdown]
# ## seconds
def sec_to_days(x: float) -> float:
    '''
    Calculates the number of days in x seconds
    
    Args:
        x (float): number of seconds
        
    Returns:
        number of days (float)
    '''
    return x * sec_to_min(1) * min_to_hrs(1) * hrs_to_days(1)
def sec_to_hrs(x: float) -> float:
    '''
    Calculates the number of hours in x seconds
    
    Args:
        x (float): number of seconds
        
    Returns:
        number of hours (float) in x seconds
    '''
    return x * sec_to_min(1) * min_to_hrs(1)
def sec_to_min(x: float) -> float:
    '''
    Calculates the number of minutes in x seconds
    
    Args:
        x (float): number of seconds
        
    Returns:
        number of minutes (float)
    '''
    return x / 60
#endregion

#region displacement
# %%[markdown]
# ## length conversions
def ft_to_m(x: float) -> float:
    '''
    Converts feet to meters
    
    Args:
        x (float): length in feet
    
    Returns:
        length (float) in meters
    '''
    return x / 3.281
def m_to_ft(x: float) -> float:
    '''
    Converts feet to meters
    
    Args:
        x (float): length in meters
    
    Returns:
        length (float) in feet
    '''
    return x * 3.281

# %%[markdown]
# ## area conversions
def km2_to_m2(km2: float) -> float:
    '''
    Converts square km to square m
    
    Args:
        km2 (float): kilometers
        
    Returns:
        square meters (float)
    '''
    return km2 * 1000000
def m2_to_km2(m2: float) -> float:
    '''
    Converts square meters to kms
    
    Args:
        m2 (float): meters
    
    Returns:
        square kilometers (float)
    '''
    return m2 / 1000000

# %%[markdown]
# ## volume conversions
def taf_to_af(x: float) -> float:
    '''
    Converts thousands of acre feet to acre feet
    
    Args:
        x (float): volume in thousands of acre feet
    
    Return:
        volume (float) in acre feet
    '''
    return x * 1000
def af_to_taf(x: float) -> float:
    '''
    Converts acre feet to thousands of acre feet
    
    Args:
        x (float): volume in acre feet
        
    Return:
        volume (float) in thousands of acre feet
    '''
    return x / 1000
def af_to_cf(x: float) -> float:
    '''
    Converts acre feet to cubic feet
    
    Args:
        x (float): volumne in acre feet
    
    Returns
        volume (float) in cubic feet
    '''
    return x * 43560
def cf_to_af(x: float) -> float:
    '''
    Converts cubic feet to acre feet
    
    Args:
        x (float): volume in cubic feet
    
    Returns
        volume (float) in acre feet
    '''
    return x / 43560
def cf_to_cm(x: float) -> float:
    '''
    Convers cubic feet to cubic meters
    
    Args:
        x (float): volume in cubic feet
        
    Returns:
        volume (float) in cubic meters
    '''
    return x / 35.3147
def cm_to_cf(x: float) -> float:
    '''
    Converts cubic meters to cubic feet
    
    Arg:
        x (float): volume in cubic meters
        
    Returns:
        volume (float) in cubic feet
    '''
    return x * 35.3147
def taf_to_cm(x: float) -> float:
    '''
    Converts thousands of acre feet to cubic meters
    
    Args:
        x (float): volume in thousands of acre feet
   
    Returns:
        volume (float) in cubic meters
    '''
    #af: float = taf_to_af(x)
    #cf: float = af_to_cf(af)
    #cm: float = cf_to_cm(cf)
    return cf_to_cm(af_to_cf(taf_to_af(x)))
def cm_to_taf(x: float) -> float:
    '''
    Converts cubic meters to thousans of acre feet
    
    Args:
        x (float): volume in cubic meters
    
    Returns:
        volume (float) in thousands of acre feet
    '''
    #cf: float = cm_to_cf(x)
    #af: float = cf_to_af(cf)
    #taf: float = af_to_taf(af)
    return af_to_taf(cf_to_af(cm_to_cf(x)))
#endregion

#region energy
# %%[markdown]
# ## temperature
def celsius_to_kelvin(celsius: float):
    '''
    Converts celsius to kelvin
    
    Args:
        celsius (float): temperature in celcius
    
    Returns:
        temperature (float) in kelvin
    '''
    return celsius + 273.15
def joules_to_celcius(heat: float, volume: float) -> float:
    '''
    Converts heat in joules to water temperature in celsius
    
    Args:
        heat (float): in joules
        volume (float): in cubic meters
        
    Returns:
        water temperature (float) in celcius
    '''
    density: float = 998.2
    specific_heat: float = 4182
    return heat / (density * specific_heat * volume) # Chapra 30.2
#endregion
#endregion

#region Closures
# %%[markdown]
# ## Closures
def f_close_on_domain(f: typing.Callable[[float], float], min: float, max: float) -> typing.Callable[[float], float]: 
    def inner(x: float) -> float:
        is_valid, _ = is_on_range(x, min, max)
        if is_valid:
            return f(x)
        else:
            return np.nan
    return inner
def f_close_on_range(f: typing.Callable[[float], float], min: float, max: float) -> typing.Callable[[float], float]:
    def inner(x: float):
        is_valid, _ = is_on_range(f(x), min, max)
        if is_valid:
            return f(x)
        else:
            return np.nan
    return inner  
def f_set_min_and_min(f: typing.Callable[[float], float], min: float = -np.inf, max: float = np.inf) -> typing.Callable[[float], float]:
    def inner(x: float):
        y = f(x)
        if y < min or np.isnan(y):
            return min
        if y > max or np.isnan(y):
            return max
        else:
            return y
    return inner   
def f_interpolate_from_data(xs: typing.List[float], ys: typing.List[float], interpolation: typing.Callable[[float, typing.List[float], typing.List[float]], float] = np.interp, extrapolate_lo: float = None, extrapolate_hi: float = None) -> typing.Callable[[float], float]: 
    def inner(x: float) -> float:
        on_range, _ = is_on_range(x, xs[0], xs[len(xs) - 1])
        if on_range:
            return interpolation(x, xs, ys)
        else:
            if x < xs[0]:
                return extrapolate_lo if extrapolate_lo != None else np.nan
            else: # since its not on range it must be x > x[1]
                return extrapolate_hi if extrapolate_hi != None else np.nan
    return inner    
#endregion
 
#region Validation   
# %% [markdown]
# ## Validation
# %%
def is_on_range(x: float, min: float, max: float, input_name: str = '', method_name: str = '') -> typing.Tuple[bool, typing.Union[InputOutOfRangeError, None]]:
    if min <= x <= max:
        return (True, None)
    else:
        return (False, InputOutOfRangeError(x, (min, max), input_name, method_name))         
def append_validation(lst: typing.List[str], valid: typing.Tuple[bool, str]) -> typing.List[str]:
    is_valid, msg = valid[0], valid[1]
    if is_valid:
        return lst
    else:
        lst = lst.append(msg)
        return lst

class ImpossibleError(Exception):
    def __init__(self, calling_method: str = ''):
        self.calling_method = calling_method
        msg = '' if not calling_method else f' in the {calling_method} method'
        self.message = f'The program reached an unexpected location{msg}, the resulted in an error.'
        super().__init__('The program should have never reached this location.')

class InputOutOfRangeError(Exception):
    def __init__(self, input, valid_range, input_name, calling_method):
        self.input: typing.Union[int, float] = input
        self.valid_range: typing.Tuple[float, float] = valid_range
        self.input_name: str = input_name
        self.calling_method: str = calling_method
        name_of_input = input_name if not input_name else f'{input_name} '
        method_name = calling_method if not calling_method else f'of the {calling_method} method '
        self.message = f'The {name_of_input}input value: {input}, {method_name}is not on the valid range: [{valid_range[0]}, {valid_range[1]}].'
        super().__init__('')


#endregion