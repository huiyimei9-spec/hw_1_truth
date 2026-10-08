import sys
import random
file_name = sys.argv[1]
with open(file_name) as file:
    for line in file:
        if random.random() < 0.01:
            print(line)
