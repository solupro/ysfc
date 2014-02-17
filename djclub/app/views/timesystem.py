# coding: utf-8
import time

from django.shortcuts import render_to_response, redirect
from django.contrib import messages
from django.template import RequestContext
from django.conf import settings
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from djclub.app.models import Bank, Bill

def bank(request):
	page_obj = {}
	bank = {}
	default_time = settings.USER_DEFAULT_TIME
	topic_delete = settings.TOPIC_DELETE
	topic_create = settings.TOPIC_CREATE
	inviter_time = settings.USER_INVITER_TIME
	gift_time = settings.USER_INVITER_TIME - settings.USER_DEFAULT_TIME

	bank = Bank.objects.get(id=1)
	if not bank:
		messages.info(requset, '时间规划局未初始化!')
		return redirect('/')

	bills = Bill.objects.filter(Q(type=1)|Q(type=2)|Q(type=7)|Q(type=8)).order_by('-date')
	page = request.GET.get('page', 1)
	paginator = Paginator(bills, settings.BANK_PAGE)
	page_obj = None
	try:
		page_obj = paginator.page(page)
	except PageNotAnInteger:
		page_obj = paginator.page(1)
	except EmptyPage:
		page_obj = paginator.page(paginator.num_pages)
	#print locals()
	return render_to_response('bank.html', locals(), context_instance=RequestContext(request))