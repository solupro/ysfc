# coding: utf-8
import time

from django.shortcuts import render_to_response, redirect
from django.contrib import messages
from django.template import RequestContext
from django.conf import settings

from djclub.app.models import Node, Nodeclass, Topic
from djclub.app.forms import NodeForm

def add(request):
	post = {}

	if request.method == 'POST':
		post = request.POST.copy()
		form = NodeForm(post)
		form.node = None
		if not form.is_valid():
			for field in form.errors:
				messages.info(request, form[field].errors.as_text())
		elif getattr(request.session.get('user', ''), 'id', 0) != 1:
			messages.info(request, 'You are not the manager!')
		else:
			cd = form.cleaned_data

			nodeclass = None
			try:
				nodeclass = Nodeclass.objects.get(name=cd['nodeclass'])
			except Exception, e:
				print e
				nodeclass = Nodeclass(name=cd['nodeclass'])
				nodeclass.save()

			node = Node(name=cd['name'], site=cd['site'], description=cd['description'], \
						status=cd['status'], nodeclass=nodeclass, date=int(time.time()))
			node.save()
			messages.info(request, '节点创建成功！')
			return redirect('/')

	form = NodeForm(initial={
		'name' : request.POST.get('name', ''),
		'site' : request.POST.get('site', ''),
		'description': request.POST.get('description', ''),
		'status' : request.POST.get('status', 1),
		'nodeclass' : request.POST.get('nodeclass', ''),
	})
	return render_to_response('node_add.html',{'form':form}, context_instance=RequestContext(request))


def show(request, node_site='', page=1):
	node = None
	try:
		node = Node.objects.get(site=node_site)
	except Exception, e:
		print e
		messages.info(request, 'The node does not exists!')
	if node:
		page = page if page >= 1 else 1
		s = (page - 1) * settings.PER_PAGE
		e = s + settings.PER_PAGE
		page_obj = Topic.objects.filter(node=node).order_by('-last_reply_date')[s:e]
		page_url = "node/%s/%s/" % (node_site, page)
		return render_to_response('node_index.html', locals(), context_instance=RequestContext(request))
	else:
		return redirect('/')

def edit(request, node_name=''):
	node = None
	post = {}

	if getattr(request.session['user'], 'id', 0) != 1:
		messages.info(request, 'You are not the manager!')
		return redirect('/')

	try:
		node = Node.objects.get(name=node_name)
	except Exception, e:
		print e
		messages.info(request, 'The node does not exists!')
		return redirect('/')

	if request.method == 'POST':
		post = request.POST.copy()
		form = NodeForm(post)
		form.node = node
		if not form.is_valid():
			for field in form.errors:
				messages.info(request, form[field].errors.as_text())
		elif getattr(request.session['user'], 'id', 0) != 1:
			messages.info(request, 'You are not the manager!')
		else:
			cd = form.cleaned_data

			nodeclass = None
			try:
				nodeclass = Nodeclass.objects.get(name=cd['nodeclass'])
			except Exception, e:
				print e
				nodeclass = Nodeclass(name=cd['nodeclass'])
				nodeclass.save()
			node.name = cd['name']
			node.site = cd['site']
			node.description = cd['description']
			node.status = cd['status']
			node.nodeclass = nodeclass
			node.date = int(time.time())

			node.save()
			messages.info(request, '节点更新成功！')
			return redirect('/')

	form = NodeForm(initial={
		'name' : request.POST.get('name', ''),
		'site' : request.POST.get('site', ''),
		'description': request.POST.get('description', ''),
		'status' : request.POST.get('status', 1),
		'nodeclass' : request.POST.get('nodeclass', ''),
	})
	return render_to_response('node_edit.html', locals(), context_instance=RequestContext(request))