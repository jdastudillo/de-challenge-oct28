import copy 
import datetime
import itertools
from collections import OrderedDict


def CombineComponents(dict_in):
	keys = dict_in.keys()

	values = (dict_in[key] for key in keys)
	combinations = [dict(zip(keys, combination)) for combination in (itertools.product(*values))]
	return combinations

def RemoveKeysListofDicts(LOD_in,keygone):
	listofdicts = copy.deepcopy(LOD_in)
	for d in listofdicts:
		del d[keygone]
	return listofdicts
#There are only two ways to express hour:minute:second
hms_combinations = [
{'hour': '%H:', 'minute': '%M:', 'second': '%S', 'AMPM': ' %p'}, 
{'hour': '%I:', 'minute': '%M:', 'second': '%S'}
]
#In a datetime its possible to express hour:minute without seconds
hm_combinations = RemoveKeysListofDicts(hms_combinations, 'second')

#its a little more complicated for month/day/year
possible_day_formats = ['%d']
possible_month_formats = ['%b','%B', '%m']
possible_year_formats = ['%y', '%Y']
mdy_components = {
	'month' : possible_month_formats,
	'day' : possible_day_formats,
	'year' : possible_year_formats}
ymd_components = {
	'year' : possible_year_formats,
	'month' : possible_month_formats,
	'day' : possible_day_formats
	}
dmy_components = {
	'day' : possible_day_formats,
	'month' : ['%b','%B'], ## day can appear before month only when month is spelled
	'year' : possible_year_formats,
}

#We can sometimes have a weekday in the date
possible_weekday_formats = ['%a','%A']
amdy_components = {
	'weekday': possible_weekday_formats,
	'month' : possible_month_formats,
	'day' : possible_day_formats,
	'year' : possible_year_formats}
admy_components = {
	'weekday': possible_weekday_formats,
	'day' : possible_day_formats,
	'month' : ['%b','%B'], ## day can appear before month only when month is spelled
	'year' : possible_year_formats,
}

#START COMBINING DAY MARKERS
amdy_combinations = CombineComponents(amdy_components)
admy_combinations = CombineComponents(admy_components)
#its possible to express monthyearday without weekday
mdy_combinations = CombineComponents(mdy_components)
ymd_combinations = CombineComponents(ymd_components)
dmy_combinations = CombineComponents(dmy_components)
#its possible to express monthyear without day
my_combinations = RemoveKeysListofDicts(mdy_combinations, 'day')
ym_combinations = RemoveKeysListofDicts(ymd_combinations, 'day')
my_combinations = RemoveKeysListofDicts(dmy_combinations, 'day')



dictlist_all_time_combinations = hms_combinations + hm_combinations
dictlist_all_date_combinations = amdy_combinations + admy_combinations + mdy_combinations + ymd_combinations + dmy_combinations + my_combinations + ym_combinations + my_combinations
print(type(dictlist_all_date_combinations))

def DictlistToStringlist(dictlist_in):
	outlist = []
	for d in dictlist_in:
		stringyy = ''
		for v in d.values():
			stringyy = stringyy+ str(v)
		outlist.append(stringyy)
	return outlist

list_of_all_time_combinations = DictlistToStringlist(dictlist_all_time_combinations) + [''] #time is optional so add blank
list_of_all_date_combinations = [element.replace('%','/%')[1:] for element in DictlistToStringlist(dictlist_all_date_combinations)]


print(list_of_all_date_combinations)
print(list_of_all_time_combinations)


"""
or date_format in (
		"%m/%d/%Y %H:%M:%S %p", #default format from source
		'%A, %B %d %Y', #Common format that appears in excel
		'%A, %B %d, %Y' #another Common format that appears in excel



"""