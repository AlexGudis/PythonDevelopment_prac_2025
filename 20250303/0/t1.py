import shlex

s = input()
s = shlex.split(s)
print(shlex.join(s))