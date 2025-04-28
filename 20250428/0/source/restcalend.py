import calendar
import sys

y, m = int(sys.argv[1]), int(sys.argv[2])

s = calendar.month(y, m).split('\n')

#print(s[0].split(' '))

if len(s[2].split()) == 7:
    print(calendar.month(y, m))
else:
    print('First day of the month is not a monday')