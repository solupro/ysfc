# coding: utf-8
import time, copy

from django.shortcuts import render_to_response, redirect
from django.contrib import messages
from django.template import RequestContext
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from djclub.app.models import User, Bank, Bill, Topic, City, Favorites, Notify
from djclub.app.forms import RegisterForm, LoginForm, SettingForm
from djclub.app.functions import set_password


def login(request):
	if request.method == 'POST':
		post = request.POST.copy()
		form = LoginForm(post)
		if not form.is_valid():
			for field in form.errors:
				messages.info(request, form[field].errors.as_text())
		else:
			try:
				if form.check_password():
					messages.info(request, 'Successful user login!')
					request.session['user'] = form.user
					return redirect('/')
				else:
					messages.info(request, 'Username or password error!')
			except Exception, e:
				messages.info(request, e)

	form = LoginForm(initial={
		'username' : request.POST.get('username', ''),
		'password' : '',
	})
	return render_to_response('login.html', {'form':form}, context_instance=RequestContext(request))


def register(request, inviter = ''):
	#print inviter
	if request.method == 'POST':
		post = request.POST.copy()
		inviter = post.get('inviter', '')
		del post['inviter']
		form = RegisterForm(post)
		if not form.is_valid():
			for field in form.errors:
				messages.info(request, form[field].errors.as_text())
		else:
			cd = form.cleaned_data
			#print set_password(cd['password1'])
			user_time = settings.USER_INVITER_TIME if inviter else settings.USER_DEFAULT_TIME
			user = User(name=cd['username'], usercenter=cd['username'], \
						email=cd['email'], password=set_password(cd['password1']), time=user_time, date=int(time.time()))
			user.save()

			#init bank
			if Bank.objects.all().count() == 0:
				b = Bank(time=settings.BANK_INIT_TIME)
				b.save()
			bank = Bank.objects.get(id=1)
			gift_time = settings.USER_INVITER_TIME - settings.USER_DEFAULT_TIME
			giver = None
			try:
				giver = User.objects.get(name=inviter)
			except Exception, e:
				print e
			if giver:
				giver.time += gift_time
				giver.save()
				bank.time -= settings.USER_DEFAULT_TIME + gift_time
				userBill = Bill(author=user,time=settings.USER_INVITER_TIME,type=7,balance=user.time,date=int(time.time()),user_id=giver.id)
				giverBill = Bill(author=giver,time=gift_time,type=8,balance=giver.time,date=int(time.time()),user_id=user.id)
				giverBill.save()
			else:
				bank.time -= settings.USER_DEFAULT_TIME
				userBill = Bill(author=user,time=settings.USER_DEFAULT_TIME,type=1,balance=user.time,date=int(time.time()))	
			userBill.save()
			bank.save()

			messages.info(request, 'You have successfully registered!')
			return redirect(login)

	form = RegisterForm(initial={
			'username' : request.POST.get('username', ''),
			'email' : request.POST.get('email', ''),
		})	
	return render_to_response('register.html', {'form':form, 'inviter':inviter}, context_instance=RequestContext(request))


def logout(request):
	if request.session.get('user', None):
		del request.session['user']
		messages.info(request, 'You have logout!')
	return redirect('/')


def usercenter(request, user_name=''):
	#print 'usercenter.user_name:', user_name
	user = None
	try:
		user = User.objects.get(name=user_name)
	except Exception, e:
		print 'usercenter:', e
		messages.info(request, 'The username does not exists!')
	if user:	
		topics = Topic.objects.filter(author=user).order_by('-last_reply_date')
		page = request.GET.get('page', 1)
		paginator = Paginator(topics, settings.PER_PAGE)
		page_obj = None
		try:
			page_obj = paginator.page(page)
		except PageNotAnInteger:
			page_obj = paginator.page(1)
		except EmptyPage:
			page_obj = paginator.page(paginator.num_pages)
		return render_to_response('usercenter.html', {'user':user, 'page_obj':page_obj}, context_instance=RequestContext(request))
	else:	
		return redirect('/')


