#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 20 19:09:15 2020

@author: subhamoy and andres
"""

import requests 
from bs4 import BeautifulSoup
import julian
from datetime import datetime

###local folder to save the data  
root = '/Users/subhamoy/Documents/swri_projects/sep_prediction/codes/'
###http location to access the files
url = "https://satdat.ngdc.noaa.gov/sxi/archive/fits/"


import os
import csv

list_month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
goes_ar = ['goes12', 'goes13', 'goes14', 'goes15']  ###satellites to look for

with open(root+'sepserver_goes_events_clean.csv', encoding ='ISO-8859-1') as f:  ####read csv to loop through the event identifiers
  reader = csv.reader(f)
  for row in reader:
      if row[5][3:] in list_month:
          #print(row[1]+'-'+row[5]+'-'+row[6])
          st = str(list_month.index(row[5][3:])+1)
          #print(st.zfill(2))
          identifier = row[1] + st.zfill(2) + row[5][:2] + row[6][:-3].zfill(2) + row[6][-2:]   ###create the identifier in YYYYMMDDHHMM format from SEP start time
          print(identifier)

          dt = datetime(int(identifier[:4]),
              int(identifier[4:6]),
              int(identifier[6:8]),
              int(identifier[8:10]),
              int(identifier[10:12]),
              0,0)
          print(dt)
          jd = julian.to_jd(dt, fmt='jd')   ###convert to julian date for easy search process
          print(jd)
          t_array = []
          for i in range(4):      ####array of date folder strings
              t = julian.from_jd(jd-i, fmt='jd')
              month = str(t.month).zfill(2)
              day = str(t.day).zfill(2)   
              ar = str(t.year) + '/' + month + '/' + day + '/'
              t_array.append(ar)
          print(t_array)
          for goes in goes_ar:
              path = root + identifier + '/x_ray/' +goes
              for i in range(4):
                  archive_url = url + goes + '/' + t_array[i]
                  r = requests.get(archive_url)
                  soup = BeautifulSoup(r.content,'html5lib')
                  links = soup.findAll('a')
                  for link in links:
                      try:
                          l=link['href']
                          if l.startswith('SXI') and l.endswith('FTS'):
                              yyyy = int(l[4:8])
                              mm = int(l[8:10])
                              dd = int(l[10:12])
                              hh = int(l[13:15])
                              mn = int(l[15:17])
                              ss = int(l[17:19])
                              dt_l = datetime(yyyy,mm,dd,hh, mn, ss, 0)
                              jd_l = julian.to_jd(dt_l, fmt='jd')
                              if jd_l>=(jd-3) and jd_l<=jd and l[23:24]=='B':
                                  if os.path.exists(root + identifier)==False:
                                      os.mkdir(os.path.join(root, identifier))
                                  if os.path.exists(root + identifier + '/x_ray/')==False:
                                      os.mkdir(root + identifier + '/x_ray/')
                                  if os.path.exists(path)==False:
                                      os.mkdir(path)
                                  image_url = archive_url + l
                                  rr = requests.get(image_url)
                                  with open(path+'/'+l,'wb') as f:
                                      f.write(rr.content)
                      except KeyError:
                          print(link)
