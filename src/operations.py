import abc
import sys
import typing
import dataclasses

import datetime

import numpy as np

sys.path.insert(0, '/Users/johnkucharski/Documents/source/canteen')
import src.outlet as outlet
import src.reservoir as reservoir
import src.utilities as utilities


#region Operations (Reservoir Volume) Targets 
class Rule_Curve:
    '''
    This class is used to define target volumes for reservoirs based on the day of the water year.
    '''
    def __init__(self, dowy_volume_pairs: typing.List[typing.Tuple[int, float]], leap_year: bool = False, 
                 interpolator: typing.Callable[[typing.List[float], typing.List[float]], typing.List[float]] = np.interp) -> None:
        '''Initializes the Rule_Curve class 
        Args:
            dowy_volume_pairs (List[Tuple[int, float]]): list of paired (day of water year: int, target volume: float) rules.
            leap_year (bool, optional): True if the water year contains a leap day, False otherwise. Defaults to False.
            interpolator (Callable[[List[float], [List[float]], List[float]]): a function for intepolating between target volumes in the list of dowy_volume_pairs. Defaults to numpy.interp.
        Returns:
            None (instantiates an instance of the Rule_Curve class) 
        '''
        dowy_volume_pairs.sort(key = lambda x: x[0])
        self._end_of_water_year = 366 if leap_year else 365
        self._days = [i for i, _ in dowy_volume_pairs]
        self._targets = [j for _, j in dowy_volume_pairs]
        self._interpolator = interpolator
        self._rules = dowy_volume_pairs
        self._is_valid, self._messages = self.__validate_rules()
    
    def __validate_rules(self) -> typing.Tuple[bool, typing.List[str]]:
        is_valid, errors = True, []
        for i in range(len(self.rules)):
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
    def rules(self) -> typing.List[typing.Tuple[int, float]]:
        '''Returns the Rule_Curve.rules attribute containing a List of day of water year, target volume pairs.'''
        return self._rules
    @property
    def days(self) -> typing.List[int]:
        '''Returns the days of the water year contained in the rules attributes.'''
        return self._days
    @property
    def targets(self) -> typing.List[float]:
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
            n = len(self.rules)
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
    
    @staticmethod    
    def convert_datetime_to_day_of_wy_rule_curve_tuples(rules: typing.List[typing.Tuple[datetime.datetime, float]]) -> typing.List[typing.Tuple[int, float]]:
        '''Assists in the creation of rule curves by converting lists of datetime, target volume pairs to day of water year, target volume pairs
        Args: 
            rules (List[datetime, float]): datetime, target volume pairs.
        Returns:
            (List[int, float]): day of water year, target volume pairs.
        '''
        return [(utilities.datetime_to_dowy(item[0]), item[1]) for item in rules].sort(key = lambda x: x[0])
#endregion

#region Release Rules 


# class set_target_release:
#     '''
#     Provides static methods for constraining the release (to incorporate hedging rules, maximum safe flood releases, etc.) based the current and targeted volume.
#     '''
#     @staticmethod
#     def add_max_and_min_rules(volume: float, target_volume: float, max: float = np.inf, min: float = 0):
#         release: float = volume - target_volume if (volume - target_volume) < max else max
#         return release if release > min else min

# class set_release:
#     @staticmethod
#     def standard_operating_proceedure(res: reservoir.Reservoir, volume: float, demand: float = np.inf) -> typing.Dict[str, float]:
#         releases = {}
#         volume_released: float = 0
#         target_release: float = demand if volume - demand <= res.capacity else volume - res.capacity
#         for i in range(0, len(res.outlets)):
#             if volume_released < target_release and res.outlets[i].location < volume:
#                 release = min(target_release - volume_released, res.outlets[i].max_release(volume))
#                 releases[res.outlets[i].name] = release
#                 volume_released += release
#                 volume -= release
#             else:
#                 releases[res.outlets[i].name] = 0
#         return releases    

#class Builder(abc.ABC):
    #def add_rule_curve(self, date_volume: Tuple[datetime, float])
    #def add_forecast(self, forecast)
    #def add_objective(self, objective)
    #def add_objectives(self, List-objective)

# @dataclasses.dataclass
# class Rules:
#     rules: typing.List[typing.Callable] = []

# class Operations:
#     def __init__(self, rules: typing.List[typing.Callable] = [], releases: typing.List[typing.Callable] = []):
#         self._rules = rules
    
#     @staticmethod
#     def add_rule(fx: typing.Callable, description: str) -> None:
        
# class Operations:
#     def __init__(self, target_fx, release_fx, outlets: typing.List[outlet.Outlet]) -> None:
#         self._f_target = target_fx
#         self._f_release = release_fx
#         self._outlets = outlets
    
     
          
    

    

        
                 
# def validate_rule_curve(dowy: int, last_dowy: int,
#                         rules: typing.List[typing.Tuple[int, float]],
#                         interpolators: typing.List[typing.Callable[[typing.List[float], typing.List[float]], typing.List[float]]]) -> typing.Tuple[bool, str]:
#     msgs: str = ''
#     msgs += utilities.is_on_range(dowy, 1, last_dowy, 'day of water year (dowy)')[1]
#     for rule in rules:
#         msgs += utilities.is_on_range(rule[0], 1, last_dowy, 'rule day of water year')[1]
#     return len(msgs) == 0, msgs
    



