# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import celery
from celery import app as CELERY_APP
import json
from celery.result import AsyncResult
from django.http import HttpResponse,HttpResponseRedirect
from django.core.serializers import serialize
from django_celery_results.models import TaskResult
from django.views.decorators.csrf import csrf_exempt

def task_progress(request):
    '''
    Função que que serve o ajax para retornar midias que estão no processamento ou finalizaram
    '''
    i = CELERY_APP.control.inspect()
    MediaIDs = []
    task_app_id = []
    response_data = []

    for arrayOfDicts in i.active().values():
        for d in arrayOfDicts:
            task_name = d['name']
            MediaIDs.append(d['args'].replace(")","").replace("(","").replace("'","").split()[-1])
            task_app_id.append(d['id'])

    for i,data in enumerate(task_app_id):
        result = AsyncResult(data)
        data_db = TaskResult.objects.filter(task_id=data)
        if data_db.exists():
            if data_db.first().status == 'FAILURE':
                response_data.append({ 
                    'task_id' : data,
                    'state': 'FAILURE',
                    'details': repr(result.info),
                    'mediaid': MediaIDs[i]
                    
                })
            else:
                response_data.append({ 
                    'task_id' : data,
                    'state': data_db.first().status,
                    'details': repr(result.info),
                    'mediaid': MediaIDs[i]
                    
                })
        else:
            response_data.append({ 
                'task_id' : data,
                'state': result.state,
                'details': repr(result.info),
                'mediaid': MediaIDs[i]  
            })
        
    return HttpResponse(json.dumps(response_data), content_type='application/json')



@csrf_exempt
def celery_fail(request):
    '''
    Função que que serve o ajax para retornar midias que falharam no processamento
    '''
    data_tmp = {}
    
    if request.POST:
        ajax_data = request.POST.getlist('data_id[]')
        data_db = TaskResult.objects.all().order_by('date_done')
        del ajax_data[-1] #retirando csftoken

        if data_db.exists():
            for data in data_db:
                mediaID = data.task_args.replace(")","").replace("(","").replace("'","").replace("]","").split()[-1]
                if mediaID in ajax_data:
                    if mediaID in data_tmp:
                        if data.date_done > data_tmp.get(mediaID)[0]:
                            data_tmp[mediaID] = [data.date_done, data.status]
                    else:
                        data_tmp[mediaID] = [data.date_done, data.status]
                else:
                    continue
        
        for value in data_tmp:
            data_tmp[value][0] = data_tmp[value][0].date()
        
    return HttpResponse(json.dumps(data_tmp, default = myconverter), content_type='application/json')

import datetime
def myconverter(o):
    if isinstance(o, datetime.date):
        return o.__str__()

from django.shortcuts import render,Http404
import urllib2

def celery_result(request):
    '''
    Função que que serve a lista de processamentos via flower
    '''

    req = urllib2.Request("http://localhost:5555/api/tasks")
    opener = urllib2.build_opener()
    f = opener.open(req)
    json_ui = json.loads(f.read())
    print "[monitor_celery] json_ui",dict_name

    for uuid,data in json_ui.items():
        data['desc'] = dict_name[data["name"]]
        data['received'] = datetime.datetime.fromtimestamp(data['received'])
        data['started'] = datetime.datetime.fromtimestamp(data['started'])

    return render(request, 'html/task.html', {'json_bat': json_ui})