import urllib2
import re
import sys

# Gets KODI Plugin Paramter and turns it into a dictionary
def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param

def grab_url(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:24.0) Gecko/20100101 Firefox/24.0')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link

def get_video(url):
    # Determine if ScreenWave, DailyMotion or Youtube
    print url
    if url.startswith('http://play'): # ScreenWave
        if "/play/" in url:
            url = url.replace('/play/', '/')
        content = grab_url(url)
        video_srv = re.compile('var\sSWMServer\s=\s"(.+?)"').match(content).group(1)
        video_id = re.compile('\'vidid\':  \"(.+?)\",').findall(content)
        if len(video_id) > 1:
            print 'More than one Video found'
        else:
            video_id = video_id[0]
        quality = '_hd1.mp4'
        video_url = 'http://' + video_srv + '/vod/' + video_id + quality
        print 'Video URL: ', video_url
        return video_url
    elif url.startswith('//www.daily'): #DailyMotion
        url = 'http:' + url
        video_id = url.split('/')[-1]
        content = grab_url(url)
        content =  content.replace('\\', '') # Remove all the backslashes from the htmlcode for easier re.compile
        match_mp4_str = '"video\/mp4","url":"(http:\/\/www.dailymotion.com\/cdn\/H264-[0-9]{{3}}x[0-9]{{3}}\/video\/{}.mp4\?auth=.+?)"'.format(video_id)
        match_mp4 = re.compile(match_mp4_str).findall(content)
        video_url =  match_mp4[-1] # Pick the last Found entry in the match, this is always best quality available
        print 'Video URL: ', video_url # Debug Info
        return video_url

    else: # YouTube
        youtube_id = url
        if "?" in youtube_id:
            youtube_id = youtube_id[:youtube_id.find("?")]
        print 'Youtube Video ID: ', youtube_id
        url = "plugin://plugin.video.youtube/?action=play_video&videoid=" + youtube_id
        return url

def cleanName(name):
    name = name.replace("&#8217;", "'").replace("&#8211;", "-").replace("&amp;", "&").replace("&#8220;", "\"").replace(
        "&#8221;", "\"").replace("&#8230;", "...")
    name = name.strip()
    return name

def convert_airdate(airdate, mode):
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
    if mode == 'date':
        date = day + '.' + month + '.' + year
    elif mode == 'aired':
        date = year + '-' + month + '-' + day
    #date = day + '.' + month + '.' + year
    return date

def scrape_data(page_content, mode='None'):
    # Match String 1: URL, Name, Thumbnail
    match_str1 = 'href="(.+?)" title="Permalink to (.+?)" rel="bookmark">\n\t\t\t\t<img width="300" height="160" src="(.+?)"'
    # Match String 2: Plot
    match_str2 = '<div class="entry">\n\t\t\t<p>(.+?)<\/p>'
    #Matches airdate
    match_str3 = '<span class="tie-date">(.+?)<\/span>\s\s\s<span class="post'
    match1 = re.compile(match_str1).findall(page_content)
    match2 = re.compile(match_str2).findall(page_content)
    if mode == 'DB':
        match3 = re.compile(match_str3).findall(page_content)
        #Convert Aired-Date format
        #airdates = []
        #for entry in match3:
        #    airdates.append(convert_airdate(entry))
    # Combine those tuples:
    video_info = []
    for num, entry in enumerate(match1):
        new_entry = ()
        if mode == 'DB':
            new_entry = new_entry + entry + (match2[num],) + (match3[num],)
        else:
            new_entry = new_entry + entry + (match2[num],)
        video_info.append(new_entry)
    return video_info