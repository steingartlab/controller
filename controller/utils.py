from enum import Enum
from dataclasses import fields
from typing import Type

class ZeroBasedAutoEnum(Enum):
    """Zero-based enum because it's 2023 and we're not using MatLab."""

    def _generate_next_value_(name, start, count, last_values):
        if len(last_values) > 0:
            return last_values[-1] + 1
        return 0


def dataclass_from_dict(dataclass_: Type, dict_: dict) -> Type:
    """Populated dataclass from a dictionary.
    
    Used to parse incoming http dicts to a dataclass.

    Args:
        dataclass_ (Type): Dataclass object, i.e. not an instance of it.
        dict_ (dict): Dict that matches keys of dataclass_ **exactly**.

    Returns:
        Type: Dataclass instance, populated by values from dict.
    """

    field_set = {f.name for f in fields(dataclass_) if f.init}
    filtered_arg_dict = {k : v for k, v in dict_.items() if k in field_set}
    
    return dataclass_(**filtered_arg_dict)