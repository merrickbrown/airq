# exposes all modules in util without additional import needed
# this is only relevant when airq is itself imported. internally
# (startup_airq.py) still need to do 
# from util import thing 

from .util import *

