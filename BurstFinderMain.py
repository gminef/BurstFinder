import argparse
import BF_GA_optimization
import os 
import utils
import Burst_finder
import pandas as pd

PARAMETERS_CSV_FILE = 'Parameters.csv'

print (' BURST FINDER : \n',\
'Please select one of the following options:       \n',\
'  1- Parameter optimization for a specific station\n',
'  2- Find bursts in a dataset\n',\
'  3- Test performance\n',\
'  4- Real time burst finding\n',\
'  5- Exit')

the_option = input()

if the_option == "1":
    print(
            "Please specify the *Instrument code* of the observatory:\n"\
            "whose data the Burst Finder algorithm’s parameters will be optimized for.\n"\
            "*Instrument code* corresponds to one of the instrument-location combination from\n"\
            "[link](http://soleil.i4ds.ch/solarradio/data/readme.txt). The text before the first\n"\
            "hyphen in a file name is the *instrument code*"   
        )
    instrument_code = input()

    print (
            "\nPlease specify a .csv file name:\n"\
            "This .csv should list a previously classified dataset of spectra data.\n"\
            "It is composed of fit.gz file names followed by 0 or 1.\n \
            “0” means no burst can be found in the file (negative),\n"\
            "1” means there is at least one burst in the file (positive).\n"\
            "No header needed and please use semicolon separator.\n"\
            "Recommended to use a dataset of 100 files with 50 positives and 50 negatives.\n"\
            "The optimization process will iterate different binary threshold, area threshold and ASI threshold\n"\
            "value combinations and will set the best option found as default for the specified observatory."               
        )
    csv_file = input()
    if not os.path.isfile(csv_file):
        print ( "File ", csv_file," doesn't exist")
        exit()

    print("Please specify folder of the files:")
    fit_files_dir = input()
    if not os.path.isdir(fit_files_dir):
        print ( "Directory ", fit_files_dir," doesn't exist")
        exit()

    solution, solution_fitness = BF_GA_optimization.run_GA(fit_files_dir, csv_file)
    print(solution, solution_fitness)

    if os.path.isfile(PARAMETERS_CSV_FILE):
        parameters_df = utils.read_parameters_file(PARAMETERS_CSV_FILE)

        if instrument_code in parameters_df['Observatory'].values:
            row = parameters_df.loc[parameters_df['Observatory'] == instrument_code]
            print (row["Fitness"])

            if int(row["Fitness"]) < solution_fitness:
                # update row values
                parameters_df.loc[parameters_df['Observatory'] == instrument_code] = [\
                     instrument_code, solution[0], solution[1], solution[2],\
                     solution[3], solution[4], solution_fitness]
                parameters_df.to_csv(PARAMETERS_CSV_FILE, header=True)

        else: # didn't find instrument
            # Create new row with all the data regarding the instrument
            new_row = {'Observatory': [instrument_code], 'ASI Threshold': [solution[0]],\
                   'Area Threshold': [solution[1]], 'Binary Threshold': [solution[2]],\
            	   'V min': [solution[3]], 'V max': [solution[4]], 'Fitness': [solution_fitness]}
            new_row_df = pd.DataFrame(new_row)
            # Append the new data
            parameters_df = pd.concat([parameters_df, new_row_df])
            # Write updated csv with the new instrument and its data
            parameters_df.to_csv(PARAMETERS_CSV_FILE, index=False, header=True)

        row = parameters_df.loc[parameters_df['Observatory'] == instrument_code]

        print(
        "*Instrument code* parameters are optimized as:\n"\
        "ASI Threshold: {ASI_Thr}".format(ASI_Thr = row["ASI Threshold"]),"\n"\
        "Area Threshold: {Area_Thr}".format(Area_Thr=row["Area Threshold"]),"\n"\
        "Binary Threshold: {Bin_Thr}".format(Bin_Thr=row["Binary Threshold"]),"\n"\
        "V min: {V_min}".format(V_min=row["V min"]),"\n"\
        "V max: {V_max}".format(V_max=row["V max"]),"\n"\
        "You can now proceed with the burst finding process for this observatory.\n"\
        " Updated values will be used automatically."
         )

    else: # TODO : create empty header file with new dataframe
        print (PARAMETERS_CSV_FILE, " file does not exist")


        
    


    
