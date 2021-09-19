import sys

import datetime
from enum import Enum
from typing import List, Dict, Callable, Any

import numpy as np
import pandas as pd

sys.path.insert(0, '/Users/johnkucharski/Documents/source/canteen')
import src.data as data
import src.outlet as outlet
import src.reservoir as reservoir

import src.operations as operations
import src.utilities as utilities

                       
#TODO #1:
# (1) Add optimize class (inherits simulation) 
# (a) objectives = List[(str, symbol (<,>,=), value)] each str would be the name of a column of output (may want same string twice so a list not a dictionary),
# (b) penalty = callable function loops over output from Simulation.simulate() and computes penalty at each time step.
# (c) something like "levers" to modify operations? or just redefine operations?
# * perhaps levers could multiple a rule's outflow by some value. This could be added to all the rules as a optional argument usually set to 1.
# * i think these "levers" are "action names" in the PTreeOpt() init. The actual levers are in the PTreeOpt.f function in an if action_name == "action name" then pull lever style.
# (d) something like "indicators", like flow or storage that say when to activate a lever. This is what the policy tree should find.
# * I think indicators in the policy tree are called: features, and feature names on the PTreeOpt() init

class Run_Order(Enum):
    BEFORE_OPERATIONS = 0,
    BEFORE_STORAGE = 1,
    AFTER_STORAGE = 2

class Additional_Output:
    def __init__(self, fn: Callable[[data.Input], Dict[str, Any]], is_outflow: bool = False, run_order: Run_Order = Run_Order.AFTER_STORAGE):
        self._fn = fn
        self._is_outflow = is_outflow
        if is_outflow and run_order == Run_Order.AFTER_STORAGE: raise ValueError(f'The output is marked as an outflow. It must be run before storage calculations performed but is set to run after storage calculations.')
        else: self._run_order = run_order
    @property
    def run_order(self) -> Run_Order:
        return self._run_order
    @property
    def is_outflow(self) -> bool:
        return self._is_outflow
    
    def run(self, input: data.Input) -> Any:
        return self._fn(input)    

class Simulation:
    def __init__(self, inputs: List[data.Input],
                 reservoir: reservoir.Reservoir = reservoir.Reservoir(),
                 operations_fn: Callable[[data.Input, List[outlet.Outlet]], Dict[str, float]] = operations.passive_operations,
                 additional_outputs: Dict[str, Additional_Output] = {}):
        self._inputs = inputs
        self._reservoir = reservoir
        self._f_operations = operations_fn
        self._additional_ouputs = additional_outputs
        
        
    @property
    def inputs(self) -> List[data.Input]:
        return self._inputs
    @property
    def reservoir(self) -> reservoir.Reservoir:
        return self._reservoir
    @property
    def additional_outputs(self) -> Dict[str, Additional_Output]:
        return self._additional_ouputs
    
    def operations(self, input: data.Input, outlets: List[outlet.Outlet]) -> Dict[str, float]:
        return self._f_operations(input, outlets)
    
    def simulate(self) -> Dict[str, List[Any]]:
        outputs = {}
        for t in range(len(self.inputs)):
            outflow: Dict[str, float] = self.add_outflows(input)
            outflow.update(self.operations(self.inputs[t], self.reservoir.outlets))
            outflow = self.add_outflows(self.inputs[t], outflow, Run_Order.BEFORE_STORAGE)
            if t + 1 < len(self.inputs) and self.inputs[t + 1].update_storage: 
                self.inputs[t + 1].storage = self.inputs[t].storage + self.inputs[t].inflow - sum(outflow.values())
            output = self.add_outputs(self.inputs[t], outflow) if self.additional_outputs else outflow
            outputs.update({ k: outputs[k] + [v] if k in outputs else [v] for k, v in output.items()})
            outflow.clear()
            output.clear()
        return self.input_to_dict() | outputs      
    def add_outflows(self, input: data.Input, outflow: Dict[str, float] = {}, run_order = Run_Order.BEFORE_OPERATIONS) -> Dict[str, float]: 
        for k, v in self.additional_outputs.items():
            if v.run_order == run_order and v.is_outflow: outflow[k] = v.run(input)
        return outflow
    def add_outputs(self, input: data.Input, output: Dict[str, Any] = {}):
        for k, v in self.additional_outputs.items():
            if not v.is_outflow: output[k] = v.run(input)
        return output  
            
    def input_to_dict(self):    
        d = { k: np.full(len(self.inputs), np.nan).tolist() for k, _ in self.inputs[0].to_dict().items()}
        for i in range(0, len(self.inputs)):
            for k, v in self.inputs[i].to_dict().items():
                if k in d:
                    d[k][i] = v
                else:
                    l = np.full(len(self.inputs), np.nan).tolist()
                    l[i] = v
                    d[k] = l
        return d