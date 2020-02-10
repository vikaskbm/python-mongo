from colorama import Fore, init
from infrastructure.switchlang import switch
import infrastructure.state as state
import services.data_service as svc
from dateutil import parser


def run():
    print(' ****************** Welcome host **************** ')
    print()

    show_commands()

    while True:
        action = get_action()

        with switch(action) as s:
            s.case('c', create_account)
            s.case('a', log_into_account)
            s.case('l', list_cages)
            s.case('r', register_cage)
            s.case('u', update_availability)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')
            s.case(['x', 'bye', 'exit', 'exit()'], exit_app)
            s.case('?', show_commands)
            s.case('', lambda: None)
            s.default(unknown_command)

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an account')
    print('Login to your [a]ccount')
    print('[L]ist your cages')
    print('[R]egister a cage')
    print('[U]pdate cage availability')
    print('[V]iew your bookings')
    print('Change [M]ode (guest or host)')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def create_account():
    print(' ****************** REGISTER **************** ')
    name = input("Enter a name : ")
    email = input("Enter your email : ")

    old_account = svc.find_account_by_email(email)
    if old_account:
        print(f'ERROR:Account with email {email} already exists')
        return

    state.active_account = svc.create_account(name,email)
    print(f"created new account with {state.active_account.id}")


def log_into_account():
    print(' ****************** LOGIN **************** ')

    email = input("Enter your email : ").strip().lower()
    account = svc.find_account_by_email(email)
    if not account:
        print(f"User with email {email} not found")

    state.active_account = account
    print(f"User logged in successfully ")


def register_cage():
    print(' ****************** REGISTER CAGE **************** ')
    if not state.active_account:
        print(f"You have to be logged in")  
        return

    meters = input("Enter lengtg of snake")
    if not meters:
        print("cancelled")
        return

    meters = float(meters)
    name=input("Enter name of cage")
    price=float(input("Enter price of cage"))
    is_carpeted=input("is_carpeted?").lower().startswith('y')
    has_toys=input("has_toys ?").lower().startswith('y')
    allow_dangerous_snakes=input("allow dangerous snakes?").lower().startswith('y')

    cage = svc.register_cage(state.active_account,name,meters,
            is_carpeted,has_toys,allow_dangerous_snakes,price)

    state.reload_account()
    print(f"created new cage with {cage.id}")




def list_cages(supress_header=False):
    if not supress_header:
        print(' ******************     Your cages     **************** ')

    if not state.active_account:
        print(f"You have to be logged in")  
        return

    cages = svc.find_cage_for_user(state.active_account)
    print(f"You have {len(cages)} cages")    
    for idx,c in enumerate(cages):
        print(f" {idx+1} - {c.name} is {c.square_meters} meters")
        for b in c.bookings:
            print(" - Booking {}, {}. Booked - {} ".format(
                b.check_in_date,
                (check_out_date-check_in_date).days,
                'YES' if b.booked_date else 'NO'
            ))




def update_availability():
    print(' ****************** Add available date **************** ')

    if not state.active_account:
        print("You need to login")
        return

    list_cages(supress_header=True)


    cage_num = input("Enter Cage num ")
    if not cage_num:
        print("Didnt enter cage num")
        return

    cage_num = int(cage_num)

    cages = svc.find_cage_for_user(state.active_account)
    selected_cage = cages[cage_num-1]
    print(f"Selected cage {selected_cage}")
    # parser comes from dateutils in datetime module
    start_date = parser.parse(input("Enter start date[yyyy-mm-dd]: "))
    days = int(input("Hpw many days do you wish you rent: "))

    svc.add_date(selected_cage,start_date,days)
    state.reload_account()



def view_bookings():
    print(' ****************** Your bookings **************** ')
    if not state.active_account:
        print("You need to login")
        return

    cages = svc.find_cage_for_user(state.active_account)
    bookings = [
        (c,b) 
        for c in cages
        for b in c.bookings
        if b.booked_date is not None
    ]

    print(f"You have {len(bookings)} bookings")
    for c,b in bookings:
        print(" -> Cage {} booked_date:{}, from: {}, for: {}".format(
            c.name,
            datetime.date(b.booked_date.year,b.booked_date.month,b.booked_date.day),
            datetime.date(b.check_in_date.year,b.check_in_date.month,b.check_in_date.day),
            b.duration_in_days

            ))


def exit_app():
    print()
    print('bye')
    raise KeyboardInterrupt()


def get_action():
    text = '> '
    init(convert=True)
    if state.active_account:
        text = f'{state.active_account.name}> '

    action = input(Fore.YELLOW + text + Fore.WHITE)
    return action.strip().lower()


def unknown_command():
    print("Sorry we didn't understand that command.")


def success_msg(text):
    init(convert=True)
    print(Fore.LIGHTGREEN_EX + text + Fore.WHITE)


def error_msg(text):
    init(convert=True)
    print(Fore.LIGHTRED_EX + text + Fore.WHITE)
