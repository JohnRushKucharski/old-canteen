#region Header
# %% [markdown]
# # Validaiton Baseclass
# Provides an interface for validation
#
# Author: John Kucharski | Date: 12 June 2021
#
# Status: open to extension, closed to change
# Testing: no implementation to test

# %% [markdown]
# Todo
#

# %% [markdown]
# Dependencies
import abc
import typing
#endregion

# %%
class Validator(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def is_valid(obj: object) -> typing.Tuple[bool, typing.List[str]]:
        pass
    @staticmethod
    @abc.abstractmethod
    def messages(obj: object) -> typing.List[str]:
        pass