# region Header
# %% [markdown]
# # Validation
# Provides an interface for validation
#
# Author: John Kucharski | Date: 12 June 2021
#
# Status: open to extension, closed to change
# Testing: no implementation to test
#
# TODO: #15 This has not been implemented, except in the Reservoir class
# endregion

# region Dependencies
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Protocol
# endregion

class Level(Enum):
    '''
    Captures the seriousness of validation message.
    '''
    MESSAGE = 0,
    '''
    Indicates a informational message, that may affect the validity of a computational results but should immediately prevent a computation from occuring.
    '''
    ERROR = 1,
    '''
    Indicates an issue that will prevent computations from occuring.
    '''

@dataclass
class Message:
    '''
    Records validation messages for objects.
    '''
    level: Level
    '''
    Describes the message severity.
    '''
    text: str
    '''
    A text message.
    '''
    def print() -> str:
        '''
        prints a string representation of the message level and message text.
        '''

# %%
class Validator(Protocol):
    '''
    An interface for the validation of class objects at the time of construction or change that returns messages.
    
    Note: messages() should be called, the maximum Message.level returned by the funcion call should be checked to determine if the object is valid or not.
    '''
    @property
    def messages(self) -> List[Message]:
        '''
        A property recording the current messages.
        '''
    @staticmethod
    def is_valid(self) -> bool:
        '''
        True if the object is valid (has no ERROR messages), otherwise False.
        '''
    @staticmethod
    def validate(self) -> List[Message]:
        '''
        Gathers validation messsages from an object
        '''