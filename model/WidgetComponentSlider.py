# pylint: disable=invalid-name
"""
Define the class for a Slider Widget Component.
"""
from dataclasses import dataclass

@dataclass
class WidgetComponentSlider:

    """
    Class for a Slider Widget Component.
    """

    component_id: str
    offset: int = 50
    offset_float: float = offset / 100