from deap import base
from deap import creator
from deap import tools
from django.db.models.fields import return_None

from .models import *

import time
import random
import TimeTable_App.ttable_class
import TimeTable_App.elitism
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# Genetic Algorithm flow:
def main(gr_num):

    if(gr_num<=1):
        print('WARNING: number of groups is unintialized')
        #time.sleep(5) # тестовое замедление
        return

    # problem constants:
    HARD_CONSTRAINT_PENALTY = 10  # the penalty factor for a hard-constraint violation
    TIME_SLOTS_PER_DAY = 5
    GROUPS_AMOUNT = gr_num        # the number of groups
    SUBJECTS = len(Subjects.objects.all())

    # Genetic Algorithm constants:
    POPULATION_SIZE = 200
    P_CROSSOVER = 0.9  # probability for crossover
    P_MUTATION = 0.3  # probability for mutating an individual
    MAX_GENERATIONS = 300
    HALL_OF_FAME_SIZE = 30

    # set the random seed:
    RANDOM_SEED = 42
    random.seed(RANDOM_SEED)

    toolbox = base.Toolbox()

    # create the group scheduling problem instance to be used:
    ttable = TimeTable_App.ttable_class.TimeTableProblem(GROUPS_AMOUNT, TIME_SLOTS_PER_DAY,HARD_CONSTRAINT_PENALTY)

    print('Ttable_Length:'+str(len(ttable)))

    # define a single objective, maximizing fitness strategy:
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))

    # create the Individual class based on list:
    creator.create("Individual", list, fitness=creator.FitnessMin)

    # create an operator that randomly returns 0 or SUBJECTS (lesson variant, 0== 'without lesson this time slot'):
    toolbox.register("lessonNum", random.randint, 0, SUBJECTS * 3)

    # create the individual operator to fill up an Individual instance:
    toolbox.register("individualCreator", tools.initRepeat, creator.Individual, toolbox.lessonNum, len(ttable))

    # create the population operator to generate a list of individuals:
    toolbox.register("populationCreator", tools.initRepeat, list, toolbox.individualCreator)

    # fitness calculation
    def getCost(individual):
        return ttable.getCost(individual),  # return a tuple

    toolbox.register("evaluate", getCost)

    # genetic operators:
    toolbox.register("select", tools.selTournament, tournsize=2)
    # toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mate", tools.cxUniform, indpb=0.1)
    # toolbox.register("mutate", tools.mutUniformInt, low = 0, up = SUBJECTS*3, indpb=1.0 / len(ttable))
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=1.0 / len(ttable))

    print(GROUPS_AMOUNT, " ", TIME_SLOTS_PER_DAY," ", len(ttable))



    # create initial population (generation 0):
    population = toolbox.populationCreator(n=POPULATION_SIZE)

    # prepare the statistics object:
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("min", np.min)
    stats.register("avg", np.mean)

    # define the hall-of-fame object:
    hof = tools.HallOfFame(HALL_OF_FAME_SIZE)

    # perform the Genetic Algorithm flow with hof feature added:
    population, logbook = TimeTable_App.elitism.eaSimpleWithElitism(population, toolbox, cxpb=P_CROSSOVER, mutpb=P_MUTATION,
                                              ngen=MAX_GENERATIONS, stats=stats, halloffame=hof, verbose=True)

    # print best solution found:
    best = hof.items[0]
    print("-- Best Individual = ", best)
    print("-- Best Fitness = ", best.fitness.values[0])
    print()
    print("-- Schedule = ")
    ttable.printScheduleInfo(best)

    # extract statistics:
    minFitnessValues, meanFitnessValues = logbook.select("min", "avg")

    # plot statistics:
    # sns.set_style("whitegrid")
    # plt.plot(minFitnessValues, color='red')
    # plt.plot(meanFitnessValues, color='green')
    # plt.xlabel('Generation')
    # plt.ylabel('Min / Average Fitness')
    # plt.title('Min and Average fitness over Generations')
    # plt.show()

    groupTtableDict = ttable.getGroupTtable(best)
    return TIME_SLOTS_PER_DAY, groupTtableDict

if __name__ == "__main__":
    main(1)