# coding:utf-8
import os
import ConfigParser
from datetime import datetime

from django.db.models import Q
from django.http import HttpResponse
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from connect import BASE_DIR
from jlog.models import Log
from jumpserver.views import pages
from juser.models import User, DEPT
from jumpserver.api import get_user_dept, is_super_user, is_group_admin, is_common_user

CONF = ConfigParser.ConfigParser()
CONF.read('%s/jumpserver.conf' % BASE_DIR)


def log_list_online(request):
    header_title, path1, path2 = u'查看日志', u'查看日志', u'在线用户'
    keyword = request.GET.get('keyword')
    web_socket_host = CONF.get('websocket', 'web_socket_host')
    dept_id = get_user_dept(request)
    dept_name = DEPT.objects.get(id=dept_id).name
    user_id = request.session.get('user_id')
    username = User.objects.get(id=user_id).username

    if is_super_user(request):
        if keyword:
            posts = Log.objects.filter(Q(user__contains=keyword) | Q(host__contains=keyword)) \
                .filter(is_finished=0).order_by('-start_time')
        else:
            posts = Log.objects.filter(is_finished=0).order_by('-start_time')
        contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)

    elif is_group_admin(request):
        if keyword:
            posts = Log.objects.filter(Q(user__contains=keyword) | Q(host__contains=keyword)) \
                .filter(is_finished=0).filter(dept_name=dept_name).order_by('-start_time')
        else:
            posts = Log.objects.filter(is_finished=0).filter(dept_name=dept_name).order_by('-start_time')
        contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)

    elif is_common_user(request):
        if keyword:
            posts = Log.objects.filter(user=username).filter(Q(user__contains=keyword) | Q(host__contains=keyword))\
                .filter(is_finished=0).order_by('-start_time')
        else:
            posts = Log.objects.filter(is_finished=0).filter(user=username).order_by('-start_time')
        contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)

    return render_to_response('jlog/log_online.html', locals(), context_instance=RequestContext(request))


def log_list_offline(request):
    header_title, path1, path2 = u'查看日志', u'查看日志', u'历史记录'
    keyword = request.GET.get('keyword')
    web_socket_host = CONF.get('websocket', 'web_socket_host')
    dept_id = get_user_dept(request)
    dept_name = DEPT.objects.get(id=dept_id).name
    user_id = request.session.get('user_id')
    username = User.objects.get(id=user_id).username
    if is_super_user(request):
        if keyword:
            posts = Log.objects.filter(Q(user__contains=keyword) | Q(host__contains=keyword)) \
                .filter(is_finished=1).order_by('-start_time')
        else:
            posts = Log.objects.filter(is_finished=1).order_by('-start_time')
        contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)

    elif is_group_admin(request):
        if keyword:
            posts = Log.objects.filter(Q(user__contains=keyword) | Q(host__contains=keyword)) \
                .filter(is_finished=1).filter(dept_name=dept_name).order_by('-start_time')
        else:
            posts = Log.objects.filter(is_finished=1).filter(dept_name=dept_name).order_by('-start_time')
        contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)

    elif is_common_user(request):
        if keyword:
            posts = Log.objects.filter(user=username).filter(Q(user__contains=keyword) | Q(host__contains=keyword))\
                .filter(is_finished=1).order_by('-start_time')
        else:
            posts = Log.objects.filter(is_finished=1).filter(user=username).order_by('-start_time')
        contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)
    return render_to_response('jlog/log_offline.html', locals(), context_instance=RequestContext(request))


def log_kill(request, offset):
    pid = offset
    if pid:
        os.kill(int(pid), 9)
        Log.objects.filter(pid=pid).update(is_finished=1, end_time=datetime.now())
        return HttpResponseRedirect('jlog/log_offline.html', locals(), context_instance=RequestContext(request))


def log_history(request):
    if request.method == 'GET':
        id = request.GET.get('id', 0)
        log = Log.objects.get(id=int(id))
        if log:
            log_his = "%s.his" % log.log_path
            if os.path.isfile(log_his):
                f = open(log_his)
                content = f.read()
                return HttpResponse(content)


def log_search(request):
    keyword = request.GET.get('keyword')
    env = request.GET.get('env')
    dept_id = get_user_dept(request)
    dept_name = DEPT.objects.get(id=dept_id).name
    user_id = request.session.get('user_id')
    username = User.objects.get(id=user_id).username
    if is_super_user(request):
        if env == 'online':
            posts = contact_list = Log.objects.filter(Q(user__contains=keyword) | Q(host__contains=keyword)) \
                .filter(is_finished=0).order_by('-start_time')
        elif env == 'offline':
            posts = contact_list = Log.objects.filter(Q(user__contains=keyword) | Q(host__contains=keyword)) \
                .filter(is_finished=1).order_by('-start_time')
        contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)

    elif is_group_admin(request):
        if env == 'online':
            posts = contact_list = Log.objects.filter(Q(user__contains=keyword) | Q(host__contains=keyword)) \
                .filter(is_finished=0).filter(dept_name=dept_name).order_by('-start_time')
        elif env == 'offline':
            posts = contact_list = Log.objects.filter(Q(user__contains=keyword) | Q(host__contains=keyword)) \
                .filter(is_finished=1).filter(dept_name=dept_name).order_by('-start_time')
        contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)

    elif is_common_user(request):
        if env == 'online':
            posts = contact_list = Log.objects.filter(Q(user__contains=keyword) | Q(host__contains=keyword)) \
                .filter(is_finished=0).filter(user=username).order_by('-start_time')
        elif env == 'offline':
            posts = contact_list = Log.objects.filter(Q(user__contains=keyword) | Q(host__contains=keyword)) \
                .filter(is_finished=1).filter(user=username).order_by('-start_time')
        contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)
    return render_to_response('jlog/log_search.html', locals(), context_instance=RequestContext(request))
