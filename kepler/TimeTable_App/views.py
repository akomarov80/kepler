from django.db.models.functions import NullIf
from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaultfilters import title
from django.views.generic import ListView, DetailView, CreateView
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponse

import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import seaborn as sns

from .models import *

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from deap import base
from deap import creator
from deap import tools

import random
import TimeTable_App.ttable_calc


def plot_test(request):
    func = [0, 1, 2, 3, 4, 5]

    sns.set_style("whitegrid")
    plt.plot(func, color='red')
    # делаешь графики
    plt.draw()
    response = HttpResponse(content_type="image/jpeg")
    plt.savefig(response, format="png")
    plt.clf()
    return response


def tt_calc(request):
    subjects = Subjects.objects.all()
    teachers = Teachers.objects.all()
    classrooms = Classrooms.objects.all()

    group_number_str = '1'
    if request.method == 'POST':
        group_number_str = request.POST.get('groups_number')
        print(group_number_str)

    teachers_num   = len(teachers)
    classrooms_num = len(classrooms)
    days_num       = 5


    if group_number_str =='1':   # страховка от ложного запуска ttable_calc
        message = 'group number is trivial'
        return render(request, 'Test.html',
                  {'teachers': teachers, 'subjects': subjects, 'classrooms': classrooms,
                   'message': message,
                   'title': 'Автоматическое составление расписаний (Другова О.А.)'})

    timeslots_num, groups_ttable = TimeTable_App.ttable_calc.main(int(group_number_str))

    # # test
    # object = TimeTable_App.ttable_calc.main(int(group_number_str))
    # print('*** ',object)
    # timeslots_num = 5
    # groups_ttable = {'gr1':[1, 2, 3], 'gr2':[1, 2, 3], 'gr3':[1, 2, 3]}


    groups = []
    for k in range(int(group_number_str)):
        groups.append(k + 1)

    timeslots = []
    for k in range (timeslots_num):
        timeslots.append(k+1)

    days_of_the_week = []
    for k in range (days_num):
        days_of_the_week.append(k+1)




    shift_per_lesson = classrooms_num*teachers_num
    shift_per_day = timeslots_num*shift_per_lesson
    # deviding array for groups time table (per lessons)
    ttable_array   = []
    for item in groups_ttable.values():
        # print(len(item))
        one_group_ttb=[]
        for i in range(0, len(item), shift_per_day):
            for j in range(i, i+shift_per_day, shift_per_lesson):
                # print('\t'+str(len(item[j:j+shift_per_lesson])))
                one_group_ttb.append(item[j:j+shift_per_lesson])
            # print('111>>:', len(one_group_ttb))
        # print('111E>>:', len(one_group_ttb))
        ttable_array.append(one_group_ttb)
        # print('222>>:', len(ttable_array))

    # Making strings for time table
    ttable_strings = []
    for i in range(len(ttable_array)):             # i == group
        one_group_ttb_strings=[]
        for j in range(len(ttable_array[i])):      # j == time slot
            for cN in range(classrooms_num):
                flag = 0
                for tN in range(teachers_num):
                    SubjID = ttable_array[i][j][cN*teachers_num+tN]
                    # print(cN*teachers_num+tN)
                    # print(ttable_array[i][j])
                    # print(SubjID)
                    if SubjID==0:
                        one_group_ttb_strings.append('gr #'+str(i+1)+' lesson (None):')
                        flag = 1
                        break
                    elif SubjID !=0 and SubjID<len(subjects):
                        one_group_ttb_strings.append('gr #'+str(i+1)+' lesson (lecture):'+ str(subjects[SubjID].title)+'; teacher:'+ teachers[tN].name + '; classroom:'+str(classrooms[cN].number))
                        # print(one_group_ttb_strings[-1])
                        flag = 1
                        break
                    elif SubjID !=0 and SubjID<2*len(subjects):
                        one_group_ttb_strings.append('gr #'+str(i+1)+' lesson (studies):'+ str(subjects[SubjID-len(subjects)].title)+'; teacher:'+ teachers[tN].name + '; classroom:'+str(classrooms[cN].number))
                        # print(one_group_ttb_strings[-1])
                        flag = 1
                        break
                    elif SubjID !=0 and SubjID<3*len(subjects):
                        one_group_ttb_strings.append('gr #'+str(i+1)+' lesson (prakt. work):' + str(subjects[SubjID-2*len(subjects)].title) + '; teacher:' + teachers[tN].name + '; classroom:' + str(classrooms[cN].number))
                        # print(one_group_ttb_strings[-1])
                        flag = 1
                        break
                if flag !=0:
                    break
        # print('333>> ', len(one_group_ttb_strings))
        ttable_strings.append(one_group_ttb_strings)
    # print('444>> ', len(ttable_strings))
    adapted_ttable=[]

    for i in range(len(ttable_strings)):
        adapted_ttable_group=[]
        for j in range(len(days_of_the_week)):
            lesson_in_day = []
            for k in range(j,len(ttable_strings[i]),timeslots_num):
                # print(ttable_strings[i][k])
                lesson_in_day.append(ttable_strings[i][k])
            adapted_ttable_group.append(lesson_in_day)
        # print(' adapted_ttable_group ')
        # print(adapted_ttable_group)
        adapted_ttable.append(adapted_ttable_group)

    # print('html_test')
    # for gr_week_ttable in adapted_ttable:
    #     for gr_day_ttable in gr_week_ttable:
    #         for lesson in gr_day_ttable:
    #             print(lesson)


    #time.sleep(5) # тестовое замедление
    message = 'calc is over'
    return render(request, 'Calculation.html',
                  {'teachers': teachers, 'subjects': subjects, 'classrooms': classrooms,
                   'groups': groups, 'timeslots': timeslots, 'days_of_the_week': days_of_the_week,
                   'ttable_strings': ttable_strings, 'adapted_ttable': adapted_ttable, 'message': message,
                   'title': 'Автоматическое составление расписаний (Другова О.А.) - результат'})

    # return render(request, 'Test.html',
    #               {'teachers': teachers, 'subjects': subjects, 'classrooms': classrooms, 'count': TimeTable_App.ttable_calc.main(),
    #                'title': 'Автоматическое составление расписаний (Другова О.А.)'})
# end of timetable insertion

def index(request):
    subjects = Subjects.objects.all()
    teachers = Teachers.objects.all()
    classrooms = Classrooms.objects.all()
    return render(request, 'index.html', {'teachers': teachers, 'subjects': subjects, 'classrooms': classrooms,
                                          'title': 'Автоматическое составление расписаний (Другова О.А.)'})

def calc(request):
    subjects = Subjects.objects.all()
    teachers = Teachers.objects.all()
    classrooms = Classrooms.objects.all()
    return render(request, 'Calculation.html', {'teachers': teachers, 'subjects': subjects, 'classrooms': classrooms,
                                          'title': 'Автоматическое составление расписаний (Другова О.А.)- результат'})
