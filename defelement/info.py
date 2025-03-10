"""Information about DefElement."""

import os

from defelement import settings

number_of_elements = len([
    file for file in os.listdir(settings.element_path)
    if file.endswith(".def") and not file.startswith(".")])
