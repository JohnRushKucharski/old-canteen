#region Header
# %% [markdown]
# # Input
#
# Author: John Kucharski | Date: 28 August 2021
#
# Status: open
# Testing: partial

#%%
#TODO: #2 Factories by making dispatch work (may need data structure for datetime.date, int)
#TODO: #3 Make it easier for outputs to be applied irregularly (e.g. every other time step, or once a month, etc.)
#endregion

#region Dependencies
#%%
import copy
import datetime
from enum import IntEnum
from dataclasses import dataclass
from typing import OrderedDict, Protocol, Union, Callable, List, Dict, Any
from multipledispatch import dispatch

import pandas as pd
import matplotlib.pyplot as plt

#%%
@dataclass
class Category(IntEnum):
    '''A enum describing if a variable is an inflow, outflow or neither.'''
    INFLOW = 0
    '''An inflow into the reservoir used to compute storage values.'''
    OUTFLOW = 1
    '''An output from the reservoir used to compute storage values.'''
    STORAGE = 2
    '''A storage value used in reservoir operations.'''
    OTHER = 3
    '''Any variable not listed above, e.g. inflow, outflow, storage.'''
class IVariable(Protocol):
    '''Interface for a variable in the data class'''
    isoutflow: bool
    '''True if the variable is a reservoir outflow, False otherwise.'''
    def value(self, *args) -> Any:
        '''Returns value of additional data parameter.'''   
    def print(self):
        '''Prints a string representation of the parameter.'''  
@dataclass
class Input:
    '''An immutable TimeStep input'''
    value: Any
    '''Usually a float value representing inflow, storage volume or some other value, but could be any input for instance: a string season name, integer year, or boolean describing a gate is broken.'''
    category: Category = Category.INFLOW
    '''Describes input as an inflow, outflow or neither, for the purposes of computing storage values and summation.'''
    isoutput: bool = False
    '''True if the value is computed from an Output variable, False otherwise.'''
    def print(self, verbose: bool = False) -> str:
        '''Returns a string representation of the input value.'''
        if verbose:
            return f'{self.value} [{self.category.name.lower()}{", output" if self.isoutput else ""}]'
        else:
            return f'{self.value}' 
@dataclass
class RunOrder(IntEnum):
    '''An enum for callable output extensions.'''
    PRE_OPERATIONS = 0
    '''Computes the output value before operations are applied.'''
    POST_OPERATIONS = 1
    '''Computes the output value after operations are applied.'''   
@dataclass
class Output:
    '''An immutable TimeStep output.'''
    fn: Callable[['TimeSeries', int], Dict[str, Any]]
    '''A function that accepts an input and produces a Dict[str, Any] suitable for converting into a Dict[str, Input]'''
    category: Category
    '''Labels the output as an inflow, outflow or neither for the purposes of computing storage and summation of results.'''
    runorder: RunOrder = RunOrder.PRE_OPERATIONS
    '''Defines if the value should be computed before or after operations in a Simulation()'''    
    def run(self, ts: 'TimeSeries', t: int) -> Dict[str, Input]:
        '''Runs the fn function the results are converted into a Dict[str, Input].'''
        return {k: Input(value=v, category=self.category, isoutput=True) for k, v in self.fn(ts, t).items()}
    def to_dict(self, key: str, values_list: bool = False, n: int = 1, t: int = 1, starting_position: int = 0) -> Dict[str, Union['Output', List['Ouput']]]:
        if values_list:
            return {key: self.to_list(n, t, starting_position)}
        else:
            return [{key: v} for v in self.to_list(n, t, starting_position)]
    def to_list(self, n: int, t: int = 1, starting_position: int = 0) -> List['Output']:
        '''
        Generates a list with n items, with the output duplicated every 't' timesteps starting at the specified timestep (None is added where the Output is not duplicated).
        Args:
            n [int]: the desired lenght of the output list.
            t [int]: the number of timesteps between duplications of the output.
            starting_position [int]: the first time period with the duplicated output.
        Returns:
            A List[Output] where the output is duplicated at specified regular intervals.
        Note: 
            The resulting list will contain intervals of None between intervals of the duplicated output.
        '''
        out = copy.deepcopy(self)
        return [out if i == starting_position or (i - starting_position) % t == 0 else None for i in range(n)]  
    def print(self) -> str:
        '''Returns a simple string describing when the output is computed.'''
        return f'{"" if self.category == Category.OTHER else self.category.name.lower()} computed {self.runorder.name.lower()}'
