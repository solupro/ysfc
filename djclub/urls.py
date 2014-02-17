from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

#topic
urlpatterns = patterns('djclub.app.views.topic',
    url(r'^$', 'index'),
    url(r'^add/topic/$', 'add', name='topicadd'),
    url(r'^topic/(?P<topic_id>[\d]+)/$', 'view', name="topicview"),
    url(r'^topic/(?P<topic_id>[\d]+)/edit/$', 'edit', name="topicedit"),
    url(r'^topic/(?P<topic_id>[\d]+)/fav/$', 'fav', name="topicfav"),
    url(r'^topic/(?P<topic_id>[\d]+)/delete/$', 'delete', name="topicdel"),
    url(r'^topic/(?P<topic_id>[\d]+)/vote/$', 'vote', name="topicvote"),
)

#node
urlpatterns += patterns('djclub.app.views.node',
	url(r'^add/node/$', 'add', name='nodeadd'),
    url(r'^node/(?P<node_site>[\w\d\-]+)/?$', 'show'),
    url(r'^node/(?P<node_site>[\w\d\-]+)/(?P<page>[\d]+)/?$', 'show'),
    url(r'^node/edit/(?P<node_name>[\w\d\-]+)/$', 'edit', name='nodedit'),
)

#account
urlpatterns += patterns('djclub.app.views.account',
    url(r'^account/login/$', 'login', name='login'),
    url(r'^account/logout/$', 'logout', name='logout'),
    url(r'^account/register/$', 'register', name='register'),
    url(r'^account/register/~(?P<inviter>[\w\d]+)/?$', 'register', name='register'),
    url(r'^member/(?P<user_name>[\w\-\d]+)/?$', 'usercenter'),
    url(r'^settings/?$', 'setting'),
    url(r'^users/?$', 'users', name='users'),
    url(r'^top/?$', 'top', name='top'),
    url(r'^favorites/$', 'favorites', name='favorites'),
    url(r'^times/$', 'times', name='times'),
    url(r'^notification/$', 'notify', name='notification'),
    url(r'^notification/(?P<notify_id>[\d]+)/delete/$', 'notify_del', name='notify_del'),
)

#city
urlpatterns += patterns('djclub.app.views.city',
	url(r'^city/([\w\-\d]+)/?$', 'show'),
)

#timesystem
urlpatterns += patterns('djclub.app.views.timesystem',
	url(r'^bank/?$', 'bank'),
)

#reply
urlpatterns += patterns('djclub.app.views.reply',
    url(r'^topic/(?P<topic_id>[\d]+)/reply/$', 'reply_add', name='replyadd'),
    url(r'^reply/(?P<reply_id>[\d]+)/thanks/$', 'thanks', name='thanks'),
    url(r'^reply/(?P<reply_id>[\d]+)/delete/$', 'reply_del', name='replydel'),
    url(r'^reply/(?P<reply_id>[\d]+)/edit/$', 'reply_edit', name='replyedit'),
)

#overtime
urlpatterns += patterns('djclub.app.views.overtime',
    url(r'^ot/add/', 'record'),
    url(r'^ot/show/', 'index'),

    url(r'^animetop/', 'animeTop'),
    url(r'^showdown/', 'showdown'),
)