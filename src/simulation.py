#region Simulation
# %% [markdown]
# # Simulation
# This file provides a data container for stuctures used to make releases from reservoirs.
#
# Author: John Kucharski | Date: 06 July 2021
# 
# Status: open to extension, closed to change [s*O*lid] :)
# Testing: not done

# TODO: #13 Store simulation results.
#endregion

#region Dependencies
from ast import Call, Or
import sys
import copy
from dataclasses import dataclass
from typing import List, Dict, Tuple, Callable, Union

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, '/Users/johnkucharski/Documents/source/canteen')
from src.data import Category, RunOrder, Input, TimeStep, TimeSeries
from src.outlet import Outlet
from src.reservoir import Reservoir

import src.operations as operations
import src.utilities as utilities
#endregion 
                       
#%%
# class Run_Order(Enum):
#     '''
#     Describes the order in which an Additional_Output should be run.
#     '''
#     BEFORE_OPERATIONS = 0,
#     BEFORE_STORAGE = 1,
#     AFTER_STORAGE = 2

# class Additional_Output:
#     '''
#     Provides an ability to inject simulations with other output models.
#     '''
#     def __init__(self, fn: Callable[[Input], Dict[str, Any]], is_outflow: bool = False, run_order: Run_Order = Run_Order.AFTER_STORAGE):
#         self._fn = fn
#         self._is_outflow = is_outflow
#         if is_outflow and run_order == Run_Order.AFTER_STORAGE: raise ValueError(f'The output is marked as an outflow. It must be run before storage calculations performed but is set to run after storage calculations.')
#         else: self._run_order = run_order
#     @property
#     def run_order(self) -> Run_Order:
#         return self._run_order
#     @property
#     def is_outflow(self) -> bool:
#         return self._is_outflow
    
