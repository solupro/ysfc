# Create your views here.
from django.shortcuts import render_to_response
from djclub.app.models import *


def index(requset):
	nodeClasses = Nodeclass.objects.all()
	print nodeClasses[0]
	return render_to_response('index.html')

def show(requset):
	return render_to_response('index.html')