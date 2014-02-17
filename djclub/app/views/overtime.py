# coding: utf-8
import time, datetime

from django.shortcuts import render_to_response, redirect
from django.contrib import messages
from django.template import RequestContext
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from djclub.app.models import Node, Nodeclass, Topic, User, Reply, Favorites, Bank, Bill, Votes, Overtime
from djclub.app.forms import TopicForm, ReplyForm
from djclub.app.functions import getTimeZone, send_mail, AnimeParser, VoteParser, mycmp

def index(request):
	if not request.session.get('user'):
		messages.info(request, '登录后进行操作!')
		return redirect('login')
	ot = Overtime.objects.filter(who=request.session['user']).order_by('-record_time')

	page = request.GET.get('page', 1)
	paginator = Paginator(ot, settings.PER_PAGE)
	page_obj = None
	try:
		page_obj = paginator.page(page)
	except PageNotAnInteger:
		page_obj = paginator.page(1)
	except EmptyPage:
		page_obj = paginator.page(paginator.num_pages)
	return render_to_response('overtime.html', locals(), context_instance=RequestContext(request))

def animeTop(request):
	import urllib2, re
	from math import fsum

	index_page = r'http://www.dm123.cn/data/2013/201304'
	vote_page = r'http://www.dm123.cn/e/public/vote/?classid=2358&id='
	html = urllib2.urlopen(index_page).read()
	p = AnimeParser()
	p.parse(html)
	p.close()
	links = p.links
	rc = re.compile(r'.*/2013-\d{2}-\d{2}/(\d+).html')
	ids = []
	for link in links:
		values = rc.findall(link,re.I)
		if values:
			ids.extend(values)
	ids = list(set(ids))
	kv = {}
	for id in ids:
		html = urllib2.urlopen(vote_page + id).read()
		vp = VoteParser()
		vp.parse(html)
		vp.close()
		title = vp.title
		vs = vp.votes
		s = int(fsum(vs))
		vs.append(s)
		if title:
			kv[title] = vs
		vp = None
		#print kv
	kv = sorted(kv.items(), cmp=mycmp)
	print kv
	return render_to_response('animetop.html', locals(), context_instance=RequestContext(request))

def showdown(request):
	return render_to_response('showdown.html', locals(), context_instance=RequestContext(request))

def record(request):
	who = request.GET.get('who', 'solu')
	key = request.GET.get('key', '')
	remark = request.GET.get('remark', '')

	import hashlib
	mykey = hashlib.md5(settings.SECRET_KEY + who).hexdigest()

	if (key == mykey):
		user = None
		try:
			user = User.objects.get(name=who)
		except Exception, e:
			print e
			return redirect('/')
		
		ot = Overtime(who=user,record_time=int(time.time()), remark=remark)
		ot.save()
		
		#本月加班次数
		today = datetime.date.today()
		timeZone = getTimeZone(today)

		count = user.overtime_set.filter(record_time__gte=timeZone['st']) \
								 .filter(record_time__lte=timeZone['et']).count()

		#print count
		message = "%s年%s月%s日加班累计%s次。" % (timeZone['year'], timeZone['month'],today.day, count)
		send_mail('每月加班次数统计', message, user.email)
	return redirect('/')