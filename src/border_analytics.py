"""
TEST IDEAS:
* What if dates are in different formats
* What if theres a comma in one of the fields
* What if theres 2 commas in one of the fields
# What if two fields have a comma
* What if the columns in the csv are in different orders

"""


"""
##############OVERVIEW##############
For this challenge, we want to you to 
calculate the total number of times 
vehicles, equipment, passengers and pedestrians 
cross the 
U.S.-Canadian and U.S.-Mexican borders 
each month. 

We also want to know the 
running monthly average of total number of crossings 
for that type of 
crossing and border.


###INPUTS:####
Border_Crossing_Entry_Data.csv 
ALl columns will be read as strings, but can be converted
COLUMNS : 
	Port Name (ignore)
	State (ignore)
	Port Code (ignore)
	Border (keep)
	Date (keep)
	Measure (keep)
	Value (keep)
	Location (ignore)



###OUTPUTS:####
report.csv 
File must contain variables Border,Date,Measure,Value,Average
File must be unique at Border*Date*Measure
File must be sorted (desc) by date, value, measure, border




####SCRIPT SUMMARY######
### STEP 1 : READIN INPUT AND ENSURE PROPER FORMAT
### 1A REFORMAT VARIABLES: DictReader can only read strings
### 1B REDUCE SIZE: keep only the fields I care about


#### STEP 2 : PREPARE DATA FOR SUMMARIZING
#### If a given border*meausure combination does not exist, no problem
#### But if for a given border*measure, there are missing date entries
#### That will make my moving average incorrect (need to pad with zeros)
#### Within each border*measure combination, insert value 0 for missing dates


#### STEP 3 : CREATE SUMMARY STATISTICS FOR EACH BORDER*MEASURE*DATE
#### 3A. SORT DATA SO THAT I CAN USE INTERTOOLS.GROUPBY 
#### 3B. FOR EACH BORDER*MEASURE*DATE CALCULATE NUMBER OF CROSSINGS
#### 3C. WITHIN EACH BORDER*MEASURE, APPEND MOVING AVERAGE FOR THAT MONTH
#### 3D. TRANSFORM RUNNING TOTAL 
####FOR EACH BORDER*CROSSING TYPE (aka measure) , CALCULATE:
		FOR EACH MONTH:
			TOTAL CROSSINGS
			ROUND(PREVIOUS MONTH'S RUNNING TOTAL DIVIDED BY THIS MONTHS ORDER IN TIME)





SORT OUTPUT FILE
FILTER TO ONLY INCLUDE CASES WITH VALUE = 0
MAKE SURE IT CONTAINS THE RIGHT VARIABLES
MAKE SURE IT IS KEYED AT THE RIGHT LEVEL
MAKE SURE IT HAS THE RIGHT NUMBER OF ROWS (AKA UNIQUE CROSSTABS OF KEYS INCLUDING EMPTY MONTHS OR CATEGORIES)

"""



#!/usr/bin/python3

import csv
from pathlib import Path
import os
import operator
import itertools
import datetime
import locale
import collections
import re
import datetime
from fractions import Fraction
from math import ceil





def my_round(num_in, round_to = 0):
	twice_my_num = num_in * 2
	# if twice my number is a whole number then 
	# using the normal round function will use
	# bankers rounding and i want integer rounding
	if twice_my_num % 1 == 0 :
		return ceil(num_in)
	else:
		return round(num_in,round_to)

def PrintNRows(iterable_object, Nrows = 4):
	for i, row in enumerate(iterable_object):
		print(i,row)
		if (i >= (Nrows-1)):
			break


def CleanWhitespace(string_in):
	#convert all contiguous whitespace to be single space
	#remove leading and trailing whitespace,
	cleaned_string = re.sub(r'\s+', ' ', string_in).strip()
	return cleaned_string


def DateToString(datetime_in):
    		return datetime_in.strftime("%m/%d/%Y %I:%M:%S %p")


def IncreaseMonthByM(month_in,M):
	return datetime.datetime(
			year=month_in.year,
			month=month_in.month + M,
			day=month_in.day,
			hour=month_in.hour,
			minute=month_in.minute,
			second=month_in.second)





def PadDictlistWithCustomValues(key, value, my_dictlist, key_to_impute, imputed_value = 0.00):
	#This function scans a dictlist (my_dictlist) for a key:value pair
	#If key:value pair is found, it returns dictlist as-is
	#If not, it returns an augmented dictlist with ONE additional row
	#The additional row is a copy of the FIRST row, with TWO modifications
	### modify the key:value pair, and impute one additional value in dict
    for dict_i in my_dictlist:
        if any(dict_i[key] == value for dict_i in my_dictlist):
            return my_dictlist
        else:
        	#create new temp dict
        	dict_j = dict_i.copy()
        	#modify the temp dict so it has the missing key:value pair.
        	dict_j[key] = value
        	#perform imputation
        	dict_j[key_to_impute] = imputed_value
        	ReturnsNone = my_dictlist.extend([dict(dict_j)])
        	return my_dictlist