class TimeStep:
    '''A mutable container holding a single time step's inputs and outputs.'''
    def __init__(self, date: Union[datetime.date, int], inputs: Dict[str,Input], outputs: Dict[str,Output] = None):
        self._date = date
        cnt = sum([1 if v.category.name == Category.STORAGE else 0 for v in inputs.values()])
        if cnt < 2:
            self._inputs = inputs
        else:
            raise ValueError(f'The proposed timestep: {self.print_date()}, contains more than one storage value in its inputs resulting in an error.')   
        self._outputs = self.sort_outputs(outputs)
        # def sort_by_runorder_category(key: str):
        #     ro = outputs[key].run_order.name
        #     return 0 + outputs[key].category.value if ro == RunOrder.PRE_OPERATIONS.name else 10 + outputs[key].category.value 
        # self._outputs = OrderedDict(sorted(outputs, key=sort_by_runorder_category)) if outputs !=None else OrderedDict()
        #self._outputs = OrderedDict(sorted(outputs, key= lambda k: (outputs[k].run_order, outputs[k].category))) if outputs != None else OrderedDict()    
    def sort_outputs(self, outputs: Dict[str, Output]) -> OrderedDict[str, Output]:
        if outputs == None:
            return OrderedDict()
        else:
            scored = {}
            for k, v in outputs.items():
                # Order: RunOrder (PRE_OPERATIONS < POST_OPERATIONS), Category (INFLOW < OUTFLOW < STORAGE < OTHER)
                scored[k] = v.runorder.value * 10  + v.category.value 
            scored = {k: v for k, v in sorted(scored.items(), key=lambda x: x[1])}
            return {k: outputs[k] for k, _ in scored.items()} # the last two lines rely on the fact that dictionaries in Python 3.6+ remember their order of insertion.
    @property
    def date(self) -> Union[datetime.date, int]:
        '''The time step or date.'''
        return self._date
    @property
    def inputs(self) -> Dict[str, Input]:
        '''A dictionary of named input variables.'''
        return self._inputs
    @inputs.setter
    def inputs(self, inputs: Dict[str, Input]) -> Dict[str, Input]:
        self._inputs = inputs
    @property
    def outputs(self) -> OrderedDict[str, Output]:
        '''An ordered (first by Output.RunOrder then by Output.isoutflow) dictionary of computable variables.'''
        return self._outputs
    def inflows(self) -> float:
        '''Uses the Input.Category field to sum all inflow values.'''
        return sum([self.inputs[k].value for k in self.inputs.keys() if self.inputs[k].category.name == Category.INFLOW.name])
    def outflows(self) -> float:
        '''Uses the Input.Category field to sum all outflow values.'''
        return sum([self.inputs[k].value for k in self.inputs.keys() if self.inputs[k].category.name == Category.OUTFLOW.name])
    def storage(self):
        '''Uses the Input.Category field to sum all storage values.'''
        return sum([self.inputs[k].value for k in self.inputs.keys() if self.inputs[k].category.name == Category.STORAGE.name])
    def addinputs(self, new_inputs: Dict[str, Input]) -> 'TimeStep':
        '''Creates an new independent object based on self, plus new inputs (primarily by running outputs) to the timestep's existing inputs.'''
        result = copy.deepcopy(self)
        result.inputs = result._inputs | new_inputs
        return result
    def print_date(self):
        return self.date.strftime("%d %b %Y") if isinstance(self.date, datetime.date) else self.date
    def print_data(self, verbose: bool = False):
        s = ''
        for k, v in self.inputs.items():
            s += f', {k}: {v.print(verbose=verbose)}' if s else f'{k}: {v.print(verbose=verbose)}'
        for k, v in self.outputs.items():
            s += f', {k}: {v.print()}' if s else f'{k}: {v.print()}'
        return s
    def print(self, verbose: bool = False) -> str:
        '''Print a string representation of the data.'''
        return f'{self.print_date()} ({self.print_data(verbose=verbose)})'
