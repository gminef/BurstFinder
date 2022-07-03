from distutils.command.build_ext import build_ext
import sys

from sklearn import utils
sys.path.append('../src/')	#this and above line is added because 'PyCallisto.py' and
							#'pyCallistoUtils.py' are not in the same folder as this script.
import pycallisto as pyc
#import pycallisto_utils as utils
#import astropy.io.fits as pyfits
import matplotlib.pyplot as plt
import numpy as np 
import cv2 as cv
import os
import csv
import gc
import time
from datetime import datetime, timedelta

SHOW_IMG = False
SHOW_DEBUG = False


def get_filtered_contours(image, original_img, minimum_area_thresh):
    contours,hierarchy = cv.findContours(image,cv.RETR_LIST, cv.CHAIN_APPROX_NONE )
    filtered_contours = []
    colored  = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
    for i,cnt in enumerate(contours):
        area = cv.contourArea(contours[i])
        if area > minimum_area_thresh and area < ((image.shape[0]*image.shape[1])*(0.75)):
            filtered_contours.append(cnt)

    if SHOW_IMG:
        cv.drawContours(colored, filtered_contours, -1, (0, 255, 0), 2)
        cv.imshow("contours", colored)
        cv.waitKey()
    
    return filtered_contours


def sort_contours(cnts, method="left-to-right"):
   
	# initialize the reverse flag and sort index
	reverse = False
	i = 0
	# handle if we need to sort in reverse
	if method == "right-to-left" or method == "bottom-to-top":
		reverse = True
	# handle if we are sorting against the y-coordinate rather than
	# the x-coordinate of the bounding box
	if method == "top-to-bottom" or method == "bottom-to-top":
		i = 1
	# construct the list of bounding boxes and sort them from top to
	# bottom
	boundingBoxes = [cv.boundingRect(c) for c in cnts]
	(cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
		key=lambda b:b[1][i], reverse=reverse))
	# return the list of sorted contours and bounding boxes
	return (cnts, boundingBoxes)


def get_freq_times(filtered_contours, freqs, cutoff, vmin, vmax, start_time, end_time, shape):
    
    #output = "No Sun Burst"
    output = 0
    bursts_x,bursts_y = [],[]
    Timerange = end_time - start_time
    Timerange = Timerange.total_seconds()
    Freqrange = freqs[0] - freqs[-1]
    Timestep = Timerange/shape[1]
    Freqstep = Freqrange/shape[0]

    for cnt_num,cnt in enumerate(filtered_contours) :
        if SHOW_DEBUG: 
            print ("Contour Number ",cnt_num," : ")
        
        area = cv.contourArea(cnt) * Timestep * Freqstep
        #if area < minimum_area_thresh:
            #print ("area :",area," discarded, signal too weak")
            #continue    
        
        # convert to list of points
        cnt_to_list = [[l[0][0],l[0][1]] for l in cnt]

        #sort contours points from left to right
        sorted_filtered_cnt = sorted(cnt_to_list, key=lambda x:x[0])

        time_2 = sorted_filtered_cnt[-1][0]
        time_1 = sorted_filtered_cnt[0][0]

         # skip the case when time difference is less than 1s
        if (time_2 - time_1)*Timestep < 1: #Because we consider there sould not be any bursts less than 1 second duration
            #print ("time extension :",(time_2 - time_1)," discarded, signal too brief, less than 1s")
            continue

        # larger the y the less frequency so the maximum frequency will be with the lowest y 
        sorted_filtered_cnt_freq = sorted(cnt_to_list, key=lambda x:x[1],reverse = True)
        #print(sorted_filtered_cnt_freq)

        freq_2 = sorted_filtered_cnt_freq[-1][1]
        
        # here we are removing the lowest frequency point when we have two points on the same x -time- 
        for i in range(len(sorted_filtered_cnt) - 1, -1, -1):
            if sorted_filtered_cnt[i][0] == sorted_filtered_cnt[i-1][0]: # x1 == x2
                if sorted_filtered_cnt[i][1] < sorted_filtered_cnt[i-1][1]: # y1 < y2 then remove the other point 
                    sorted_filtered_cnt.pop(i-1)
                else:
                     sorted_filtered_cnt.pop(i)


        # sorted_filtered_cnt_freq_2 = sorted(sorted_filtered_cnt, key=lambda x:x[1],reverse = True)

        # freq_1 = sorted_filtered_cnt_freq_2[0][1]

        # time_1 = time_1 * 0.25
        # time_2 = time_2 * 0.25

        # #print("Frequency 2 : ",freq_2,",  Frequency 1 : ",freq_1)
       

        # freq_2 = freqs[freq_2] 
        # freq_1 = freqs[freq_1]


        
        #print("Frequency 2 : ",freq_2,", Time 2 : ",time_2,", Frequency 1 : ",freq_1,", Time 1 : ",time_1)

        numpy_sorted_filtered_cnt = np.array(sorted_filtered_cnt)
        
        x = numpy_sorted_filtered_cnt[:,0]
        y = numpy_sorted_filtered_cnt[:,1]
        m, b = np.polyfit(x, y, 1)
        
        #print(m)
        #print(b)
        
         # plt.title('line plot')
        
         # plt.plot(x, y, 'o')
        
         # plt.plot(x, m*x + b)
         # plt.show()
        v = m * Freqstep / Timestep
        if SHOW_DEBUG: 
            print("slope of fitted line", v)

        
        if m < 0:
             # Not a burst 
             continue
             #return sunBurst, original_bursts_points # change  this later to simplify the code return 
        
        
        
        if v < vmin:
            if SHOW_DEBUG: 
                print ("v :",v," discarded, signal too horizontal")
            continue
        
        if v > vmax:
            if SHOW_DEBUG: 
                print ("v :",v," discarded, signal too vertical")
            continue
        


        ASI = v * area

        if SHOW_DEBUG: 
            print ("v :",v)
            print ("area :",area)
            print ("ASI :",ASI)

        if ASI > cutoff:
            #output = "Sun Burst!"
            output = 1
            bursts_x.append(x)
            bursts_y.append(y)
           
    #if (found = 0)
    #    print ("No Sun Burst")
    return output,bursts_x,bursts_y

