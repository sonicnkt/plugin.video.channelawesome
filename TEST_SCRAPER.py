#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Nils Thiele'
import re, urllib2, sqlite3
from bs4 import BeautifulSoup

db_url = 'http://channelawesome.com/category/videos/producers/calluna/'
db_name = 'calluna'
show_name = 'Calluna'
local_db = 'test.db'
update = True

def grab_url(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:24.0) Gecko/20100101 Firefox/24.0')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link

def convert_airdate(airdate):
    airdate = re.compile('(.+?)\s([0-9]{1,2}),\s([0-9]{4})').findall(airdate)
    months = {'January': '01',
              'February': '02',
              'March': '03',
              'April': '04',
              'May': '05',
              'June': '06',
              'July': '07',
              'August': '08',
              'September': '09',
              'October': '10',
              'November': '11',
              'December': '12'}
    year = airdate[0][2]
    month = months[airdate[0][0]]
    day = airdate[0][1]
    if len(day) < 2:
        day = '0' + day
    #date = year + '-' + month + '-' + day
    date = day + '.' + month + '.' + year

    return date

conn = sqlite3.connect(local_db)
c = conn.cursor()

# Create DB entries
c.execute('CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY, name TEXT, url TEXT, thumb TEXT, plot TEXT, airdate TEXT)'.format(db_name))
c.execute('CREATE TABLE IF NOT EXISTS show_list (table_name  TEXT PRIMARY KEY, show_name TEXT, show_url TEXT)')
c.execute('INSERT OR REPLACE INTO show_list VALUES ("{}", "{}", "{}")'.format(db_name, show_name, db_url))
# Get max page number
content = grab_url(db_url)
matchc = re.compile('class="pages">Page (.+?) of (.+?)</span>').findall(content)
lastp = int(matchc[0][1])
video_list = []
counter = 0
in_db = 0
for i in range(1, lastp + 1):
    percent = int( (100 / lastp) * i)
    message = "Scraping page " + str(i) + " out of " + str(lastp)
    url = db_url + 'page/' + str(i) # Modified "/page/" to "page/"
    page_content = grab_url(url)
    # Match String 1: URL, Name, Thumbnail
    match_str1 = 'href="(.+?)" title="Permalink to (.+?)" rel="bookmark">\n\t\t\t\t<img width="300" height="160" src="(.+?)"'
    # Match String 2: Plot
    match_str2 = '<div class="entry">\n\t\t\t<p>(.+?)<\/p>'
    # Match String Aired-Date
    match_str3 = '<span class="tie-date">(.+?)<\/span>\s\s\s<span class="post'
    match1 = re.compile(match_str1).findall(page_content)
    match2 = re.compile(match_str2).findall(page_content)
    match3 = re.compile(match_str3).findall(page_content)
    # Convert Aired-Dates
    airdates = []
    for entry in match3:
        airdates.append(convert_airdate(entry))
    # Combine those 3 tuples:
    video_info = []
    for num, entry in enumerate(match1):
        new_entry = ()
        new_entry = new_entry + entry + (match2[num],) + (airdates[num],)
        video_info.append(new_entry)
    if update:
        for url, name, thumbnail, plot, airdate in video_info:
            counter = counter + 1
            print counter
            c.execute('SELECT airdate FROM {} WHERE name="{}"'.format(db_name, name))
            test = c.fetchone()
            if test is None:
                entry = (name, url, thumbnail, plot, airdate)
                print 'Episode: "{}" not in DB, adding to update list now!'.format(name)
                video_list.append(entry)
            else:
                print 'Episode: "{}" Allready in DB, breaking loop now!'.format(name)
                in_db = True
                break
    else:
        for url, name, thumbnail, plot, airdate in video_info:
            counter = counter + 1
            print counter
            entry = (name, url, thumbnail, plot, airdate)
            video_list.append(entry)
    if in_db:
        break


if len(video_list) > 0:
    video_list.reverse()
    c.executemany('INSERT INTO {} (name, url, thumb, plot, airdate) VALUES (?,?,?,?,?)'.format(db_name), video_list)
    conn.commit()
else:
    print 'No Update available!'
conn.close()
print 'Done!'