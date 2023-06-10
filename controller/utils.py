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


def last_folder_update(folder_path: str = 'acoustics') -> float:
    max_modification_time = 0.0

    for file_path in glob(f'{folder_path}/*'):
        if not os.path.isfile(file_path):   
            continue

        modification_time = os.path.getmtime(file_path)

        if modification_time <= max_modification_time:
            continue
        
        max_modification_time = modification_time

    return max_modification_time


def make_url(ip_address: str, port: int) -> str:
    return f'http://{ip_address}:{port}'