# Define  global variables
thisfile_path = Path(__file__)
project_directory = thisfile_path.parent.parent
input_filepath = project_directory / 'input' / "Border_Crossing_Entry_Data.csv"
output_filepath = project_directory / 'output' / "report.csv"




#########
# STEP 1 : read in dataset,
# make sure data conforms to desired formats
# keep track of unique values of border,measure
# keep track of min/max date
#########
input0 = []  # object that will be my input data
unique_values_date = set()  # keep track of unique dates
with open(input_filepath) as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		# convert the Date variable which is a string to be a datetime
		# Keep only 1st 10 characters to allow for irregularity in date/datetime input
		yearmonth_as_datetime0 = datetime.datetime.strptime(row['Date'][:10], "%m/%d/%Y")
		# collapse that date into a yearmonth, set at midnight of the first of the month
		yearmonth_as_datetime1 = datetime.datetime(
			year=yearmonth_as_datetime0.year,
			month=yearmonth_as_datetime0.month,
			day=1,
			hour=0,
			minute=0,
			second=0)

		# reformat for appending into input0
		yearmonth_out = yearmonth_as_datetime1
		border_out = CleanWhitespace(row['Border'])
		measure_out = CleanWhitespace(row['Measure'])
		value_out = int(row['Value'])

		# add to set if unique value
		unique_values_date.add(yearmonth_as_datetime1)

		# prepare output: keep only border, date, measure, and value
		output_keys = ['Border', 'Date', 'Measure', 'Value']
		output_values = [border_out,
						 yearmonth_out,
						 measure_out,
						 value_out
						 ]

		# add rows (dicts) to input0 (list of dicts)
		input0.append(dict(zip(output_keys, output_values)))





#########
#STEP 2 : PAD input DATASET WITH ZEROS WHERE NECESSARY
#########
#Before summarizing, I must pad data with zeros for dates that do not appear
# for a given border*measure, if date doesnt exist, impute values with zero


#determine the range of dates that must exist for each border*measure
firstmonth=min(unique_values_date)
lastmonth=max(unique_values_date)


#I want to groupby . this necessitates sorting
sorted_input = sorted(input0, key=operator.itemgetter('Border', 'Measure'))

summarised_data = []
for i,j in itertools.groupby(sorted_input, key=lambda x:(x['Border'], x['Measure'])):
	#i is a tuple that defines the key of the groupby
	#j is a grouped object that, when converted to list, is a list of dicts 
	## this list of dicts is all the available data rows for that border*measure 
	## that is the sub-object we are iterating by
	#print(i)
	#print(list(j))
	j_as_list = list(j)
	#print(j_as_list['Date'] in d for d in date_range)
	#within each list(j), if 
	
	#summarised_data = []

	running_total_previous_month = 0
	index_this_month = 1
	this_month_datetime = firstmonth

	while this_month_datetime <= lastmonth:
		dictlist_augmented = PadDictlistWithCustomValues(
			key='Date', 
			value = this_month_datetime, 
			my_dictlist = j_as_list, ##i can probably filter this if it would make execution faster but only if this fxn can handle an empty list
			key_to_impute = 'Value', 
			imputed_value = 0.00)
		if index_this_month == 1:
			moving_average = 0.00
		else:
			moving_average = float(running_total_previous_month)/float(index_this_month-1)
		


		total_this_month = sum(int(row['Value']) for row in dictlist_augmented if row['Date'] == this_month_datetime)

		returndict = {'Border':dictlist_augmented[0]['Border'], 
					'Measure':dictlist_augmented[0]['Measure'], 
					'Date':DateToString(this_month_datetime), 
					'Value':total_this_month,
					'Average': int(my_round(moving_average))
					}

		summarised_data = list(filter(lambda d: d['Value'] > 0.0001, summarised_data))
		summarised_data.append(returndict)
		


		index_this_month = index_this_month + 1
		running_total_previous_month = running_total_previous_month + total_this_month
		this_month_datetime =  IncreaseMonthByM(this_month_datetime,1)






summarised_data = sorted(summarised_data, key=operator.itemgetter('Date','Value','Measure','Average'), reverse=True)
print(summarised_data)




with open(output_filepath, 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, 
    	fieldnames = ['Border','Date','Measure','Value','Average'])
    dict_writer.writeheader()
    dict_writer.writerows(summarised_data)

