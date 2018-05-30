from deap import tools
from deap import base, creator
import random

IND_SIZE =
POP_SIZE = 30
creator.create("FitnessMin", base.Fitness, weights = (1.0, 1.0, 1.0))
creator.create("Individual", list, fitness = creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("attribute", random.random)
toolbox.register("individual", tools.initRepeat, creator.Individual,
                 toolbox.attribute, n = IND_SIZE)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evaluate(individual):
    return sum(individual),

toolbox.register("mate", tools.cxPartialyMatched())
toolbox.register("mutate", tools.mutShuffleIndexes(), indpb = 0.05)
toolbox.register("select", tools.selSPEA2(), k = )
toolbox.register("evaluate", evaluate)


def main():
    pop = toolbox.population(POP_SIZE)
    CXPB, MUTPB, NGEN = 0.5, 0.2, 10000

    #Evaluate the entire population
    fitnesses = map(toolbox.evaluate, pop)
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    for g in range(NGEN):
        offspring = toolbox.select(pop, len(pop))
        offspring = map(toolbox.clone, offspring)

        for child1, child2 in list(zip(offspring[::2], offspring[1::2])):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        pop[:] = offspring

    return pop
