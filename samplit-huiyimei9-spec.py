import sys
import random
name = sys.argv[1]
with open(name) as file:
    for line in file:
        if random.random() < 0.01:
            print(line)
