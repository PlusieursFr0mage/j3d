import random
import noise
from noise import pnoise2

factor = 15 #it doesn't need to be 15, it can be anything different from greater than 1 or lower than -1, otherwise it will return 0.0
oct=6
seed=100


print(pnoise2(0.91, 4, octaves=oct, base=seed))
#help(noise)
