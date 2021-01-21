import pandas as pd
import time

# CLEANING TEMP DF

temp_hour = pd.read_csv("csv/l-mesuretemprivieres-d-r28.csv")

print(temp_hour.tail())
print(temp_hour.info())
# no null value in temp

# type of Teau (or Theo lol) is object, we're gonna convert it to float64
temp_hour["Teau"] = pd.to_numeric(temp_hour["Teau"].str.replace(',', '.'))

# we're gonna sort temp by id_sonde then by date_mesure
temp_hour = temp_hour.sort_values(by=["date_mesure", "id_sonde"])
print(temp_hour.head())
print(temp_hour.tail())

# we're gonna check for each date if we have all Teau
# it can takes nearly 10 minutes
# after check we have all Teau, no data missing
"""
tab_dates = pd.unique(temp["date_mesure"])
print(len(tab_dates))
x = 0
start = time.time()
for date in tab_dates:
	count = temp[temp["date_mesure"] == date].count()[0]
	if count != 17:
		print("error", count, date)
	x += 1
	if x % 1000 == 0:
		print(x, "done in", time.time() - start)
print("check done")
"""

# column id_mesure isn't usefull in my case, gonna drop it
temp_hour = temp_hour.drop(["id_mesure"], axis=1)

# save the cleaned temp
temp_hour.to_csv("csv/temp_hour.csv")

# CREATE TEMP / DAY

# create new df with temp / day
temp_hour = pd.read_csv("csv/temp_hour.csv")

x = 0

nb_hours = 0
values = [0] * 17

tab_mean = []
tab_date = [temp_hour["date_mesure"][0].split(" ")[0]]

while x < len(temp_hour):
    date = temp_hour["date_mesure"][x].split(" ")[0]
    
    if date != tab_date[-1]:
        for value in values:
            tab_mean.append(value / nb_hours)
        tab_date.append(date)
        values = [0] * 17
        nb_hours = 0

    y = 0
    while y < 17:
        values[y] += temp_hour["Teau"][x + y]
        y += 1
        
    x += 17
    nb_hours += 1
        
for value in values:
    tab_mean.append(value / nb_hours)
    
dates = []
for date in tab_date:
    i = 0
    while i < 17:
        dates.append(date)
        i += 1

dic = {
        "date_mesure" : dates,
        "Teau" : tab_mean,
        "id_sonde" : [104, 109, 771, 813, 815, 816, 817, 818, 819, 820, 821, 823, 824, 825, 827, 828, 830] * len(tab_date)
    }
temp_day = pd.DataFrame(data=dic)
print(temp_day.info())
print(temp_day.head())
print(temp_day.tail())
temp_day.to_csv("csv/temp_day.csv")

# CREATE TEMP / MONTH

# create new df with temp / month
temp_day = pd.read_csv("csv/temp_day.csv")
x = 0

nb_days = 0
values = [0] * 17

tab_mean = []
tab_date = [temp_day["date_mesure"][0][0:7]]

while x < len(temp_day):
    date = temp_day["date_mesure"][x][0:7]
    
    if date != tab_date[-1]:
        for value in values:
            tab_mean.append(value / nb_days)
        tab_date.append(date)
        values = [0] * 17
        nb_days = 0

    y = 0
    while y < 17:
        values[y] += temp_day["Teau"][x + y]
        y += 1
        
    x += 17
    nb_days += 1
        
for value in values:
    tab_mean.append(value / nb_days)
    
dates = []
for date in tab_date:
    i = 0
    while i < 17:
        dates.append(date)
        i += 1

dic = {
        "date_mesure" : dates,
        "Teau" : tab_mean,
        "id_sonde" : [104, 109, 771, 813, 815, 816, 817, 818, 819, 820, 821, 823, 824, 825, 827, 828, 830] * len(tab_date)
    }
temp_month = pd.DataFrame(data=dic)
print(temp_month.info())
print(temp_month.head())
print(temp_month.tail())
temp_month.to_csv("csv/temp_month.csv")

# CLEANING RES DF

temp_hour = pd.read_csv("csv/temp_hour.csv")
res = pd.read_csv("csv/l-reseautemprivieres-d-r28.csv")

print(res.tail())
print(res.info())

# index 33 has a NaN value id_sonde, we're gonna drop it
res = res.drop([33])

# there are many stations in res we're not gonna use
# we have temp of 17 stations and we have 33 stations in res
# we're gonna drop those stations in res
tab_id = pd.unique(temp_hour["id_sonde"])

tab = res["id_sonde"]
for i in tab:
    if not int(i) in tab_id:
        res = res.drop(res.index[res["id_sonde"] == i])

res["id_sonde"] = res["id_sonde"].astype(int)
res.reset_index(drop=True, inplace=True)
print(res.tail())

tab_id2 = pd.unique(res["id_sonde"])
if tab_id.all() != tab_id2.all():
	print("not same id_sonde")
else:
	print("same id_sonde in both dataframes")

# some lib_sonde have spaces at then end of the sring, we're gonna drop those spaces
tab_lib = pd.unique(res["lib_sonde"])
for lib in tab_lib:
	new_lib = False
	size = len(lib)
	while lib[size - 1] == " ":
		new_lib = lib[0:size-1]
		size = len(new_lib)
	if new_lib != False:
		res.loc[res["lib_sonde"] == lib, ["lib_sonde"]] = new_lib

# we could merge the two dataframes but that would takes so much more space on disk for not much

# save the cleaned dataframe res
res.to_csv("csv/reseau.csv")