class TimeSeries:
    '''
    A mutable container holding a list of timestep data.
    '''
    #TODO: Check to make sure other outputs requiring initialization have starting value.
    # add factory that allows or initial Timestep, then all other timesteps, also for irregular pattern to some inputs, outputs (e.g. every x timesteps include y in list)
    #TODO: Check for some consistency inputs, though outputs may be computed on irregular time steps.
    def __init__(self, timesteps: List[TimeStep]):
        self.timesteps: List[TimeStep] = timesteps
        self.storage_key: str = self.find_storage_key()
    def find_storage_key(self) -> str:
        '''Identifies the storage key for the time sereies. Note: only one storage key can be used across all the time steps in the time series.'''
        storage_keys = [str(k) for k, v in self.timesteps[0].inputs.items() if v.category.name == Category.STORAGE.name]
        if len(storage_keys) == 1:
            return storage_keys[0]
        else:
            raise ValueError('A storage value is not provided in the first timestep to initialize storage, this results in an error.')
    def dates(self) -> List[Union[datetime.date, int]]:
        '''Returns a list of timeseries dates.'''
        return [t.date for t in self.timesteps]
    def input(self, vname: str) -> List[Input]:
        '''Returns a list of Inputs with the specified variable name.'''
        return [t.inputs[vname].value for t in self.timesteps]
    def inflows(self) -> List[float]:
        '''Returns a list of inflows summed by timestep.'''
        return [sum([t.inputs[k].value for k in t.inputs.keys() if t.inputs[k].category.name == Category.INFLOW.name]) for t in self.timesteps]
    def outflows(self) -> List[float]:
        '''Returns a list of outflows summed by timestep.'''
        return [sum([t.inputs[k].value for k in t.inputs.keys() if t.inputs[k].category.name == Category.OUTFLOW.name]) for t in self.timesteps]
    def storage(self) -> List[float]: 
        '''Returns a list of storage values by timestep.'''
        return [sum([t.inputs[k].value for k in t.inputs.keys() if t.inputs[k].category.name == Category.STORAGE.name]) for t in self.timesteps]           
    def plot(self, *args):
        outplots = len(args)
        fig, ax = plt.subplots(nrows=3 + outplots, ncols=1, sharex=True, figsize=(10, 10))
        plt.suptitle('Simulation Summary Ouputs')
        ax[0].step(self.dates(), self.inflows(), where='post', color='cornflowerblue', linestyle='dashed', label='inflow')
        ax[1].step(self.dates(), self.storage(), where='post', color='blue', linestyle='solid', label='storage')
        ax[2].step(self.dates(), self.outflows(), where='post', color='darkorchid', linestyle='solid', label='outflow')
        for i in range(3): ax[i].set_ylabel('volume')
        i: int = 1
        for name in args:
            ax[i + 2].step(self.dates(), [self.timesteps[t].inputs[name].value for t in range(len(self.timesteps))], where='post', label=name)
            ax[i + 2].set_ylabel(name)
            i += 1
        #plt.ylabel('volume')
        fig.legend(frameon=False)
    
    @staticmethod
    def from_dataframe(df: pd.DataFrame, outputs: Union[List[Dict[str, Output]], None] = None):
        if outputs != None and len(outputs) != len(df): raise ValueError('The inputs and request outputs are not of equal length generating an error')
        t = 0
        ts = []
        for idx, row in df.iterrows():
            inputs = {}
            for name in df.columns:
                cat: Category
                if 'inflow' in name:
                    cat = Category.INFLOW
                elif 'outflow' in name:
                    cat = Category.OUTFLOW
                elif 'storage' in name:
                    cat = Category.STORAGE
                else: #has none of the above tags in the name
                    cat = Category.OTHER
                inputs[name] = Input(value=row[name], category=cat, isoutput=pd.isna(row[name]))
            if outputs == None or outputs[t] == None:
                ts.append(TimeStep(date=idx, inputs=inputs, outputs=None))
            else:
                ts.append(TimeStep(date=idx, inputs=inputs, outputs=outputs[t]))
        return TimeSeries(ts)
def inputs_dictionary_from_categoryname(inputs: List[Input]) -> Dict[str, Input]:
    '''Puts a list of inputs into a dictionary for a single timestep.'''
    result = {}
    for i in range(len(inputs)):
        k = inputs[i].category.name.lower()
        if result.has_key(k):
            result[k] = inputs[i]
        else:
            raise ValueError('The list contains more than one {k} input (based on the Input.Category.name), causing an error since it is stored in the output dictionary as a key.')
    return result
def factory(dates: Union[List[datetime.date], List[int]], inputs: Dict[str, Union[List[Input], List[Any]]], outputs: Union[Dict[str, List[Union[Output, None]]], None] = None) -> TimeSeries:
    timesteps = []
    # TODO check lengths of date and input lists, output list should be able to vary with a pattern
    print(f'dates: {len(dates)}, {print([len(v) for v in inputs.values()])}')
    for t in range(len(dates)):
        timesteps.append(TimeStep(dates[t], inputs={k: v[t] if isinstance(v[t], Input) else Input(v[t]) for k, v in inputs.items()}, outputs= {k: v[t] for k, v in outputs.items() if v[t] != None} if outputs != None else None))
    return timesteps