elif the_option == "2":
    print("Please specify folder of the files to process.")

    fit_files_dir = input()
    if not os.path.isdir(fit_files_dir):
        print ( "Directory ", fit_files_dir," doesn't exist")
        exit()

    print("Do you want only a list of the files with bursts (0), or also"\
            "generate .png where possible bursts are marked (1)?")

    user_choice = input()
    write_burst_imgs = False
    if user_choice == "1":
        write_burst_imgs = True
    elif user_choice != "0" and user_choice != "1":
        print("Unsupported choice ",user_choice)
        exit()
    
    if not os.path.isfile("Parameters.csv"):
        print ("Parameters.csv does not exist.")
        exit()
    
    parameters_data_frame = utils.read_parameters_file("Parameters.csv")

    for entry in os.listdir(fit_files_dir): # loop on all files in a directory
        full_path = os.path.join(fit_files_dir, entry)
        if os.path.isfile(full_path) and entry[-7:] == ".fit.gz":
            
            instrument_code = entry.split('_')[0]
            
            print ("Instrument_code: ",instrument_code)
            try:

                if instrument_code in parameters_data_frame['Observatory'].values: # if instrument exists in the Parameters.csv file
                    row = parameters_data_frame.loc[parameters_data_frame['Observatory'] == instrument_code]
                    cutoff, minimum_area_thresh, binary_thresh, vmin, vmax = int(row["ASI Threshold"]),\
                        int(row["Area Threshold"]),float(row["Binary Threshold"]),float(row["V min"]),float(row["V max"])
    
                    result = Burst_finder.singh_alg(full_path, cutoff, minimum_area_thresh, binary_thresh, vmin, vmax,write_burst_img=write_burst_imgs)
                    # write the burst output
                    with open(fit_files_dir+'/Bursts.csv', 'a+') as file:
                        file.write(entry+","+str(result)+"\n",)
                else:
                    print(
                        "Please firstly carry out a parameter optimization on a data set which include some"\
                        "files known to have bursts in them and some that do not have any bursts.\n"\
                        "This is necessary to optimize the parameters of the burst finder algorithm according to "\
                        "a specific instruments' data.\n It is usual that different instruments have different "\
                        "local RFI profiles as well as different intensity calibration. That's why this step is required."
                    )
                        
                    exit()
            except (ValueError, OSError) as e:
                    print ("Error -> ", entry, "{0}".format(e))
            
elif the_option == "3":
    
    print(
            "Please specify the *Instrument code* of the observatory whose dataset will be tested:\n"\
            "*Instrument code* corresponds to one of the instrument-location combination from\n"\
            "[link](http://soleil.i4ds.ch/solarradio/data/readme.txt). The text before the first\n"\
            "hyphen in a file name is the *instrument code*"   
        )
    instrument_code = input()
    
    print (
            "\nPlease specify a .csv file name:\n"\
            "This .csv should list a previously classified dataset of spectra data.\n"\
            "It is composed of fit.gz file names followed by 0 or 1.\n"  \
            "0 means no burst can be found in the file (negative)"\
            "1 means there is at least one burst in the file (positive).\n"\
            "No header needed and please use semicolon separator.\n"\
            "The output will be p, n and processed:\n"\
            "p: The number of real positives (as specified by the .csv file) identified as positive by the algorithm, \n"\
            "n : The number of real negatives (as specified by the .csv file) identified as negative by the algorithm, \n"\
            "processed : Total number of the processed files.\n"
        )
    csv_file = input()
    if not os.path.isfile(csv_file):
        print ( "File ", csv_file," doesn't exist")
        exit()

    print("Please specify folder of the files:")
    fit_files_dir = input()
    if not os.path.isdir(fit_files_dir):
        print ( "Directory ", fit_files_dir," doesn't exist")
        exit()
    
    if not os.path.isfile("Parameters.csv"):
        print ("Parameters.csv does not exist.")
        exit()
    
    parameters_data_frame = utils.read_parameters_file("Parameters.csv")
        
    if instrument_code in parameters_data_frame['Observatory'].values: # if instrument exists in the Parameters.csv file
        row = parameters_data_frame.loc[parameters_data_frame['Observatory'] == instrument_code]
        cutoff, minimum_area_thresh, binary_thresh, vmin, vmax = int(row["ASI Threshold"]),\
            int(row["Area Threshold"]),float(row["Binary Threshold"]),float(row["V min"]),float(row["V max"])

        p, n = Burst_finder.opt_loop1(fit_files_dir, csv_file, cutoff,\
             minimum_area_thresh, binary_thresh, vmin, vmax)
        
 
    else:
        print(
            "Please firstly carry out a parameter optimization. "\
            "This is necessary to optimize the parameters of the burst finder algorithm according to "\
            "a specific instruments' data.\n It is usual that different instruments have different "\
            "local RFI profiles as well as different intensity calibration. That is why this step is required."
        )
            
        exit()


elif the_option == "4":
    print(
        "Please specify *Instrument codes* of the observatory, whose data will be processed in real time.\n"\
        "*Instrument codes* corresponds to the instrument-location combination from [link] "\
        "(http://soleil.i4ds.ch/solarradio/data/readme.txt).\n The text before the first hyphen in"\
        " a file name is the *instrument code* \nUp to 4 observatory codes can be chosen."
        )
    instrument_code = input()

    # output_folder = input("Please specify the folder to save the files.\n")
    # utils.create_output_folder(output_folder)

    utc_time = utils.get_current_utc_time()
    utils.download_current_date_data(utc_time,instrument_code)#,output_folder)


else:
    exit()