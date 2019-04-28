import subprocess
import threading
import os
import time
from random import randint
runs=[]
# ( runs, porta)
runs.append((10000000000000, 8080))

for r in runs:
    for run_number in range(0, r[0]):
        xterm = 'xterm -hold -e'
        var = str(randint(8080, 8083))
        comp_xterm = 'python3 viewer.py --port '+ var
        str_xterm = xterm +' "'+ comp_xterm + '"' 
        os.system(str_xterm +'&')
        os.system('python3 student_read.py --port ' + var)
        os.system('killall xterm')
