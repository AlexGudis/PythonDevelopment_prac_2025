import cmd
import calendar
import shlex

months = dict()

class calend(cmd.Cmd):
    prompt = "cmd>> "

    def do_pryear(self, theyear):
        """Print a month’s calendar as returned by formatmonth()"""
        try:
            calendar.TextCalendar().pryear(int(theyear))
        except ValueError:
            print('Invalid arguments')

    def do_prmonth(self, line):
        "Print a month’s calendar as returned by formatmonth()."
        line = shlex.split(line)
        try:
            calendar.TextCalendar().prmonth(int(line[0]), months[line[1]])
        except ValueError:
            print('Incorrect arguments')

    def complete_prmonth(self, text, line, begidx, endidx):
        words = (line[:endidx] + ".").split()
        return [c.name for c in list(calendar.Month) if c.name.startswith(text)]

    def do_EOF(self, args):
        return 1

if __name__ == '__main__':
    for el in list(calendar.Month):
        months[el.name] = el
    calend().cmdloop() 