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
    before_image: str = ''
    after_image: str = ''
    component_id: str = None
    offset: int = 50
    offset_float: float = offset / 100