def draw_burst_upper_contour(original_fit_image, xlist ,ylist):
    for num in range(len(xlist)):
        for point in zip(xlist[num],ylist[num]):
            cv.circle(original_fit_image, point, 1,(0,0,255))
    if SHOW_IMG:
        cv.imshow("Bursts",original_fit_image)
    return  original_fit_image

def singh_alg (fit_file_path, cutoff, minimum_area_thresh, vmin, vmax,write_burst_img = False):
    burst_img = None
    fits = pyc.PyCallisto.from_file(fit_file_path)

    #do background subtraction
    background_subtracted = fits.subtract_background()
    plt, image, freqs,start_time,end_time = background_subtracted.spectrogram(option=3, show_tick=False,xtick=1)
    plt.close()
    
    shape1 = image.shape
    rowno = shape1 [0]
    colno = shape1 [1]
    #erase lower rows because of instrument interference
    image[rowno-10:rowno,:] = 0
    
    #Assign 0 to negative values
    image[image<0] = 0
    if SHOW_DEBUG:
        print (start_time,end_time)

        print ("Image minimum value : ",image.min(),", Image maximum value : ",image.max())


    #convert image datatype to be unsigned integer
    image_8bit = np.uint8(image)
    image_8bit_color = cv.applyColorMap(image_8bit, cv.COLORMAP_JET)

    

    # do binary thresholding 
    #binary_thresh = 2 
    # _, binary_image_color = cv.threshold(image_8bit_color, binary_thresh, 255, cv.THRESH_BINARY)
    image_8bit = cv.medianBlur(image_8bit,5)
    # binary_image_adaptive_gaussian = cv.adaptiveThreshold(image_8bit,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
    #         cv.THRESH_BINARY_INV,7,binary_thresh)
    # binary_image_adaptive_mean = cv.adaptiveThreshold(image_8bit,255,cv.ADAPTIVE_THRESH_MEAN_C,\
    #         cv.THRESH_BINARY_INV,7,binary_thresh)
    thop, binary_image_otsu = cv.threshold(image_8bit,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
    if SHOW_IMG:
        # cv.imshow("binary image ",binary_image_color)
        # cv.imshow("adaptive binary image gaussian", binary_image_adaptive_gaussian)
        # cv.imshow("adaptive binary image mean", binary_image_adaptive_mean)
        cv.imshow("binary image otsu", binary_image_otsu)
        cv.waitKey()
    if SHOW_DEBUG:
        print(binary_image_otsu.shape)
    
    shape = binary_image_otsu.shape
    binary_image = binary_image_otsu

    filtered_contours = get_filtered_contours(binary_image,image,minimum_area_thresh)

    output_singh,Bursts_x,Bursts_y = get_freq_times(filtered_contours, freqs, cutoff, vmin, vmax, start_time, end_time, shape)
    

    if SHOW_IMG :
        BGR_image  = cv.cvtColor(image.astype('float32'), cv.COLOR_GRAY2BGR)
        cv.drawContours(BGR_image, filtered_contours, -1, (0, 255, 0), 2)
        cv.imshow("contours", BGR_image)
        
        if output_singh: # if a burst
    
            burst_img = draw_burst_upper_contour(BGR_image.copy(),Bursts_x,Bursts_y)
            burst_img = burst_img*255
            burst_img_file_path = fit_file_path.split('.')[0]+'.png'
            if SHOW_DEBUG:
             print (" burst_img_file_path  ",burst_img_file_path)
            cv.imwrite(burst_img_file_path,burst_img)

    if SHOW_IMG : 
        cv.waitKey() # decomentar esta línea para ver imagenes de los ficheros procesados. 
        # Cuando se cierran ventanas de imagenes seguirá con el siguiente fichero.
        # Cuando se comenta waitkey, los procesa todos en masiva y genera 
        # el csv de los resultados al final.
        
    return (output_singh)

    
def opt_loop1 (fit_files_dir, csv_file_path, cutoff, minimum_area_thresh, vmin, vmax):
    p=0 
    n=0
    processed = 0
    with open(csv_file_path, newline='') as fi:
        # read and process fits file_names in csv    
        file_read = csv.reader(fi, delimiter=';')
    
        array = list(file_read)
        
    split_array = [array[x:x+100] for x in range(0, len(array), 100)]
    #print (split_array)
    
    length = len(split_array)
    
    # p=0
    # n=0
    # processed = 0
    del fi, file_read, array
            
    for i in range(1, (length +1), 1):
        
        shortarray = split_array.pop(0)
        #shortarray = split_array[i-1]
        
        st_row_time=time.monotonic()  
        
        for row in shortarray:
            full_path = os.path.join(FIT_FILES_DIR, row[0])
    
            if os.path.isfile(full_path) and row[0][-7:] == ".fit.gz":
                try:
                    #print("FIT FILE : ",entry)
                    #st_singh_alg_time=time.monotonic()
                    result = singh_alg(full_path, cutoff, minimum_area_thresh, vmin , vmax)                
                    #end_singh_alg_time=time.monotonic()
    
                    if result==1 and int(row[1])==1:
                        p = p + 1
                         
                    if result==0 and int(row[1])==0:
                        n = n + 1
                    
                    processed = processed + 1 
                        
                    #print ("Processed: ", row[0], "result: ", result, "row[1]", row[1], "time: ", timedelta(seconds=end_singh_alg_time-st_singh_alg_time))
                        
                except (ValueError, OSError) as e:
                        print ("Error -> ", row[0], "{0}".format(e))
            
        #shortarray.clear() 
        #del shortarray, full_path, result
        end_row_time=time.monotonic()
        print ("Positives, negatives, total processed :", p, n, processed, "time: ", timedelta(seconds=end_row_time-st_row_time))
        gc.collect()
    return p, n
   
#Main program
# cutoff, minimum_area_thresh, binary_thresh, vmin, vmax

# FIT_FILES_DIR = "D://Usuarios//MiDa//Documents//Callisto//Menu-Callisto-main//Data//Instruments//GAURI_2013_all_gz"
CSV_FILE_PATH = 'Spain-Peralejos03_01052021-30042022_3.csv'

FIT_FILES_DIR = "D://Usuarios//MiDa//Documents//Callisto//data//Spain-Peralejos_052021-042022"
#FIT_FILES_DIR = "/home/rawan/sunBurst/burst_finder/data/Burst_files_for_testing_png_generation/"
#CSV_FILE_PATH = 'humain_optpop100.csv'


def opt_loop3 (cutoff, minimum_area_thresh, binary_thresh, vmin, vmax):
    return opt_loop1(FIT_FILES_DIR,CSV_FILE_PATH,cutoff, minimum_area_thresh, vmin, vmax)
 

cutoff = 20
minimum_area_thresh = 70
vmin = 0.1
vmax = 1200 


p,n = opt_loop1(FIT_FILES_DIR,CSV_FILE_PATH, cutoff, minimum_area_thresh, vmin, vmax)
# opt_loop2(FIT_FILES_DIR, cutoff, minimum_area_thresh, binary_thresh, vmin, vmax)


# # #print('he acabado')

