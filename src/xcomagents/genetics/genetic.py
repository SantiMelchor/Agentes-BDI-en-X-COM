import random

class Chromosome():
    def __init__(self, genes):
        self.genes_num = len(genes)
        self.values = genes
        self.__fitness = -1


    @property
    def fitness(self):
        return self.__fitness

    @fitness.setter
    def fitness(self,value):
        self.__fitness = value

    def mutate(self):
        for i in range(len(self.values)):
            if random.randint(1,100) <= 5:
                self.values[i] = random.randint(0,9)


    def __eq__(self, chromosome):
        if not isinstance(chromosome, Chromosome):
            print("Solo se pueden comparar cromosomas")
        return self.values == chromosome.values

    def __repr__(self):
        cadena = "\n"+"-"*self.genes_num*2
        cadena+="\n|"
        cadena+="|".join(map(str,self.values)) +"|" + f" - [{self.fitness}]"
        cadena+="\n"+"-"*self.genes_num*2+"\n"
        return cadena

def generate(genes):
        
        chromosome = []
        for i in range(genes):
            chromosome.append(random.randint(0,9))
        return chromosome

def generate_pop(population, agents=4, roles=5, seed = None):
    if seed:
        random.seed(seed)
    gene_number = agents * roles
    if agents  < 1 or roles < 1 or population < 1:
        return -1
    muestra = []
    for i in range(population):
        chromosome = Chromosome(generate(gene_number))
        while chromosome in muestra:
            chromosome = Chromosome(generate(gene_number))
        muestra.append(chromosome)
    return muestra

def fitness(chromosome: Chromosome):
    return sum(chromosome.values)

def cross(father, mother):
    cross_point = random.choice(range(1,len(father.values)-2))
    chromosome_1 = Chromosome(father.values[:cross_point] + mother.values[cross_point:]) 
    chromosome_2 = Chromosome(father.values[cross_point:] + mother.values[:cross_point])
    chromosome_1.mutate()
    chromosome_2.mutate()
    return chromosome_1, chromosome_2

def new_generation_roulette(population, crossover = 1):
    new_population = []
    probabilities = []
    total = 0
    for i in population:
        total += i.fitness
    new_population.append(population[0])
    for i in population:
        probabilities.append(i.fitness/total)
    
    for i in range(len(population)//2 - 1):
        father = random.choices(population=population, weights=probabilities, k=1)[0]
        mother = random.choices(population=population, weights=probabilities, k=1)[0]
        while mother == father:
            mother = random.choices(population=population, weights=probabilities, k=1)[0]
        if random.random() < crossover:
            chromosome_1, chromosome_2 = cross(father=father, mother=mother)
        else:
            chromosome_1 = mother
            chromosome_2 = father
        new_population.append(chromosome_1)
        new_population.append(chromosome_2)

    new_chromosome = Chromosome(generate(population[0].genes_num)) 
    while new_chromosome in new_population:
        new_chromosome = Chromosome(generate(population[0].genes_num)) 
    new_population.append(new_chromosome)
    return new_population

def tournmanet_choice(population, k=5):
    combatientes = random.sample(population=population,k=k)
    combatientes.sort(reverse=True,key=lambda x: x.fitness)
    return combatientes[0]

def new_generation_tournament(population, k=5, crossover = 1):
    new_population = []
    new_population.append(population[0])
    for i in range(len(population)//2 - 1):
        father = tournmanet_choice(population=population,k=k)
        mother = tournmanet_choice(population=population,k=k)
        while mother == father:
            mother = tournmanet_choice(population=population,k=k)
        if random.random() < crossover:
            chromosome_1, chromosome_2 = cross(father=father, mother=mother)
        else:
            chromosome_1 = mother
            chromosome_2 = father
        new_population.append(chromosome_1)
        new_population.append(chromosome_2)

    new_chromosome = Chromosome(generate(population[0].genes_num)) 
    while new_chromosome in new_population:
        new_chromosome = Chromosome(generate(population[0].genes_num)) 
    new_population.append(new_chromosome)
    return new_population
    


# generations = 1500  
# population = generate_pop(10)
# #print(population)
# for j in range(generations):
#     for i in population:
#         fit = fitness(i)
#         i.fitness = fit
#     population.sort(reverse=True,key=lambda x: x.fitness)
#     if population[0].fitness == 180:
#         print(j)
#         break
#     #print(population[0].fitness)
#     population = new_generation_torunament(population)

# for i in population:
#     fit = fitness(i)
#     i.fitness = fit
# population.sort(reverse=True,key=lambda x: x.fitness)
# print(population)





