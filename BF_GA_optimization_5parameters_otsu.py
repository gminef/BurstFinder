# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 14:15:19 2022

@author: gmine
"""

import pygad
import Burst_finder_26062022_Otsu as singh
import numpy as np
import csv
import gc


def fitness_function(solution, solution_idx):
    p, n=singh.opt_loop1('D://Usuarios//MiDa//Documents//Callisto//data//Spain-Peralejos_052021-042022'
                        , 'peralejos_optpop100.csv'
                        , cutoff=solution[0], 
                        minimum_area_thresh=solution[1], 
                        #binary_thresh=solution[2], 
                        vmin=solution[2], 
                        vmax=solution[3]
                        ) 
    fitness =2*p + n
    #print (solution[0], solution[1], solution[2], solution[3], 'p: ',p, 'n: ', n, 'fitness: ', fitness)
    global writer
    global header

    csv_result = {
    
         # write results in csv
         'cutoff':  solution[0],
         'minumum area threshold': solution[1],
         #'binary threshold': solution[2],
         'vmin': solution[2],
         'vmax': solution[3],
         'p': p,
         'n': n,
         'fitness': fitness
         }
    with open('solutionsGA.csv', 'a', encoding='UTF8', newline='') as fo:
        writer = csv.DictWriter(fo, fieldnames=header)
        writer.writerow(csv_result)
        fo.flush()
    gc.collect()
    return fitness

sol_per_pop = 12
num_genes = 4
cutoffs = np.arange(0,190,5)
#binary_thresholds=[0.000001,0.00001, 0.0001, 0.001, 0.01, 0.1, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 7,8,9, 10, 11, 12, 13, 14, 15]
vmins=[0.000001,0.00001, 0.0001, 0.001, 0.01, 0.1, 1, 2, 3, 4]
vmaxs=np.arange(700, 1600, 100)
min_area_thresholds=np.arange(10, 100, 5)
# gene_space = [np.arange(50,2001,50), [0.1, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10], np.arange(0.01,5,0.1), np.arange(150,1000,5), np.arange(1,300,2)]
gene_space = [cutoffs.tolist(), min_area_thresholds.tolist() 
              #,binary_thresholds
              ,vmins, vmaxs.tolist()
              ]

mutation_percent_genes = 10
num_generations=15
parent_selection_type = "sss"
#K_tournament=4
crossover_type="single_point"
keep_parents=2
mutation_type="random"
num_parents_mating=4
filename = 'GA_Optimization_Humain_'

ga_instance = pygad.GA(num_generations=num_generations,
                       gene_space=gene_space,
                       num_parents_mating=num_parents_mating,
                       fitness_func=fitness_function,
                       sol_per_pop=sol_per_pop,
                       parent_selection_type=parent_selection_type,
                       keep_parents=keep_parents,
                       num_genes=num_genes,
                       mutation_type=mutation_type,
                       mutation_percent_genes=mutation_percent_genes,
                       save_best_solutions=True,
                       save_solutions=True,
                       crossover_type=crossover_type
                       )

header = ['cutoff', 'minumum area threshold'
          #,'binary threshold'
          , 'vmin','vmax','p', 'n', 'fitness']  
with open('solutionsGA.csv', 'w', encoding='UTF8', newline='') as fo:
    writer = csv.DictWriter(fo, fieldnames=header)
    writer.writeheader()

ga_instance.run()
ga_instance.plot_fitness()

#Save the current instance of the genetic algorithm to avoid losing the progress made. 
ga_instance.save(filename=filename)

solution, solution_fitness, solution_idx = ga_instance.best_solution()
print("Parameters of the best solution : {solution}".format(solution=solution))
print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))
print("Index of the best solution : {solution_idx}".format(solution_idx=solution_idx))

#Load the saved model using the load() function and continue using it.
#loaded_ga_instance = pygad.load(filename=filename)
#print(loaded_ga_instance.best_solution())