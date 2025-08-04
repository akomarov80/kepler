from django.db.models.functions import NullIf
from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaultfilters import title
from django.views.generic import ListView, DetailView, CreateView
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponse

from .models import *

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from deap import base
from deap import creator
from deap import tools

import random
import matplotlib.pyplot as plt
import seaborn as sns

# константы задачи

ONE_MAX_LENGTH = 100

# константы генетического алгоритма

POPULATION_SIZE = 200
P_CROSSOVER = 0.9
P_MUTATION = 0.1
MAX_GENERATIONS = 50

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

print('*')

toolbox = base.Toolbox()
toolbox.register("zeroOrOne", random.randint, 0, 1)

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox.register("individualCreator", tools.initRepeat, creator.Individual, toolbox.zeroOrOne, ONE_MAX_LENGTH)
toolbox.register("populationCreator", tools.initRepeat, list, toolbox.individualCreator)

print('**')


def oneMaxFitness(individual):
    return sum(individual),


toolbox.register("evaluate", oneMaxFitness)

toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("mate", tools.cxOnePoint)
toolbox.register("mutate", tools.mutFlipBit, indpb=1.0 / ONE_MAX_LENGTH)

print('***')


def get_user_count():
    population = toolbox.populationCreator(n=POPULATION_SIZE)
    generationCounter = 0

    fitnessValues = list(map(toolbox.evaluate, population))
    for individual, fitnessValue in zip(population, fitnessValues):
        individual.fitness.values = fitnessValue

    fitnessValues = [individual.fitness.values[0] for individual in population]

    maxFitnessValues = []
    meanFitnessValues = []

    out = ""

    while max(fitnessValues) < ONE_MAX_LENGTH and generationCounter < MAX_GENERATIONS:
        generationCounter = generationCounter + 1
        offspring = toolbox.select(population, len(population))
        offspring = list(map(toolbox.clone, offspring))

        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if (random.random() < P_CROSSOVER):
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < P_MUTATION:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        freshIndividuals = [ind for ind in offspring if not ind.fitness.valid]
        freshFitnessValues = list(map(toolbox.evaluate, freshIndividuals))
        for individual, fitnessValue in zip(freshIndividuals, freshFitnessValues):
            individual.fitness.values = fitnessValue

        population[:] = offspring

        fitnessValues = [ind.fitness.values[0] for ind in population]

        maxFitness = max(fitnessValues)
        meanFitness = sum(fitnessValues) / len(population)
        maxFitnessValues.append(maxFitness)
        meanFitnessValues.append(meanFitness)

        out += f"- Generation {generationCounter}: maxFitness = {maxFitness}, meanFitness = {meanFitness}\n"

    return out


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
    count = None

    if request.method == 'POST':
        count = get_user_count()

    return render(request, 'Calculation.html',
                  {'teachers': teachers, 'subjects': subjects, 'classrooms': classrooms, 'count': get_user_count(),
                   'title': 'Автоматическое составление расписаний (Другова О.А.)'})
