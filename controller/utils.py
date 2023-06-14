from enum import Enum
from dataclasses import fields
from glob import glob
import os
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


def last_folder_update(folder_path: str = 'acoustics') -> float:
    """Check when folder was last updated.
    
    Args:
        folder_path (str, optional): Folder location.
            Defaults to 'acoustics' (don't want to hardcode bc tests).

    Returns:
        float: Unix timestamp of last update.
    """
    
    max_modification_time: float = -1.0

    for file_path in glob(f'{folder_path}/*'):
        if not os.path.isfile(file_path):   
            continue

        modification_time = os.path.getmtime(file_path)

        if modification_time <= max_modification_time:
            continue
        
        max_modification_time = modification_time

    return max_modification_time


def make_url(ip_address: str, port: int) -> str:
    """Parse url from its constituents.
    
    Args:
        ip_address (str): Format 192.168.0.1.
        port (int): Format 8001.

    Returns:
        str: Formatted url.
    """
    return f'http://{ip_address}:{port}'