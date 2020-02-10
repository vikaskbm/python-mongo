from infrastructure.switchlang import switch
import program_hosts as hosts
import infrastructure.state as state
import services.data_service as svc
from dateutil import parser


def run():
    print(' ****************** Welcome guest **************** ')
    print()

    show_commands()

    while True:
        action = hosts.get_action()

        with switch(action) as s:
            s.case('c', hosts.create_account)
            s.case('l', hosts.log_into_account)

            s.case('a', add_a_snake)
            s.case('y', view_your_snakes)
            s.case('b', book_a_cage)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')

            s.case('?', show_commands)
            s.case('', lambda: None)
            s.case(['x', 'bye', 'exit', 'exit()'], hosts.exit_app)

            s.default(hosts.unknown_command)

        state.reload_account()

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an account')
    print('[L]ogin to your account')
    print('[B]ook a cage')
    print('[A]dd a snake')
    print('View [y]our snakes')
    print('[V]iew your bookings')
    print('[M]ain menu')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def add_a_snake():
    print(' ****************** Add a snake **************** ')
    # TODO: Require an account
    if not state.active_account:
        print(f"You have to be logged in")  
        return 


    # TODO: Get snake info from user
    name = input('Enter name of snake')

    species = input('Enter Species of snake')
    length = int(input('Enter length of snake'))
    is_venomous = input('Is the snake venomous [y/n]').lower().startswith('y')

    snake = svc.add_snake(state.active_account, name,species,length,is_venomous)
    state.reload_account()
    print(f"successfully created snake {snake.name} with id {snake.id}")

    

def view_your_snakes():
    print(' ****************** Your snakes **************** ')

    # TODO: Require an account
    if not state.active_account:
        print(f"You have to be logged in")  
        return 

    # TODO: Get snakes from DB, show details list
    snakes = svc.get_snakes_for_user(state.active_account)
    print(f"You have {len(snakes)} snakes")
    for s in snakes:
        print(" * {} is a {} - {}n long and {} venomous".format(
            s.name,
            s.species,
            s.length,
            '' if s.is_venomous else 'not'
            ))



def book_a_cage():
    print(' ****************** Book a cage **************** ')
    # Require an account
    if not state.active_account:
        print(f"You have to be logged in")  
        return 

    # Verifying that user have a snake
    snakes = svc.get_snakes_for_user(state.active_account)
    if not snakes:
        print("You should frist [a]dd snakes in before booking a cage")

    # TODO: Get dates and select snake
    print("Lets check for available bookings")
    start_date = input("Enter check in date [yyyy-mm-dd]")
    if not start_date:
        print("cancelled")
        return

    check_in = parser.parse(
        start_date
    )

    checcheck_out = parser.parse(
        input("Enter check in date [yyyy-mm-dd]")
    )

    if check_in>check_out:
        print("Error: check_in must be before check_out")
        return

    snakes = svc.get_snakes_for_user(state.active_account)
    for idx,s in enumerate(snakes):
        print(" {} - {} -> {}m long and {}venomous".format(
            idx+1,
            s.name,
            s.length,
            '' if s.is_venomous else 'not '
            ))

    snake = snakes[int(input('Enter snake number that you wish to book'))-1]

    # Find cages available across date range for our particular snake attributes
    cages = svc.get_available_cages(check_in,check_out,snake)

    print(f"You snake can be booked in {len(cages)} cages ")    
    for idx,c in enumerate(cages):
        print("{} - {c.name} is {c.square_meters} meters. Carpeted = {}, Has Toys = {}". format(
            idx+1,
            c.name,
            c.square_meters,
            "YES" if c.is_carpeted else 'NO',
            "YES" if c.has_toys else 'NO'            
            ))

    if not cages:
        print("No cages that can be booked")
        return

    cage = cages[int(input('Enter cage number that you wish to book'))-1]
    svc.book_cage(snake,cage,checkin,checkout)

    print("successfully nooked a new cage")
       


def view_bookings():
    print(' ****************** Your bookings **************** ')
    if not state.active_account:
        print(f"You have to be logged in")  
        return 

    snakes = {s.id: s for s in svc.get_snakes_for_user(state.active_account)}
    bookings = svc.get_bookings_for_user(state.active_account)

    for b in bookings:
        print(" -> Snake: {}, Booked at: {}, From: {} To: {}".format(
                snakes.get(b.guest_snake_id).name,
                b.cage,
                datetime.date(b.check_in_date.year,b.check_in_date.month,b.check_in_date.day),
                (b.check_out_date-b.check_in_date).days
            ))