def setting(request):
	user = request.session.get('user', '')
	if not user:
		return redirect('/')
	getint = lambda field : getattr(user, field, '0') if getattr(user, field, '0') else '0'
	form = SettingForm(initial={
		'username' : getattr(user, 'name', ''),
		'email' : getattr(user, 'email', ''),
		'emailswitch': getint('emailswitch'),
		'timeswitch' : getint('timeswitch'),
		'topswitch' : getint('topswitch'),
		'website' : getattr(user, 'website', ''),
		'description' : getattr(user, 'description', ''),
		'city' : getattr(getattr(user, 'city', {}), 'name', '')
	})

	if request.method == 'POST':
		del form
		post = request.POST.copy()
		form = SettingForm(post)
		form.user = user
		if not form.is_valid():
			print 'error'
			for field in form.errors:
				messages.info(request, form[field].errors.as_text())
			return redirect(setting)
		try:
			if form.check_password():
				cd = form.cleaned_data

				user.name = cd['username']
				user.email = cd['email']
				user.emailswitch = cd['emailswitch']
				user.timeswitch = cd['timeswitch']
				user.topswitch = cd['topswitch']
				user.website = cd['website']
				user.description = cd['description']
	
				if cd['city']:
					city = None
					try:
						city = City.objects.get(name=cd['city'])
					except Exception, e:
						print e
					if not city:
						city = City(name=cd['city'])
						city.save()
					user.city = city

				user.save()
				messages.info(request, '个人资料更新成功!')
			else:
				messages.info(request, '密码错误，更新失败!')
		except Exception, e:
			messages.info(request, e)

	return render_to_response('setting.html', {'form':form}, context_instance=RequestContext(request))


def users(request):
	users = User.objects.all().order_by('-id')[:50]
	return render_to_response('users.html',{'users':users}, context_instance=RequestContext(request))


def top(request):
	users = User.objects.filter(topswitch=1).order_by('-time')[:20]
	return render_to_response('top.html',{'users':users}, context_instance=RequestContext(request))

def favorites(request):
	if not request.session.get('user'):
		messages.info(request, '登录后进行操作!')
		return redirect('login')

	favs = Favorites.objects.filter(user=request.session['user']).order_by('-id')
	page = request.GET.get('page', 1)
	paginator = Paginator(favs, settings.PER_PAGE)
	page_obj = None
	try:
		page_obj = paginator.page(page)
	except PageNotAnInteger:
		page_obj = paginator.page(1)
	except EmptyPage:
		page_obj = paginator.page(paginator.num_pages)
	return render_to_response('favorites.html', locals(), context_instance=RequestContext(request))

def times(request):
	if not request.session.get('user'):
		messages.info(request, '登录后进行操作!')
		return redirect('login')
	bill = Bill.objects.filter(author=request.session['user']).order_by('-date')
	page = request.GET.get('page', 1)
	paginator = Paginator(bill, settings.TIMES_PAGE)
	page_obj = None
	try:
		page_obj = paginator.page(page)
	except PageNotAnInteger:
		page_obj = paginator.page(1)
	except EmptyPage:
		page_obj = paginator.page(paginator.num_pages)
	return render_to_response('times.html', locals(), context_instance=RequestContext(request))

def notify(request):
	user = request.session.get('user', '')
	if not user:
		return redirect('/')
	reads = Notify.objects.filter(author=user, status=1).order_by('-date')
	r = copy.copy(reads)

	page = request.GET.get('page', 1)
	paginator = Paginator(r, settings.NOTIFY_PAGE)
	page_obj = None
	try:
		page_obj = paginator.page(page)
	except PageNotAnInteger:
		page_obj = paginator.page(1)
	except EmptyPage:
		page_obj = paginator.page(paginator.num_pages)

	unreads = Notify.objects.filter(author=user, status=0).order_by('-date')
	for un in unreads:
		un.status = 1
		un.save()
	return render_to_response('notifications.html', locals(), context_instance=RequestContext(request))

def notify_del(request, notify_id=0):
	user = request.session.get('user', '')
	notify = None
	try:
		notify = Notify.objects.get(id=notify_id)
	except Exception, e:
		print e
	if not user or not notify:
		return redirect('/')

	notify.delete()
	messages.info(request, '消息删除成功！')
	return redirect('notification')