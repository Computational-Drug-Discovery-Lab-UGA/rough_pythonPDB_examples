#!/usr/bin/python

import re
import os
import os.path
import sys
import shutil
import urllib.request
import time
from warnings import filterwarnings

"""This is simply the main method where the main flow of the 
program is."""
def main():
    inAlready = False
    with open("TextFile2.txt") as f:
        currentSurfaceSerials = []
        i = 0
        for l in f:#this separates the lines of the coordinate files
            lineNumber = int(re.search(r'\d+', l).group())
            if(i == 0):
                currentSurfaceSerials.append(lineNumber)
                i += 1
            else:
                inAlready = False
                for item in currentSurfaceSerials:
                    if(item == lineNumber):
                        inAlready = True

            if(not inAlready):
                currentSurfaceSerials.append(lineNumber)
    print(len(currentSurfaceSerials))


main()
