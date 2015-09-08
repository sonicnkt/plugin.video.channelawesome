
__author__ = 'Nils Thiele'
import re, urllib2, sqlite3
from bs4 import BeautifulSoup

db_url = 'http://channelawesome.com/category/videos/producers/calluna/'
db_name = 'calluna'
show_name = 'Calluna'
local_db = 'test.db'


conn = sqlite3.connect(local_db)
c = conn.cursor()

c.execute('SELECT id, name, url, thumb, plot, airdate FROM {}'.format(db_name))
video_info = c.fetchall()
conn.close()
print video_info
for id, name, url, thumbnail, plot, airdate in video_info:
    print str(id)+'. '+name