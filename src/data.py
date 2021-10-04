#region Header
# %% [markdown]
# # Input
#
# Author: John Kucharski | Date: 28 August 2021
#
# Status: open
# Testing: partial

#%%
#TODO: #2 Add Factories
#TODO: #4 Output Objects
#endregion

#region Dependencies
#%%
import datetime
from typing import List, Dict, Union, Any 
import numpy as np        
#endregion

#%%
class Additional_Input:
    '''
    Provide a class for storing non-standard input variables (for example: temperature).
    
    Notes: inputs can labeled as mutable [update = True] or imutable [update = False].
    Some inputs are also operational outputs (i.e., reservoir releases), marking these variables as outputs [output = True] will repress them from being printed to dictionaries and dataframes.
    '''
    def __init__(self, value: Any = np.nan, update: bool = True, output = False):
        self._value = value
        self._update = update
        self._output = output
    @property
    def value(self) -> Any:
        return self._value
    @property
    def update(self) -> bool:
        return self._update
    @property
    def output(self) -> bool:
        return self._output
    
    def print(self, digits: int = 0) -> str:
        def mutablity_tag(x: bool) -> str:
            return 'm' if self.update else 'im'
        return f'{round(self.value, digits)} [{mutablity_tag(self.update)}]' 

#%%    
class Input:
    def __init__(self, date: datetime.date, inflow: float, storage: float = np.nan, update_storage: bool = True, additional_inputs: Union[Dict[str, Additional_Input], None] = None) -> None:
        self._date = date
        self._inflow = inflow
        self._storage = storage
        self._update_storage = update_storage
        self._additional_inputs = additional_inputs
        
    @property
    def date(self) -> datetime.date:
        return self._date
    @property
    def inflow(self) -> float:
        return self._inflow
    @property
    def storage(self) -> float:
        return self._storage
    @storage.setter
    def storage(self, storage: float) -> None:
        self._storage = storage
        # isvalid, exception = utilities.is_on_range(storage, 0, np.inf, 'storage', 'Input.storage() setter')
        # if not isvalid:
        #     raise exception
        # else:
        #     self._storage = storage
    @property 
    def update_storage(self) -> bool:
        return self._update_storage
    @property
    def additional_inputs(self) -> Union[Dict[str, Additional_Input], None]:
        return self._additional_inputs
   
    def print(self, digits: int = 0) -> str:
        def print_storage():
            return np.nan if np.isnan(self.storage) else round(self.storage, digits)
        def print_additionalinputs():
            return 'none' if self.additional_inputs is None else { k: v.print(digits) for k, v in self.additional_inputs.items() }
        return f'{self.date.strftime("%d %b %Y")} (inflow: {round(self.inflow)}, storage: {print_storage()}, additional inputs: {print_additionalinputs()})'
    
    def to_dict(self) -> Dict[str, Any]:
        base = {
            'date': self.date.strftime("%d %b %Y"),
            'inflow': self.inflow,
            'storage': self.storage,    
        }
        if self.additional_inputs == None:
            return base
        else: 
            add = { k: v.value for k, v in self.additional_inputs.items() if not v.output}
            return base | add
    
    @staticmethod
    def inputs_factory(dates: List[datetime.date], inflows: List[float], storages: List[float], update_storage: bool, additional_inputs: List[Union[Dict[str, Additional_Input], None]]):
        return [Input(dates[i], inflows[i], storages[i], update_storage, additional_inputs[i]) for i in range(len(dates))]
    
    @staticmethod
    def inputs_from_csv(path: str):
        pass