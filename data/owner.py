import mongoengine
import datetime

class Owner(mongoengine.Document):
	registered_date = mongoengine.DateTimeField(defaut=datetime.datetime.now)

	name=mongoengine.StringField(required=True)
	email=mongoengine.EmailField(required=True)

	snake_ids=mongoengine.ListField()
	cage_ids=mongoengine.ListField()

	meta = {
	    'db_alias':'core',
	    'collection':'owners'
	}