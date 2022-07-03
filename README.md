# BurstFinder

The Burst Finder-menu allows you run a burst recognition algorithm over e-Callisto native archives (fit.gz). 

Contributors: The main contributor to this project is Mine Felekten Pinar. 

INSTALLATION: Move to the directory where you have downloaded this repository, open a terminal/cmd and run pip install -r requirements.txt

Description: The Burst Finder-menu allows you run a burst recognition algorithm over e-Callisto native archives (fit.gz). 

The CALLISTO spectrometer is a programmable heterodyne receiver designed 2006 in the framework of IHY2007 and ISWI by Christian Monstein (PI) as member of the former Radio Astronomy Group (RAG) at ETH Zurich, Switzerland.

Options Available

This menu offers the following possibilities:
1.	Parameter optimization for a specific station,
2.	Find bursts in a dataset,
3.	Test performance of the algorithm over a pre-classified set of data
4.	Real time burst finding,
5.	Exit

First steps

In order to execute the Menu, you should execute BurstFinderMain.py, if you want to do it with a terminal/cmd you can just write python BurstFinderMain.py. 

Before being able to process a batch of data/real time data from a specific station, you should select option 1 to carry out a parameter optimization for that specific station. 

With Option 2, you can run the classification algorithm on a dataset, which will be a set of fit.gz files belonging a single station, deposited in a folder. 

Option 3 lets you to verify the performance of the algorithm, over an already classified dataset. 

Option 4 will let you download the files published in real time on http://soleil80.cs.technik.fhnw.ch/solarradio/data/2002-20yy_Callisto/, run the Burst Finder algorithm on them and finally report the files with possible bursts. However, it is under development and not available yet.

Extended description

Option 1 

Before being able to process a batch of data/real time data from a specific station, you should select option 1 to carry out a parameter optimization for that specific station. 

For this, you first should the “instrument code” of this observatory. Later, you need to compose a simple .csv file including 50 “positive” files with bursts, and 50 “negative” files with out bursts. Please see the example file “ALASKA-COHOE_testpopulation100.csv”. 

You should also specify the directory where these files are located.

In this way, the algorithm will optimize the needed parameters and include them in the Parameters.csv for its use later when processing the files.

Option 2

With Option 2, you can run the classification algorithm on a dataset. A dataset will be a set of fit.gz files belonging a single station, deposited in a specific folder. 

This option will ask you the directory and will process all the .  fit.gz files found in it. 

Output is a “Bursts.csv”, where in every row a file in the directory will be included, continued with a “0” or “1”. “ 0” means the algorithm classifies this file as a “negative”, “1” means that it was classified as “positive” (in other words, it includes a signal perceived as a burst.  ) 

You can also choose the option of saving a . png file where the location of the burst will be shown with a red mark.

Both the “Bursts.csv”, and the .  png files will be saved in the directory of the dataset.

Option 3

Option 3 lets you to verify the performance of the algorithm, over an already classified dataset. This data set can be previously classified in a manual manner, for example.

For this, you need to compose a .csv file including the file name of a .  fit.gz, followed by a “0” or “1”. “0” means “negative”: that this file does not contain any burst, “1” means “positive”: that it contains at least one burst.

Then, you should specify the directory where these files are located.

The option will process all the files included in the .csv file. As an output, it will give you a “p”, “n” and “processed”. 

“p”: The number of real positives (as specified by the .csv file) identified as positive by the algorithm

“n” : The number of real negatives (as specified by the .csv file) identified as negative by the algorithm

Option 4

This option is not available yet. It is currently being developed.
