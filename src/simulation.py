import sys
import typing
import datetime

import numpy as np
import pandas as pd

sys.path.insert(0, '/Users/johnkucharski/Documents/source/canteen')
import src.data as data
import src.outlet as outlet
import src.reservoir as reservoir

import src.operations as operations
import src.utilities as utilities

                       
# def simulate(inputs: typing.List[inputs.Input], s_init: float = 0, 
#              res: reservoir.Reservoir = reservoir.Reservoir(), 
#              ops: typing.Callable[[reservoir.Reservoir, float, float], typing.Dict[str, float]] = operations.set_release.standard_operating_proceedure) -> pd.DataFrame:
#     vol: float = s_init
#     for i in range(0, len(inputs)):
#         # have to calculate demand - but how in a flexible manner?
#         releases = ops(res, vol, )

class Simulation:
    def __init__(self, inputs: typing.List[data.Input],
                 reservoir: reservoir.Reservoir = reservoir.Reservoir(),
                 ops: typing.Callable[[data.Input, typing.List[outlet.Outlet]], typing.Dict[str, float]] = operations.passive_operations):
        self._inputs = inputs
        self._reservoir = reservoir
        self._f_operations = ops
        
    @property
    def inputs(self) -> typing.List[data.Input]:
        return self._inputs
    @property
    def reservoir(self) -> reservoir.Reservoir:
        return self._reservoir
    # @property
    # def f_operations(self) -> typing.Callable[[data.Input, typing.List[outlet.Outlet]], typing.Dict[str, float]]:
    #     return self._f_operations
    
    def operations(self, input: data.Input, outlets: typing.List[outlet.Outlet]) -> typing.Dict[str, float]:
        return self._f_operations(input, outlets)
    
    def simulate(self) -> pd.DataFrame:
        n = len(self.inputs)
        outflows = []
        outflow: typing.Dict[str, typing.List[float]] = {}
        for i in range(n):
            release: typing.Dict[str, float] = self.operations(self.inputs[i], self.reservoir.outlets)
            outflow.update({ k: outflow[k] + [v] if k in outflow else [v] for k, v in release.items()})
            if not i + 1 == n:
                if self.inputs[i + 1].update_storage:
                    self.inputs[i + 1].storage = self.inputs[i].storage + self.inputs[i].inflow - sum(release.values())
            outflows.append(outflow)
        return outflows
            
             