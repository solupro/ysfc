from django.shortcuts import render_to_response
from django.template import RequestContext

from djclub.app.models import City

def show(request, name=''):
	users = {}
	city = {}
	try:
		city = City.objects.get(name=name)
		users = city.user_set.all()
	except Exception, e:
		print 'city.show:', e
	return render_to_response('city_view.html', {'users':users, 'city':city}, context_instance=RequestContext(request))


