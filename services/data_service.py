from data.owner import Owner
import datetime
from data.cages import Cage
from data.bookings import Booking
from data.snakes import Snake





def create_account(name:str,email:str):
	owner = Owner()
	owner.name = name
	owner.email = email
	
	owner.save()
	return owner
	


def find_account_by_email(email:str):	
	# owner = Owner.objects().filter(email=email).first()
	owner = Owner.objects(email=email).first()

	return owner



def register_cage(active_account:Owner,name,meters,
	is_carpeted,has_toys,allow_dangerous_snakes,price):
	cage = Cage()
	
	cage.name=name
	cage.price=price
	cage.square_meters=meters
	cage.is_carpeted=is_carpeted
	cage.has_toys=has_toys
	cage.allow_dangerous_snakes=allow_dangerous_snakes

	cage.save()

	account = find_account_by_email(active_account.email)
	account.cage_ids.append(cage.id)
	account.save()

	return cage



def find_cage_for_user(account:Owner):
	query = Cage.objects(id__in = account.cage_ids)
	cages = list(query)

	return cages
	

def add_date(cage:Cage,start_date:datetime.datetime,days:int):
	booking = Booking()

	booking.check_in_date = start_date
	booking.check_out_date = start_date + datetime.timedelta(days=days)

	cage = Cage.objects(id = cage.id).first()
	cage.bookings.append(booking)
	cage.save()

	return cage


def add_snake(account:Owner,nme,spcs,len,is_ven):
	snake = Snake()
		
	snake.species = spcs
	snake.length = len
	snake.name = nme
	snake.is_venomous = is_ven
	snake.save()

	owner = find_account_by_email(account.email)
	owner.snake_ids.append(snake.id)
	owner.save()

	return snake



def get_snakes_for_user(account:Owner):
	query = Snake.objects(id__in = account.snake_ids).all()
	snakes = list(query)

	return snakes



def get_available_cages(checkin:datetime.datetime,checkout:datetime.datetime,snake:Snake):
	min_size = snake.length/4

	query = Cage.objects()\
		.filter(square_meters__gte = min_size)	\
		.filter(bookings__check_in_date__lte = checkin)	\
		.filter(bookings__check_out_date__gte = checkout)

	if snake.is_venomous:
		query=query.filter(allow_dangerous_snakes=True)

	cages = query.order_by('price','-square_meters')
	final_cages = []

	for c in cages:
		for b in c.bookings:
			if b.check_in_date<= checkin and b.check_out_date >= checkout and b.guest_owner_id == None:
				final_cages.append(c)


	return final_cages

def book_cage(account: Owner, snake:Snake, cage:Cage, checkin:datetime.datetime, checkout:datetime.datetime):
	booking = None
	for b in cage.bookings:
			if b.check_in_date<= checkin and b.check_out_date >= checkout and b.guest_owner_id == None:
				booking = b

	booking.guest_owner_id = account.id
	booking.guest_snake_id = snake.id
	booking.booked_date = datetime.datetime.now()

	cage.save()



def get_bookings_for_user(active_account: Owner):
	account = find_account_by_email(active_account.email)
	booked_cages = Cage.objects.filter(bookings__guest_owner_id = account.id )	\
		.only('bookings','name')

	def cage_to_booking(cage,booking):
		booking.cage = booking


	bookings = [
		cage_to_booking(cage,booking)
		for cage in booked_cages 
		for booking in cage.bookings
		if booking.guest_owner_id == account.id
	]