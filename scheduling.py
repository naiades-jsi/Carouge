import pandas as pd
import numpy as np
from time import time
from datetime import datetime

# Scheduling of watering times ... maybe not needed?
# 
# 

def SimpleSchedule(last_watering, timestep):
    # adds timestep to current time
    # timestep = [days, hours]
    next = last_watering + timestep
    return(next)