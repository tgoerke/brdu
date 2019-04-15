import numpy as np
import scipy as sp
import scipy.stats
from iminuit import Minuit
import argparse
import warnings
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import json
from .clapy import web_fit


def calc(ncells=None,times=None,datas=None,opath="fit/static",name="123"):
    return web_fit(ncells,times,datas,opath,name)
