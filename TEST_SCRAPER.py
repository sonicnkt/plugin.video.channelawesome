
__author__ = 'Nils Thiele'
import re, urllib2
from bs4 import BeautifulSoup

url = 'http://channelawesome.com/category/videos/channelawesome/dougwalker/nostalgia-critic/'
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
req = urllib2.Request(url)
req.add_header('User-Agent', user_agent)
response = urllib2.urlopen(req)
content = response.read()
response.close()

def convert_airdate(airdate):
    airdate = re.compile('(.+?)\s([0-9]{1,2}),\s([0-9]{4})').findall(airdate)
    months = {'January': '01',
              'Fabruary': '02',
              'March': '03',
              'April': '04',
              'May': '05',
              'June': '06',
              'July': '07',
              'August': '08',
              'September': '09',
              'October': '10',
              'November': '11',
              'Dezember': '12'}
    year = airdate[0][2]
    month = months[airdate[0][0]]
    day = airdate[0][1]
    if len(day) < 2:
        day = '0' + day
    date = year + '-' + month + '-' + day
    return date


#Matches URL,NAME,THUMB
match_str1 = 'href="(.+?)" title="Permalink to (.+?)" rel="bookmark">\n\t\t\t\t<img width="300" height="160" src="(.+?)"'
#Matches PLOT
match_str2 = '<div class="entry">\n\t\t\t<p>(.+?)<\/p>'
#Matches airdate
match_str3 = '<span class="tie-date">(.+?)<\/span>\s\s\s<span class="post'
match1 = re.compile(match_str1).findall(content)
match2 = re.compile(match_str2).findall(content)
match3 = re.compile(match_str3).findall(content)
#Find Airdate: match2=re.compile('</a></span>\n\t\n\t\t\n\t<span class="tie-date">(.+?)</span>').findall(link)
# Combine those two tuples:
video_info = []
airdates = []
for entry in match3:
    airdates.append(convert_airdate(entry))

for num,entry in enumerate(match1):
    new_entry = ()
    new_entry = new_entry + entry + (match2[num],) + (airdates[num],)
    video_info.append(new_entry)
print len(video_info)
print video_info