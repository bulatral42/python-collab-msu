import cowsay as cs
import cmd
import shlex


def parse_cowargs(parsed):
    message = parsed[0]
    cow, eyes, tongue, cowfile = 'default', 'oo', '  ', None
    if len(parsed) > 1:
        if '/' in parsed[1]:
            cowfile = parsed[1]
        elif parsed[1] in cs.list_cows():
            cow = parsed[1]
        else:
            print(f'cowsay: Could not find {parsed[1]} cowfile!')
            return None
    if len(parsed) > 2:
        eyes = parsed[2][:2]
    if len(parsed) > 3:
        tongue = parsed[3][:2]

    return message, {'cow': cow, 'eyes': eyes, 'tongue': tongue, 'cowfile': cowfile}


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

        text = parsed[0]

        if len(parsed) > 1:
            if parsed[1] in ['cowsay', 'cowthink']:
                brackets = cs.THOUGHT_OPTIONS[parsed[1]]
            else:
                print(f"Wrong brackets parameter: {parsed[1]}")
                return
        else:
            brackets = cs.THOUGHT_OPTIONS['cowsay']

        print(cs.make_bubble(text, brackets))


    def do_cowsay(self, args):
        '''
        Emulate cowsay command: express cow's words
        cowsay message [cow [eyes [tongue]]]
        '''
        parsed = shlex.split(args)
        if len(parsed) == 0:
            print("No message to say")
            return

        cowargs = parse_cowargs(parsed)
        if cowargs:
            print(cs.cowsay(cowargs[0], **cowargs[1]))
        else:
            return


    def do_cowthink(self, args):
        '''
        Emulate cowthink command: express cow's thoughts (similar to cowsay)
        cowthink thoughts [cow [eyes [tongue]]]
        '''
        parsed = shlex.split(args)
        if len(parsed) == 0:
            print("No thoughts to think")
            return
        cowargs = parse_cowargs(parsed)
        if cowargs:
            print(cs.cowthink(cowargs[0], **cowargs[1]))
        else:
            return

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
