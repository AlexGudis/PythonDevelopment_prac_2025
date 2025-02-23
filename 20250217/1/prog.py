import sys
import os

path = sys.argv[1]
if len(sys.argv) == 2:
    full_path = path + '/' + ".git" + "/" + "refs" + '/' + "heads"
    for br in os.listdir(full_path):
        print(br)

else:
    print('SMT NEW')
    