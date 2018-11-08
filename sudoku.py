from random import randint, choice, shuffle
from math import ceil
import time
from copy import deepcopy
from sys import argv

def readSudoku(filename):
	sudoku = []
	for line in open(filename, 'r'):
		row = []
		if (line != '---!---!---\n'):
			for char in line:
				if (char == '.'):
					# Zeros are empty values
					row.append(0)
				elif (char == '!' or char == '\n'):
					pass
				else:
					# Add fixed position
					row.append(int(char))
			sudoku.append(row)
	return sudoku

start = []
def create(grid):
	for row in range(9):
		for column in range(9):
			x = randint(1,9)
			if grid[row][column] == 0:
				# Randomly fill in grid
				grid[row][column] = x
			else:
				# Check for fixed position
				if (row, column) not in start:
					start.append((row,column))
	return grid

def createPopulation(startGrid):
	# Initialise population
	return [create(deepcopy(startGrid)) for i in range(populationSize)]

def printGrid(grid):
	for row in grid:
		print(row)
	print("")

def rowDuplicates(grid):
	duplicates = 0
	for i in grid:
		duplicates += len(i)-len(set(i))
	return duplicates

def columnDuplicates(grid):
	duplicates = 0
	for i in range(len(grid)):
		column = [row[i] for row in grid]
		duplicates += len(column)-len(set(column))
	return duplicates

def subGridDuplicates(grid):
	duplicates = 0
	for i in range(0,9,3):
		for j in range(0,9,3):
			subGrid = sum([row[j:j+3] for row in grid[i:i+3]], [])
			duplicates += len(subGrid)-len(set(subGrid))
	return duplicates

def fitnessFunction(population):
	fitnessArray = []
	for sample in population:
		# Sum duplicates
		rd = rowDuplicates(sample)
		cd = columnDuplicates(sample)
		sgd = subGridDuplicates(sample)
		fitnessArray.append(rd+cd+sgd)
	return fitnessArray

def elitistSelection(population, fitnessArray, ratio):

	# Shuffle population to ensure children are selected
	zipped = list(zip(population, fitnessArray))
	shuffle(zipped)
	population, fitnessArray = zip(*zipped)
	population, fitnessArray = list(population), list(fitnessArray)

	# Sort population based on fitness
	sorted_population = sorted(zip(population, fitnessArray), key = lambda ind_fit: ind_fit[1])
	# Truncate based on ratio
	parents = [individual for individual, fitness in sorted_population[:int(len(population)*ratio)]]
	return parents

def tournamentSelection(population, fitnessArray, ratio):
	parents = []
	numParents = populationSize-int(populationSize*ratio)
	for i in range(numParents):
		# Randomly select two individuals
		contender1 = randint(0, populationSize-1)
		contender2 = randint(0, populationSize-1)
		# Append fittest to parents
		if fitnessArray[contender1] > fitnessArray[contender2]:
			parents.append(population[contender2])
		elif fitnessArray[contender1] < fitnessArray[contender2]:
			parents.append(population[contender1])
		else:
			parents.append(choice([population[contender1], population[contender1]]))

	# Sort population based on fitness
	fitnessArray = fitnessFunction(parents)
	sorted_population = sorted(zip(parents, fitnessArray), key = lambda ind_fit: ind_fit[1])

	parents = [individual for individual, fitness in sorted_population]
	return parents

def uniformCrossover(fittest):
	offspring = []
	while len(fittest)+len(offspring) < populationSize:
		# Randomly choose two parents
		p1 = deepcopy(choice(fittest))
		p2 = deepcopy(choice(fittest))
		for x in range(9):
			for y in range(9):
				# "Flip coin" to decide if gene is copied
				decision = randint(1,2)
				if decision == 1:
					p1[x][y] = p2[x][y]
		offspring.append(p1)
	return offspring
			
def myCrossover(fittest):
	offspring = []
	while len(fittest)+len(offspring) < populationSize:
		# Randomly choose two parents
		p1 = deepcopy(choice(fittest))
		p2 = deepcopy(choice(fittest))
		crossovers = randint(0,8)
		for i in range(crossovers):
			crossType = randint(1,3)
			if crossType == 1:
				# cross random row
				point = randint(0,8)
				p1[point] = p2[point]
			elif crossType == 2:
				# cross random column
				point = randint(0,8)
				for row1, row2 in zip(p1, p2):
					row1[point], row2[point] = row2[point], row1[point]
			elif crossType == 3:
				# cross random subgrid
				sg = choice([0,3,6])
				point = choice([0,3,6])
				for row1, row2 in zip(p1[point:point+3], p2[point:point+3]):
					row1[sg:sg+3], row2[sg:sg+3] = row2[sg:sg+3], row1[sg:sg+3]
		offspring.append(p1)
	return offspring

def singlePointCrossover(fittest):
	offspring = []
	while len(fittest)+len(offspring) < populationSize:
		# Randomly choose two parents
		p1 = deepcopy(choice(fittest))
		p2 = deepcopy(choice(fittest))
		crossType = randint(1,2)
		# Randomly choose crossover point
		point = randint(0,8)
		if crossType == 1:
			# single point row crossover
			p1[point:] = p2[point:]
		elif crossType == 2:
			# single point column crossover
			for row1, row2 in zip(p1, p2):
				row1[point:], row2[point:] = row2[point:], row1[point:]
		offspring.append(p1)
	return offspring

