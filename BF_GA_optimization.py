# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 14:15:19 2022

@author: gmine
"""

##pip3 install pygad

import pygad
import Burst_finder as singh
import numpy as np
import csv
import gc

# Global Variables
header = ['cutoff', 'minumum area threshold','binary threshold','vmin', 'vmax', 'p', 'n', 'fitness']  


def fitness_function(solution, solution_idx):
    p, n = singh.opt_loop3(fit_files_dir_global, csv_file_path_global, cutoff=solution[0],\
         minimum_area_thresh=solution[1], binary_thresh=solution[2], vmin=solution[3], vmax=solution[4])
    # p, n = singh.opt_loop3(cutoff=solution[0],\
    #      minimum_area_thresh=solution[1], binary_thresh=solution[2], vmin=solution[3], vmax=solution[4]) 
    fitness = 2*p + n
    #print (solution[0], solution[1], solution[2], solution[3], 'p: ',p, 'n: ', n, 'fitness: ', fitness)
    global writer
    global header

    csv_result = {
    
         # write results in csv
         'cutoff':  solution[0],
         'minumum area threshold': solution[1],
         'binary threshold': solution[2],
         'vmin': solution[3],
         'vmax': solution[4],
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



######## PARAMETERS 
sol_per_pop = 10
num_genes = 5
cutoffs = [1, 2, 3, 5, 7, 9, 11, 15, 20, 30, 40, 50, 70, 90, 110, 140, 170, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 1000]
binary_thresholds=[0.00001,0.0001, 0.001, 0.01, 0.1, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5]
vmins=[0.00001,0.0001, 0.001, 0.01, 0.1, 0.5, 1, 1.5, 2]
vmaxs=np.arange(700, 1500, 100)
min_area_thresholds=np.arange(10, 200, 20)
# gene_space = [np.arange(50,2001,50), [0.1, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8,\
#                9, 10], np.arange(0.01,5,0.1), np.arange(150,1000,5), np.arange(1,300,2)]
gene_space = [cutoffs, min_area_thresholds.tolist(), binary_thresholds
              ,vmins, vmaxs.tolist()
              ]

mutation_percent_genes = 20
num_generations=7
parent_selection_type = "sss"
#K_tournament=4
crossover_type="single_point"
keep_parents=2
mutation_type="random"
num_parents_mating=4
filename = 'GA_Optimization_GAURI_'
########


def run_GA(fit_files_dir, csv_file_path):
    global fit_files_dir_global
    global csv_file_path_global
    fit_files_dir_global = fit_files_dir
    csv_file_path_global = csv_file_path
    
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

    header = ['cutoff', 'minumum area threshold','binary threshold','vmin', 'vmax', 'p', 'n', 'fitness']  
    with open('solutionsGA.csv', 'w', encoding='UTF8', newline='') as fo:
        writer = csv.DictWriter(fo, fieldnames=header)
        writer.writeheader()

    ga_instance.run()
    #ga_instance.plot_fitness()

    #Save the current instance of the genetic algorithm to avoid losing the progress made. 
    ga_instance.save(filename=filename)

    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    print("Parameters of the best solution : {solution}".format(solution=solution))
    print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))
    print("Index of the best solution : {solution_idx}".format(solution_idx=solution_idx))

    #Load the saved model using the load() function and continue using it.
    #loaded_ga_instance = pygad.load(filename=filename)
    #print(loaded_ga_instance.best_solution())

    ##### TO EXPECT WRTITING PARAMETERS CSV AND RETURN THE SOLUTION ( XMIN and all these things)

    return solution, solution_fitness


#run_GA()
