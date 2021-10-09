from src.simulation import Simulation
from typing import Callable, Dict, List, Tuple, OrderedDict, Any

import ptreeopt
'''
Thresholds should be in the form of: Dict[str, List[Any]]:
* Each list should have 1 or 2 items:
** 1 Item Lists:
Item 1: 'min' or 'max'
** 2 Item Lists:
['<', threshold_value: float] meaning the metric x should NOT be penalized if x < threshold value.
['>', threshold_value: float] meaning the metric x should NOT be penalized if x > threshold value.
[min: float, max: float] meaning the metric x should NOT be penalized if min < x < max threshold values.
''' 

class Optimization:
    def __init__(self, simulation_model: Simulation, 
                 thresholds: Dict[str, List[List[Any]]], 
                 indicators: OrderedDict[str, Tuple[float, float]],
                 actions: List[Any] 
                 ):
        self._simulation_model = simulation_model
        self._thresholds = thresholds
        self._indicators = indicators
        self._actions = actions
        
    @property
    def simulation_model(self):
        return self._simulation_model
    @property
    def thresholds(self):
        return self._thresholds
    # THRESHOLDS:
    # 'total release > 10 #af
    # 'elevation < 1554 #ft
    # min salinity
    @property
    def indicators(self) -> List[str]:
        return self._indicators
    # INDICATORS:
    # {'storage': [conservation_pool, surcharge], 'inflow': [0, 99%], 'salinity': [0, 2%? threshold]}
    def actions(self) -> List[Any]:
        return self._actions
    # ACTIONS (10):
    # [0, .1, .25, .50, .75, .90, 1, 1.25, 1.50, 2]
    
    
    min_release, max_release = 10, 10000
     
    def penalty(self, output: Dict[str, Any]) -> float:
        #threshold: Dict[str, List[Any]]
        #output: Dict[str, Any]
        penalty = 0
        for k, v in self.thresholds.items(): 
            if k in output:
                metric = output[k]
                if v[0] == 'min':
                    penalty += metric**10 
                elif v[0] == 'max':
                    penalty += metric**2 * -1
                elif v[0] == '<':
                    penalty += max(v[1] - metric, 0)**2
                elif v[0] == '>':
                    penalty += max(metric - v[1], 0)**2
                else:
                    penalty += max(v[1] - metric, 0)**2 + max(metric - v[1], 0)**2
            else:
                raise KeyError(k)
        return penalty
    
    def optimize(self, P: ptreeopt.PTree):
        penalties = []
        output: Dict[str, Any] = {}
        inputs = self.simulation_model.inputs
        for t in range(len(inputs)):
            if t == 0:
                output = self.simulation_model.step_foward(t)
            else:
                action, rule = P.evaluate(self.indicator_states(output))     
                output = self.simulation_model.step_foward(t, float(action))
                penalty = self.penalty(output)
                output['penalty'] = penalty
                penalties.append(penalty)
            #print(output)
        return sum(penalties)
          
    def indicator_states(self, output: Dict[str, Any]) -> List[Any]:
        states: List[Any] = []
        for k, _ in self.indicators.items():
            states.append(output[k])
        return states 
     