#     def run(self, input: Input) -> Any:
#         return self._fn(input)    
class Simulation(object):
    '''
    A simulation container holds the input needed for a simulation. 
    '''
    def __init__(self, timeseries: TimeSeries, reservoir = Reservoir(), operations = Callable[[TimeStep, List[Outlet]], Dict[str, float]]):
        self._reservoir: Reservoir = reservoir
        self._timeseries: TimeSeries = timeseries
        self._operations: Callable[[Dict[str, Input], List[Outlet]], Dict[str, float]] = operations
        #self.result: Union[TimeSeries, None] = None
    @property    
    def reservoir(self):
        return self._reservoir
    @property
    def timeseries(self):
        return self._timeseries
    # @property
    # def result(self):
    #     return self._result if self._result != None else 'No simulation results to display'
    # @result.setter
    # def result(self, result: Union[TimeSeries, None]):
    #     self._result = result
    def operate(self, ts: TimeStep) -> TimeStep:
        return ts.addinputs({k: Input(value=v, category=Category.OUTFLOW, isoutput=True) for k, v in self._operations(ts, self.reservoir.outlets).items()})
    def update_storage(self, ts: TimeStep) -> Input:
        '''Computes storage and returns it as an input for the simulate function to incorporate into the next timestep in the timeseries.'''
        return {self.timeseries.storage_key: Input(value=ts.inflows() + ts.storage() - ts.outflows(), category=Category.STORAGE, isoutput=True)}
    # def _run_timestep(self, ts: TimeStep) -> Tuple[TimeStep, Dict[str, Input]]:
    #     '''Mutates the current timestep and returns inputs for the simulate function to incorporate into the next timestep in the timeseries.'''
    #     if ts.outputs:
    #         isbeforeoperations = True
    #         for v in ts.outputs.values():
    #             if v.runorder == RunOrder.POST_OPERATIONS and isbeforeoperations:
    #                 ts = self._run_operations(ts)
    #                 isbeforeoperations = False
    #             ts.add_inputs(v.run(ts))
    #     else:
    #         ts = self._run_operations(ts)
    #     return ts
    def simulate(self) -> TimeSeries:
        ts: List[TimeStep] = []
        newinputs: Dict[str, Input] = {}
        for t in range(len(self.timeseries.timesteps)):
            ts.append(self.timeseries.timesteps[t] if t == 0 else self.timeseries.timesteps[t].addinputs(newinputs))
            ts, newinputs = self._stepforward(ts, t, newinputs)
        return TimeSeries(ts)    
        #     if ts[t].outputs: # then there are outputs to compute
        #         ispreops = True
        #         for output in ts[t].outputs.values():
        #             if output.runorder == RunOrder.PRE_OPERATIONS: 
        #                 ts[t] = ts[t].addinputs(output.run(ts, t))
        #             if output.runorder == RunOrder.POST_OPERATIONS:
        #                 if ispreops: # then operate
        #                     ts[t] = self.operate(ts[t])
        #                     ispreops = False
        #                 newinputs = newinputs | output.run(ts, t)
        #     else: # only operate
        #         ts[t] = self.operate(ts[t])
        #     newinputs = newinputs | self.update_storage(ts[t])
        # return TimeSeries(ts)
    def _stepforward(self, ts: List[TimeStep], t: int, newinput: Dict[str, Input], factor: float = 1) -> Tuple[List[TimeStep], Dict[str, Input]]:
        if ts[t].outputs: # then there are outputs to compute
            ispreops = True
            for output in ts[t].outputs.values():
                if output.runorder == RunOrder.PRE_OPERATIONS: 
                    ts[t] = ts[t].addinputs(output.run(ts, t))
                if output.runorder == RunOrder.POST_OPERATIONS:
                    if ispreops: # then operate
                        ts[t] = self.operate(ts[t])
                        ispreops = False
                    newinputs = newinput | output.run(ts, t)
        else: # only operate
            ts[t] = self.operate(ts[t])
        newinputs = newinput | self.update_storage(ts[t])
        return ts, newinputs
                        
             
        
        
        
        # storage: Input
        # results: List[TimeStep] = []
        # #test trying to save access to past time step too...
        # for ts in range(len(self.timeseries.timesteps)):
        #     if ts == 0: t = self.timeseries.timesteps[ts]
        #     if t.ouputs: # i.e. outputs to be computed in ts
        #         preoperations = True
        #         for output in t.outputs.values():
        #             if output.runorder == RunOrder.PRE_OPERATIONS and preoperations:
        #                 t.add_inputs(output.run(t))
        #             else:
        #                 if preoperations: t = 
        # #end
            
        #     ts: TimeStep = self.timeseries.timesteps[t] if t == 0 else self.timeseries.timesteps[t].add_inputs({self.timeseries.storage_key: storage})
        #     ts = self._run_timestep(ts)
        #     results.append(ts)
        #     storage = self._compute_storage(ts, self.timeseries.storage_key)
        # self.result = TimeSeries(results)
        # return results

    

# class Simulation:
#     '''
#     A simulation contain that holds the inputs: List[Input], reservoir: Reservoir, and operate(): Callable[[Input, List[Outlet], Dict[str, float]] required to run a simualtion.
#     The simulate() function runs the simulation.
#     '''
#     def __init__(self, data: List[Data],
#                  reservoir: Reservoir = Reservoir(),
#                  operations_fn: Callable[[Data, List[Outlet]], Dict[str, float]] = operations.passive_operations):
#                 #additional_outputs: Dict[str, Additional_Output] = {}
#         self._data = data
#         self._reservoir = reservoir
#         self._f_operations = operations_fn
#         #self._additional_ouputs = additional_outputs
           
#     @property
#     def data(self) -> List[Data]:
#         return self._data
#     @property
#     def reservoir(self) -> Reservoir:
#         return self._reservoir
#     # @property
#     # def additional_outputs(self) -> Dict[str, Additional_Output]:
#     #     return self._additional_ouputs
    
#     def operations(self, data: Data, outlets: List[Outlet], factor: float = 1) -> Dict[str, float]:
#         '''
#         Calls the operations_fn stored as a class attribute.
#         '''
#         return self._f_operations(data, outlets, factor)
    
#     def simulate(self) -> Dict[str, List[Any]]:
#         '''
#         Runs a simulation, using the class attribute: inputs, reservoir, operations_fn, and additional_outputs.
        
