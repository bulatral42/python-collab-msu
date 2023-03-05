import cowsay as cs
import cmd
import shlex
import sys


class CmdCowsay(cmd.Cmd):
    intro = "Welcome to cow farm!"
    prompt = "moo? "

    def do_make_bubble(self, args):
        '''
        Wraps text into a bubble
        make_bubble text [cowsay | cowthink] Wrap text inside a bubble
        '''
        parsed = shlex.split(args)
        if len(parsed) == 0:
            print("No text to bubble")
            return

        if len(parsed) > 0:
            text = parsed[0]

        if len(parsed) > 1:
            if parsed[1] in ['cowsay', 'cowthink']:
                brackets = cs.THOUGHT_OPTIONS[parsed[1]]
            else:
                print("Wrong brackets parameter")
                return
        else:
            brackets = cs.THOUGHT_OPTIONS['cowsay']

        print(cs.make_bubble(text, brackets))


    def do_cowsay(self, args):
        '''
        Emulate cowsay command: express cow's words
        cowsay message [cow [eyes [tongue]]]
        '''
        pass

    def do_cowthink(self, args):
        '''
        Emulate cowthink command: express cow's thoughts (similar to cowsay)
        cowthink message [cow [eyes [tongue]]]
        '''
        pass

    def do_list_cows(self, args):
        '''
        Lists all cow file names in the given or default directory
        list_cows [cowpath]
        '''
        parsed = shlex.split(args)
        if len(args) > 0:
            print(*cs.list_cows(parsed[0]))
        else:
            print(*cs.list_cows())



    def do_exit(self, args):
        '''
        Exit from cow commandline
        '''
        print("You're leaving our farm. See you next time!")
        return 1

    def precmd(self, line):
        if line == 'EOF':
            return 'exit'
        return line

    def emptyline(self):
        print("moo!")


if __name__ == "__main__":
    cmdcow = CmdCowsay()
    cmdcow.cmdloop()
