import requests
import json
from bs4 import BeautifulSoup
from collections import OrderedDict
from github import Github
from geojson_rewind import rewind


page = requests.get("https://docs.google.com/spreadsheets/d/1wQVypefm946ch4XDp37uZ-wartW4V7ILdg-qYiDXUHM/htmlview?usp=sharing&sle=true")

table_data = [[cell.text for cell in row("td")]
                         for row in BeautifulSoup(page.content, 'html.parser')("tr")]

table_data = filter(None, table_data)

updated_data = []
for x in table_data:
  if x[2] == "1/26/2020 11:00 AM":
    break
  else:
    updated_data.append(x)

def check(x):
  if x[0] == "Province/State":
    return False
  else:
    return True

updated_data = filter(check, updated_data)

def convert_lists(lists):
  new_list = []
  for x in lists:
    new_entry = {
      "province": "",
      "country": "",
      "last_update_utc": "",
      "confirmed": 0,
      "deaths": 0,
      "recovered": 0
    }
    ret_obj = new_entry
    ret_obj["province"] = x[0]
    ret_obj["country"] = x[1]
    ret_obj["last_update_utc"] = x[2]
    ret_obj["confirmed"] = x[3]
    ret_obj["deaths"] = x[4]
    ret_obj["recovered"] = x[5]
    new_list.append(ret_obj)
  return new_list


def clean_dictionary(dict):
  for x in dict:
    if x["confirmed"] == '':
      x["confirmed"] = 0
    if x["deaths"] == '':
      x["deaths"] = 0
    if x["recovered"] == '':
      x["recovered"] = 0
    else:
      next
  for x in dict:
    x["confirmed"] = int(x["confirmed"])
    x["deaths"] = int(x["deaths"])
    x["recovered"] = int(x["recovered"])
  return dict

final_to_json = clean_dictionary(convert_lists(updated_data))
## with open('./test.json', 'w') as fout:
#     json.dump(final_to_json , fout, indent=4)

# print(final_to_json[0])


def get_current_data(full_data):
  ret_val = []
  current_datetime = full_data[0]["last_update_utc"]
  print(current_datetime)
  for entry in full_data:
    if entry["last_update_utc"] == current_datetime:
      ret_val.append(entry)
    else:
      next
  return ret_val

current_data = get_current_data(final_to_json)


## function to find and return virus properties
def search_properties(country):
  ret_val = {
    "province": "",
    "country": country,
    "last_update_utc": current_data[0]["last_update_utc"],
    "confirmed": 0,
    "deaths": 0,
    "recovered": 0
  }

  for entry in current_data:
    if (country in entry["country"]):
      ret_val["confirmed"] = ret_val["confirmed"] + entry["confirmed"]
      ret_val["deaths"] = ret_val["deaths"] + entry["deaths"]
      ret_val["recovered"] = ret_val["recovered"] + entry["recovered"]

  return ret_val

def final_geojson():
  with open('countries.geo.json', 'r') as f:
    data = json.load(f)

  x = 0
  total_len = len(data["features"])
  for country in data["features"]:
    replace_properties = search_properties(country["properties"]["name"])
    country["properties"] = replace_properties
    country["id"] = x
    x= x + 1
  
  data = rewind(data)
  
  #Write result to a new file
  with open('latest.geojson', 'w') as f:
      json.dump(data, f, indent=4)


final_data = final_geojson()





    