def twoPointCrossover(fittest):
	offspring = []
	while len(fittest)+len(offspring) < populationSize:
		# Randomly choose parents
		p1 = deepcopy(choice(fittest))
		p2 = deepcopy(choice(fittest))
		crossType = randint(1,2)
		# Randomly choose two crossover points
		point1 = randint(0,3)
		point2 = randint(4,8)
		if crossType == 1:
			# two point row crossover
			p1[point1:point2] = p2[point1:point2]
		else:
			# two point column crossover
			for row1, row2 in zip(p1, p2):
				row1[point1:point2] = row2[point1:point2]
		offspring.append(p1)
	return offspring

def mutationRate(probability):
	# Generate random probability
	p = randint(0, 100)/float(100)
	if p < ceil(probability)-probability:
		return ceil(probability)-1
	else:
		return ceil(probability)

def uniformMutate(offspring, probability):
	for child in offspring:
		for i in range(mutationRate(probability)):
			loop = True
			while loop:
				x = randint(0,8)
				y = randint(0,8)
				# Check it isn't a fixed position
				if (x,y) not in start:
					child[x][y] = randint(1,9)
					loop = False
	return offspring

def nonUniformMutate(offspring, probability):
	for child in offspring:
		for i in range(mutationRate(probability)):
			loop = True
			while loop:
				x = randint(0,8)
				y = randint(0,8)
				# Check it isn't a fixed position
				if (x,y) not in start:
					if child[x][y] < 9:
						child[x][y] += 1
					else:
						child[x][y] = 1
					loop = False
	return offspring

def swapMutate(offspring, probability):
	for child in offspring:
		for i in range(mutationRate(probability)):
			loop = True
			while loop:
				x,y,a,b = randint(0,8),randint(0,8),randint(0,8),randint(0,8)
				# Check neither are fixed positions
				if (x,y) not in start and (a,b) not in start:
					mutation = choice([1,9])
					# Swap genes
					child[x][y], child[a][b] = child[a][b], child[x][y]
					loop = False
	return offspring

def stagantionPoint():
	if populationSize == 10:
		return 15000
	elif populationSize == 100:
		return 2000
	elif populationSize == 1000:
		return 250
	elif populationSize == 10000:
		return 50

def terminated(fittest, stagnationCount, iterations):
	if fittest == 0:
		print("\nSolution found\n")
		return True
	elif iterations == stagantionPoint()*10:
		print("\nSolution not found\n")
		return True
	elif (stagnationCount >= stagantionPoint()):
		print("\nSolution not found\n")
		return True
	else:
		return False

def evolve(population, fitnessArray, crossover, mutation, ratio, probability):
	iterations = 0
	stagnationCount = 0
	lastFittest = 0
	while True:
		iterations += 1
		# select best individuals
		matingPool = elitistSelection(population, fitnessArray, ratio)
		# recombine the best into children
		children = crossover(matingPool)
		# mutate children
		children = mutation(children, probability)
		# Creat new population
		population = matingPool+children
		fitnessArray = fitnessFunction(population)
		fittest = min(fitnessArray)

		print("Best fitness:", fittest)

		# Check if termination criterion have been met
		if terminated(fittest, stagnationCount, iterations):
			index = fitnessArray.index(fittest)
			printGrid(population[index])
			return iterations
		
		if (fittest == lastFittest):
			stagnationCount += 1
		else:
			stagnationCount = 0
		lastFittest = fittest

def tester():
	results = {}
	for r in range(1,10):
		ratio = r/10
		for m in range(1,10):
			mProb = m/10
			times = []
			iterations = []
			percent = 0
			for i in range(5):
				start_time = time.time()
				grid = readSudoku(argv[1])
				population = createPopulation(grid)
				fitnessArray = fitnessFunction(population)
				x = evolve(population, fitnessArray, twoPointCrossover, uniformMutate, ratio, mProb)
				elapsed_time = time.time() - start_time
				if x != None:
					times.append(elapsed_time)
					iterations.append(x)
			percent = (len(iterations))*100
			if len(iterations) > 0:
				aveTime = sum(times)/len(times)
				aveIter = sum(iterations)/len(iterations)
			else:
				aveTime = None
				aveIter = None
			results[(ratio, mProb)] = [aveTime, aveIter, percent]
			print(results)
	return results

### Initialize parameters ###
populationSize = int(argv[2])
ratio = float(argv[3])
probability = float(argv[4])
grid = readSudoku(argv[1])

start_time = time.time()

### Evolve ###
population = createPopulation(grid)
fitnessArray = fitnessFunction(population)
iterations = evolve(population, fitnessArray, twoPointCrossover, uniformMutate, ratio, probability)

### Output results ###
elapsed_time = time.time() - start_time
print("Population Size:", populationSize, "Sudoku: ", argv[-1])
print("Iterations:", iterations, " Time:", elapsed_time)
print("Mutation Rate:", probability, " Number of Parents:", ratio*populationSize)



