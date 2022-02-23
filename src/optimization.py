from turtle import pen
from src.data import TimeStep, Input, Category
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
        self._simulation = simulation_model
        self._thresholds = thresholds
        self._indicators = indicators
        self._actions = actions
        
    @property
    def simulation(self):
        return self._simulation
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
     
    def penalty(self, t: TimeStep) -> float:
        # previous arg = output: Dict[str, Any]
        #threshold: Dict[str, List[Any]]
        #output: Dict[str, Any]
        penalty = 0
        for k in self.thresholds.keys(): 
            if k == 'inflow':
                metric = t.inflows()
            elif k == 'storage':
                metric = t.storage()
            elif k == 'outflow':
                metric = t.outflows()
            elif k in t.inputs:
                metric = t.inputs[k].value
            else:
                raise KeyError(k)
        for v in self.thresholds.values():
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
        return penalty   
        #     if k in output:
        #         metric = output[k]
        #         if v[0] == 'min':
        #             penalty += metric**10 
        #         elif v[0] == 'max':
        #             penalty += metric**2 * -1
        #         elif v[0] == '<':
        #             penalty += max(v[1] - metric, 0)**2
        #         elif v[0] == '>':
        #             penalty += max(metric - v[1], 0)**2
        #         else:
        #             penalty += max(v[1] - metric, 0)**2 + max(metric - v[1], 0)**2
        #     else:
        #         raise KeyError(k)
        # return penalty
    
    def optimize(self, P: ptreeopt.PTree):
        penalties = 0
        ts: List[TimeStep] = []
        newinputs: Dict[str, Input] = {}
        for t in range(len(self.simulation.timeseries.timesteps)):
            ts.append(self.simulation.timeseries.timesteps[t] if t == 0  else self.simulation.timeseries.timesteps[t].addinputs(newinputs))
            if t == 0:
                ts, newinputs = self.simulation._stepforward(ts, t, newinputs)
            else:
                action, rule = P.evaluate(self.indicator_states(ts[t - 1]))
                ts, newinputs = self.simulation._stepforward(ts, t, newinputs, action)
                ts[t] = ts[t].addinputs({'penalty': Input(self.penalty(ts[t]), Category.OTHER, True)})
                penalties += ts[t].inputs['penalty'].value
        return penalties        
        # penalties = []
        # output: Dict[str, Any] = {}
        # inputs = self.simulation_model.timeseries.timesteps
        # for t in range(len(inputs)):
        #     if t == 0:
        #         output = self.simulation_model._stepfoward(t)
        #     else:
        #         action, rule = P.evaluate(self.indicator_states(output))     
        #         output = self.simulation_model._stepfoward(t, float(action))
        #         penalty = self.penalty(output)
        #         output['penalty'] = penalty
        #         penalties.append(penalty)
        #     #print(output)
        # return sum(penalties)
          
    def indicator_states(self, t: TimeStep) -> List[Any]:
        states: List[Any] = []
        for k, _ in self.indicators.items():
            if k == 'inflow':
                states.append(t.inflows())
            elif k == 'storage':
                states.append(t.storage())
            elif k == 'outflow':
                states.append(t.outflows())
            else:
                states.append(t.inputs[k].value)
        return states 
     