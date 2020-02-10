import mongoengine
import datetime


class Booking(mongoengine.EmbeddedDocument):
	guest_owner_id = mongoengine.ObjectIdField()
	guest_snake_id = mongoengine.ObjectIdField()

	booked_date = mongoengine.DateTimeField()
	check_in_date = mongoengine.DateTimeField(required=True)
	check_out_date = mongoengine.DateTimeField(required=True)

	rating = mongoengine.StringField()
	review = mongoengine.IntField(default=0)

	@property
	def duration_in_days(self):
		dt=self.check_out_date-self.check_in_date
		return dt.days
	