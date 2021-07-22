import sys
import typing
import datetime

import pandas as pd

sys.path.insert(0, '/Users/johnkucharski/Documents/source/canteen')
import src.reservoir as reservoir
import src.operations as operations

class Input:
    def __init__(self, date: datetime, volume: float, maps: typing.Dict[str, float] = None):
        self._volume = volume
        self._date = date
        self._maps = maps
        
    @property
    def date(self):
        return self._date
    @property
    def volume(self):
        return self._volume
    @property
    def maps(self):
        return self._maps
   
    @staticmethod
    def create_inputs(volumes: typing.List[float], dates: typing.List[float] = None, timedelta: datetime.timedelta = None, maps: typing.List[typing.Dict[str, float]] = None):
        inputs: typing.List[Input] = []
        create_dates: bool = True if dates == None else False 
        timedelta = timedelta if timedelta != None else datetime.timedelta(days = 1)
        for i in range(0, len(volumes)):
            _map = None if maps == None else maps[i]
            _date = datetime.datetime(datetime.MINYEAR, 1, 1) + timedelta * i if create_dates else dates[i] 
            inputs.append(Input(_date, volumes[i], _map))
        return inputs
                      
def simulate(inputs: typing.List[Input], s_init: float = 0, 
             res: reservoir.Reservoir = reservoir.Reservoir(), 
             ops: typing.Callable[[reservoir.Reservoir, float, float], typing.Dict[str, float]] = operations.set_release.standard_operating_proceedure) -> pd.DataFrame:
    vol: float = s_init
    for i in range(0, len(inputs)):
        # have to calculate demand - but how in a flexible manner?
        releases = ops(res, vol, )
