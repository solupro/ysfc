# coding: utf-8
from django import forms

from djclub.app.models import User, Node, Favorites, Reply, Votes, Reads, Thanks
from djclub.app.functions import check_password as cp

class LoginForm(forms.Form):
	username = forms.CharField(max_length=30, min_length=4)
	password = forms.CharField(widget=forms.PasswordInput(render_value=True), min_length=6)

	def check_password(self):
		username = self.cleaned_data['username']
		password = self.cleaned_data['password']
		try:
			if '@' in username:
				user = User.objects.get(email=username)
			else:
				user = User.objects.get(name=username)
			self.user = user
			self.user.favorites = []
			for fav in Favorites.objects.filter(user=user):
				self.user.favorites.append(int(fav.topic_id))
			#self.user.reads = []
			#for read in Reads.objects.filter(user=user):
			#	self.user.reads.append(int(read.topic_id))
			self.user.votes = []
			for vote in  Votes.objects.filter(user=user):
				self.user.votes.append(int(vote.topic_id))
			self.user.thanks = []
			for thank in Thanks.objects.filter(user=user):
				self.user.thanks.append(int(thank.reply_id))
			return cp(password, user.password)
		except Exception, e:
			print e
			raise User.DoesNotExist("The username does not exists!")
			

class RegisterForm(forms.Form):
	username = forms.CharField(max_length=30, min_length=4)
	email = forms.EmailField(max_length=75)
	password1 = forms.CharField(widget=forms.PasswordInput(render_value=True), min_length=6)
	password2 = forms.CharField(widget=forms.PasswordInput(render_value=True), min_length=6)

	def clean_password2(self):
		password1 = self.cleaned_data['password1']
		password2 = self.cleaned_data['password2']

		if password1 != password2:
			raise forms.ValidationError("The two passwords you typed do not match")
		return password2

	def clean_username(self):
		username = self.cleaned_data['username']
		try:
			user = User.objects.get(name=username)
		except Exception, e:
			return username
		if user:
			raise forms.ValidationError("The username already exists!")
		
	def clean_email(self):
		email = self.cleaned_data['email']
		try:
			user = User.objects.get(email=email)
		except Exception, e:
			return email
		if user:
			raise forms.ValidationError("The email already exists!")


class SettingForm(forms.Form):
	EXTRA_CHOICES_OPENCLOSE = [('1', '开'),('0', '关'),]
	EXTRA_CHOICES_YESNO = [('1', '是'),('0', '否'),]

	username = forms.CharField(max_length=30, min_length=4)
	email = forms.EmailField(max_length=75)
	emailswitch = forms.ChoiceField(widget=forms.Select(attrs={'class':'span3'}), choices=EXTRA_CHOICES_OPENCLOSE)
	timeswitch = forms.ChoiceField(widget=forms.Select(attrs={'class':'span3'}), choices=EXTRA_CHOICES_OPENCLOSE)
	topswitch = forms.ChoiceField(widget=forms.Select(attrs={'class':'span3'}), choices=EXTRA_CHOICES_YESNO)
	website = forms.URLField(required=False)
	description = forms.CharField(widget=forms.Textarea(attrs={'class':'span3'}), required=False)
	city = forms.CharField(max_length=100, min_length=2, required=False)
	password = forms.CharField(widget=forms.PasswordInput(render_value=True), min_length=6, required=False)

	def clean_username(self):
		username = self.cleaned_data['username']
		user = None
		if username == getattr(self.user, 'name', ''):
			return username
		try:
			user = User.objects.get(name=username)
		except Exception, e:
			return username
		if user:
			raise forms.ValidationError("The username already exists!")
		
	def clean_email(self):
		email = self.cleaned_data['email']
		user = None
		if email == getattr(self.user, 'email', ''):
			return email
		try:
			user = User.objects.get(email=email)
		except Exception, e:
			return email
		if user:
			raise forms.ValidationError("The email already exists!")

	def check_password(self):
		username = self.cleaned_data['username']
		password = self.cleaned_data['password']
		try:
			user = User.objects.get(name=username)
			return cp(password, user.password)
		except Exception, e:
			raise User.DoesNotExist("The username does not exists!")


class NodeForm(forms.Form):
	EXTRA_CHOICES_DISPLAYHIDDEN = [('1', '显示'), ('0', '隐藏'),]

	name = forms.CharField(max_length=50)
	site = forms.CharField(max_length=50)
	description = forms.CharField(widget=forms.Textarea(attrs={'class':'span3'}), required=False)
	nodeclass =forms.CharField(max_length=50)
	status = forms.ChoiceField(widget=forms.Select(attrs={'class':'span3'}), choices=EXTRA_CHOICES_DISPLAYHIDDEN)
	site = forms.CharField(max_length=50)

	def clean_name(self):
		name = self.cleaned_data['name']
		node = None
		if name == getattr(self.node, 'name', ''):
			return name
		try:
			node = Node.objects.get(name=name)
		except Exception, e:
			return name
		if node:
			raise forms.ValidationError("The node's name already exists!")

	def clean_site(self):
		site = self.cleaned_data['site']
		nodesite = None
		if site == getattr(self.node, 'site', ''):
			return site
		try:
			nodesite = Node.objects.get(site=site)
		except Exception, e:
			return site
		if nodesite:
			raise forms.ValidationError("The node's site already exists!")


class TopicForm(forms.Form):
	title = forms.CharField(max_length=240, min_length=2)
	text = forms.CharField(widget=forms.Textarea(attrs={'class':'span3', 'rows':'20', 'cols':'40'}))
	nodename = forms.ChoiceField(widget=forms.Select(attrs={'class':'span3'}), choices=[])

	def __init__(self, *args, **kwargs):
		super(TopicForm, self).__init__(*args, **kwargs)
		choices_nodes = [('0', '选择节点'),]
		nodes = Node.objects.all()
		for n in nodes:
			choices_nodes.append((str(n.id), n.name))
		self.fields['nodename'].choices = choices_nodes
		#print choices_nodes

	def clean_nodename(self):
		nodename = self.cleaned_data['nodename']
		if int(nodename) == 0:
			raise forms.ValidationError("必须选择节点")
		return nodename

class ReplyForm(forms.Form):
	content = forms.CharField(widget=forms.Textarea(attrs={'rows':'7', 'cols':'40'}))