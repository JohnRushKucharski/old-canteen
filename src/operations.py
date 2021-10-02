import abc
import sys
import enum
import typing
import dataclasses

import datetime

import numpy as np

sys.path.insert(0, '/Users/johnkucharski/Documents/source/canteen')
import src.data as data
import src.outlet as outlet
import src.reservoir as reservoir
import src.utilities as utilities

#region Operational Zones
class Zone(enum.Enum):
    INACTIVE = 0
    CONSERVATION = 1
    FLOOD = 2
    SURCHARGE = 3
    TOP_OF_DAM = 4

#region Operations (Reservoir Volume) Targets 
class Rule_Curve:
    '''
    This class is used to define target volumes for reservoirs based on the day of the water year.
    '''
    def __init__(self, date_target_pairs: typing.List[typing.Tuple[datetime.date, float]], leap_year: bool = False, 
                 interpolator: typing.Callable[[typing.List[float], typing.List[float]], typing.List[float]] = np.interp) -> None:
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
    
    def __validate_rules(self) -> typing.Tuple[bool, typing.List[str]]:
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
    def date_target_pairs(self) -> typing.List[typing.Tuple[datetime.datetime, float]]:
        '''Returns datetime, target volume pairs.'''
        return self._date_target_pairs       
    @property
    def day_of_water_year_target_pairs(self) -> typing.List[typing.Tuple[int, float]]:
        '''Returns day of water year, target volume pairs.'''
        return self._day_of_water_year_target_pairs
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
#endregion

#region Operations   
class Operations(abc.ABC):
    def __init__(self, rules: typing.List[typing.Callable[[data.Input], float]]):
        self._rules = rules
   
    @abc.abstractproperty
    def rules(self):
        return self._rules
    
    @abc.abstractmethod
    def operate(self, input: data.Input, outlets: typing.List[outlet.Outlet]) -> typing.Dict[str, float]: 
        pass  
    
    def __update_releases(previous: float, new: typing.Dict[str, float]) -> float:
        return previous + sum(new.values())    
#endregion

def passive_operations(input: data.Input, outlets: typing.List[outlet.Outlet]) -> typing.Dict[str, float]:
    releases = {}
    outlets.sort(key=lambda x: x.location)
    s, r = input.storage + input.inflow, 0
    for x in outlets:
        r += x.max_release(s)
        releases[x.name] = r
        s -= r
    return releases
        



# #region Wilson Example
# def surcharge_release(input: input.Input):
#     pass 
# def minimum_release(input: input.Input) -> float:
#     yr: int = input.date.year
#     # date between 1 Jan - 1 Apr
#     if input.date < datetime.datetime(yr, 4, 1):
#         return 5
#     # date between 1 Apr - 1 Oct
#     elif input.date < datetime.datetime(yr, 10, 1): 
#         return 15
#     # date between 1 Oct - 1 Jan (redundant but matches Excel example)
#     else:
#         return 5
# def epks_release(input: input.Input) -> float:
#     ratio: float = input.additional_inputs['epks']
#     isvalid, exception = utilities.is_on_range(ratio, 1, 4, 'Input.additional_inputs[epks]', 'epks_release()')
#     if isvalid:
#         if ratio < 2:
#             return 11000
#         elif ratio < 3:
#             return 18000
#         else: #ratio < 4
#             return 25000        
#     else:
#         raise exception
# def nwck_release(input: input.Input) -> float:
#     ratio: float = input.additional_inputs['nwck']
#     isvalid, exception = utilities.is_on_range(ratio, 1, 4, 'Input.additional_inputs[nwck]', 'nwck_release()')
#     if isvalid:
#         if ratio < 2:
#             return 6000
#         elif ratio < 3:
#             return 10000
#         else: #ratio < 4
#             return 12000        
#     else:
#         raise exception
# def tstk_release(input: input.Input) -> float:
#     ratio: float = input.additional_inputs['tstk']
#     isvalid, exception = utilities.is_on_range(ratio, 1, 4, 'Input.additional_inputs[tstk]', 'tstk_release()')
#     if isvalid:
#         if ratio < 2:
#             return 2600
#         elif ratio < 3:
#             return 4300
#         else: #ratio < 4
#             return 4700        
#     else:
#         raise exception
# def wiln_release(input: input.Input) -> float:
#     ratio: float = input.additional_inputs['tstk']
#     isvalid, exception = utilities.is_on_range(ratio, 1, 4, 'Input.additional_inputs[tstk]', 'tstk_release()')
#     if isvalid:
#         if ratio < 1.3:
#             return 15
#         elif ratio < 2:
#             return 1200
#         elif ratio < 3:
#             return 1600
#         else: #ratio < 4
#             return 2250
#     else:
#         raise exception
    
# rule_1 = minimum_release
# rule_2 = epks_release
# rule_3 = nwck_release
# rule_4 = tstk_release
# rule_5 = wiln_release
# rules = [rule_1, rule_2, rule_3, rule_4, rule_5]
    
# class Wilson_Operations(Operations):
#     def __init__(self, 
#                  rules: typing.List[typing.Callable[[input.Input, typing.List[outlet.Outlet]], typing.Dict[str, float]]],
#                  active_zone: typing.Callable[[float], Zone])  -> None:
#         self.active_zone = active_zone
#         super().__init__(rules)
#     def operate(self, input: input.Input, res: reservoir.Reservoir) -> float:
        
#         return max(rule_1[input], rule_2(input), rule_3(input), rule_4(input), rule_5(input))
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
    