#         Returns:
#             A Dict[str, List[Any]]: containing the simulation inputs and outputs.
#         '''
#         outputs = {}
#         for t in range(len(self.data)):
#             outputs.update({ k: outputs[k] + [v] if k in outputs else [v] for k, v in self.step_foward(t).items()})
#         return outputs

#     def step_foward(self, t: int, factor: float = 1) -> Dict[str, Any]:
#         '''
#         Executes a single timestep in the simulation, is called by the simulate() function.
        
#         Args:
#             t [int]: the simulation timestep
#             factor [float]: needs to be edited, allows for optimizaiton at the moment.
#         '''
#         #TODO: #12 Remove optimization 'factor's from simulation and operations logic.
#         # hasoperated: bool = False
#         # input, torun = self.sortIO(self.data[t].variables)
#         # for k, v in torun.items():
#         #     if v.runorder == RunOrder.PRE_OPERATIONS:
#         #         v.run()
        
#         outflow: Dict[str, float] = self.add_outflows(self.inputs[t]) #input
#         release: Dict[str, float] = self.operations(self.inputs[t], self.reservoir.outlets, factor)
#         release['total_release'] = sum(release.values())
#         outflow.update(release)
#         outflow = self.add_outflows(self.inputs[t], outflow, Run_Order.BEFORE_STORAGE)
#         if t + 1 < len(self.inputs) and self.inputs[t + 1].update_storage:
#             self.inputs[t + 1].storage = self.inputs[t].storage + self.inputs[t].inflow - outflow['total_release']        
#         output = self.add_outputs(self.inputs[t], outflow) if self.additional_outputs else outflow
#         return self.inputs[t].to_dict() | output 
                
        
     
#     def add_outflows(self, data: Data, outflow: Dict[str, float] = {}) -> Dict[str, float]: 
        
            
        
#         for k, v in self.additional_outputs.items():
#             if v.run_order == run_order and v.is_outflow: outflow.update({f'{k}_{label}': val for label, val in v.run(input).items()}) #outflow[k] = v.run(input)
#         return outflow
        
#     def add_outputs(self, input: Input, output: Dict[str, Any] = {}):
#         for k, v in self.additional_outputs.items():
#             if not v.is_outflow: output.update({f'{k}_{label}': val for label, val in v.run(input).items()}) #output[k] = v.run(input)
#         return output                 
            
#     def inputs_to_dict(self):
#         '''
#         Converts the simulation inputs (class attribute) to a dictionary.
#         '''    
#         d = { k: np.full(len(self.inputs), np.nan).tolist() for k, _ in self.inputs[0].to_dict().items()}
#         for i in range(0, len(self.inputs)):
#             for k, v in self.inputs[i].to_dict().items():
#                 if k in d:
#                     d[k][i] = v
#                 else:
#                     l = np.full(len(self.inputs), np.nan).tolist()
#                     l[i] = v
#                     d[k] = l
#         return d
#     def simulate_to_dataframe(self) -> pd.DataFrame:
#         '''
#         Calls the simulate() function but returns the output as a DataFrame instead of a dictionary.
#         '''
#         outputs = self.simulate()
#         df = pd.DataFrame.from_dict(outputs)
#         df.set_index(pd.to_datetime(df.date), inplace = True)
#         df.drop(columns=['date'], inplace = True)
#         return df
    
#     def plot(self, df: pd.DataFrame):
#         fig, ax = plt.subplots(nrows = 2, ncols=1, sharex=True, sharey=True, figsize=(10, 5))
#         plt.suptitle('Simulation Summary Ouputs')
#         ax[0].set_title('inflows and storage')
#         ax[0].set_ylabel('volume')
#         ax[0].step(df.index, df.inflow, where='post', color='cornflowerblue', linestyle='dashed', label='inflow')
#         ax[0].step(df.index, df.storage, where='post', color='blue', linestyle='solid', label='storage')
#         ax[1].set_title('outflows')
#         ax[1].set_xlabel('date')
#         ax[1].set_ylabel('volume')
#         ax[1].step(df.index, df.total_release, where='post', color='darkorchid', linestyle='solid', label='outflow')
#         fig.legend(frameon=False)
        