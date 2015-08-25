__author__ = 'Nils Thiele'
import re, urllib2
from bs4 import BeautifulSoup
import html2text

url = 'http://channelawesome.com/blockbuster-buster-top-10-radical-re-makes/'
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
req = urllib2.Request(url)
req.add_header('User-Agent', user_agent)
response = urllib2.urlopen(req)
link = response.read()
response.close()
#soup = BeautifulSoup(link, "html.parser")
#header = soup.find("span", {"itemprop" : "name"}).text
#entry = soup.find("div", {"class" : "entry"}).text
#entry = soup.find("div", class_='entry').text
#print header
#print entry
match_str1 = '<iframe frameborder="[0-1]" width="[0-9]{3}" height="[0-9]{3}" src="(//www.dailymotion.com/embed/video/.+?)" allowfullscreen></iframe>'

match1 = re.compile(match_str1).findall(link)

url = match1[0]
url = 'http:' + url
video_id = url.split('/')[-1]

req = urllib2.Request(url)
req.add_header('User-Agent', user_agent)
response = urllib2.urlopen(req)
link = response.read()
response.close()
dailymotion =  link.replace('\\', '')
match_mp4_str1= '"video\/mp4","url":"(http:\/\/www.dailymotion.com\/cdn\/H264-[0-9]{{3}}x[0-9]{{3}}\/video\/{}.mp4\?auth=.+?)"'.format(video_id)
match_mp4_str2= '"(http:\/\/www.dailymotion.com\/cdn\/H264-320x240\/video\/x31i0ts.mp4\?auth=.+?)"'
match_mp4 = re.compile(match_mp4_str1).findall(dailymotion)
print match_mp4[-1]