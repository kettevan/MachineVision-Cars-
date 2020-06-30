import pandas as pd
from tqdm import tqdm
import os
from PIL import Image

class Colors(object):
	class Color(object):
		def __init__(self, value):
			self.value = value

		def __str__(self):
			return "%s : %s" % (self.__class__.__name__, self.value)

	class Red(Color): pass
	class Blue(Color): pass
	class Green(Color): pass
	class Yellow(Color): pass
	class White(Color): pass
	class Gray(Color): pass
	class Black(Color): pass
	class Pink(Color): pass
	class Teal(Color): pass