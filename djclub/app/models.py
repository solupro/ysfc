# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class Bank(models.Model):
    time = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'djclub_bank'

class City(models.Model):
    name = models.CharField(unique=True, max_length=150, blank=True)
    site = models.CharField(unique=True, max_length=150, blank=True)
    description = models.TextField(blank=True)
    class Meta:
        db_table = u'djclub_city'

class User(models.Model):
    name = models.CharField(unique=True, max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    time = models.IntegerField(null=True, blank=True)
    timeswitch = models.IntegerField(null=True, blank=True, default=1)
    topswitch = models.IntegerField(null=True, blank=True, default=1)
    emailswitch = models.IntegerField(null=True, blank=True, default=1)
    timetop = models.IntegerField(null=True, blank=True)
    usercenter = models.CharField(unique=True, max_length=150, blank=True)
    status = models.IntegerField(null=True, blank=True)
    steam_id = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    website = models.TextField(blank=True)
    date = models.IntegerField(null=True, blank=True)
    city = models.ForeignKey(City, null=True, blank=True)
    class Meta:
        db_table = u'djclub_user'
        
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/member/%s" % self.name

class Nodeclass(models.Model):
    name = models.CharField(unique=True, max_length=150, blank=True)
    description = models.TextField(blank=True)
    status = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'djclub_nodeclass'

    def __unicode__(self):
        return self.name

class Node(models.Model):
    name = models.CharField(unique=True, max_length=150, blank=True)
    site = models.CharField(unique=True, max_length=150, blank=True)
    description = models.TextField(null=True, blank=True)
    nodeclass = models.ForeignKey(Nodeclass, null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    date = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'djclub_node'

    def __unicode__(self):
        return self.name

class Topic(models.Model):
    author = models.ForeignKey(User, null=True, blank=True)
    title = models.CharField(max_length=240, blank=True)
    text = models.TextField(blank=True)
    node = models.ForeignKey(Node, null=True, blank=True)
    vote = models.IntegerField(null=True, blank=True, default=0)
    report = models.IntegerField(null=True, blank=True)
    date = models.IntegerField(null=True, blank=True)
    last_reply_date = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'djclub_topic'

class Reads(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    topic = models.ForeignKey(Topic, null=True, blank=True)
    class Meta:
        db_table = u'djclub_reads'


class Votes(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    topic = models.ForeignKey(Topic, null=True, blank=True)
    class Meta:
        db_table = u'djclub_votes'

class Reply(models.Model):
    topic = models.ForeignKey(Topic, null=True, blank=True)
    author = models.ForeignKey(User, null=True, blank=True)
    text = models.TextField(blank=True)
    date = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'djclub_reply'

class Bill(models.Model):
    author = models.ForeignKey(User, null=True, blank=True)
    topic = models.ForeignKey(Topic, null=True, blank=True)
    reply = models.ForeignKey(Reply, null=True, blank=True)
    user_id = models.IntegerField(null=True, blank=True)
    time = models.IntegerField(null=True, blank=True)
    balance = models.IntegerField(null=True, blank=True)
    type = models.IntegerField(null=True, blank=True)
    date = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'djclub_bill'

class Favorites(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    topic = models.ForeignKey(Topic, null=True, blank=True)
    class Meta:
        db_table = u'djclub_favorites'


class Thanks(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    reply = models.ForeignKey(Reply, null=True, blank=True)
    class Meta:
        db_table = u'djclub_thanks'

class Notify(models.Model):
    author = models.ForeignKey(User, null=True, blank=True)
    status = models.IntegerField(null=True, blank=True, default=0)
    topic = models.ForeignKey(Topic, null=True, blank=True)
    reply = models.ForeignKey(Reply, null=True, blank=True)
    type = models.IntegerField(null=True, blank=True)
    date = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'djclub_notify'

class Overtime(models.Model):
    who = models.ForeignKey(User, null=True, blank=True)
    record_time = models.IntegerField(null=True, blank=True)
    remark = models.TextField(blank=True)

    class Meta:
        db_table = u'djclub_overtime'