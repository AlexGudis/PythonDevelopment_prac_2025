import shlex
import readline

fio = input("ФИО = ")
hb = input("Место рождения = ")


print(shlex.join(["register", fio, hb]))


