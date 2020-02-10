import mongoengine
import datetime

def global_init():
	mongoengine.register_connection(alias='core', name='snake_bnb')