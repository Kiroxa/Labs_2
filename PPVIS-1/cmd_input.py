import argparse


VERSION = "0.1.0"


def parse_args(args: list):
    ''' Adds settings and returns these parameters '''
    
    parser = argparse.ArgumentParser(prog="ATM", description="Simulation between user and bank.")
    parser.add_argument("pin", nargs='?', help="Card PIN")
    
    parser.add_argument("--version", action='version', version=f'%(prog)s version {VERSION}', help="Print version info")
    
    parser.add_argument("-l", "--load", action='store', help="Load a program session from saving file")
    parser.add_argument("-b", "--balance", action='store_true', help="Show card balance")
    parser.add_argument("-w", "--withdraw", nargs='?', help="Add the cash to withdraw")
    parser.add_argument("-p", "--phone", nargs='*', help="Add phone number and cash")
    parser.add_argument("-d", "--draft", action='store_true', help="Show other objects parameters")
    parser.add_argument("-s", "--save", action='store_true', help="Save process in continue.json")

    return parser.parse_args(args)


def set_args(args) -> dict:
    ''' Sets the settings for the program to work and returns a dictionary with settings '''
    
    return {
        "version": VERSION,
        "load": args.load if args.load else False,
        "balance": args.balance if args.balance else False,
        "pin": args.pin,
        "withdraw": args.withdraw if args.withdraw else False,
        "phone": args.phone if args.phone else False,
        "draft": args.draft if args.draft else False,
        "save": args.save if args.save else False,
    }


def main():
    pass


if __name__ == "__main__":
    main()