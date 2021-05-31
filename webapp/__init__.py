# since this is the only module, import all items
# making them available as webapp.<thing> instead of app.<thing>
# see for example __init__.py for linalg submodule of numpy
from . import app
from .app import *
