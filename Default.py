# ChannelAwesome Addon
import urllib
import urllib2
import socket
import re
import sys
import os
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc
from bs4 import BeautifulSoup

addonID = 'plugin.video.channelawesome'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
addonDir = xbmc.translatePath(addon.getAddonInfo('path'))
icon = os.path.join(addonDir, 'icon.png')


def CATEGORIES():
    addDir('Latest Videos', 'http://channelawesome.com', 2, icon)
    addDir('All Shows', 'http://channelawesome.com', 1, '')
    addDir('Search ChannelAwesome.com', '', 5, '')
    addDir('Favorites', '', 6, '')
    ##
    addDir('Nostalgia Critic', 'http://channelawesome.com/category/videos/channelawesome/dougwalker/nostalgia-critic',
           2, '')
    addDir('Disneycember', 'http://channelawesome.com/tag/disneycember', 2, '')
    addDir('Anime Abandon', 'http://channelawesome.com/tag/anime-abandon', 2, '')
    addDir('Cinemas Snob', 'http://channelawesome.com/tag/cinema-snob', 2, '')
    addDir('Brad Tries', 'http://channelawesome.com/tag/brad-tries', 2, '')
    addDir('Linkara', 'http://channelawesome.com/category/videos/producers/linkara-producers', 2, '')
    # Add your own favorite shows like this!


def ALLSHOWS(url):
    content =  grab_url(url)
    match = re.compile(
        '<li id="menu-item-.+?" class="ubermenu-item ubermenu-item-type-taxonomy ubermenu-item-object-category '
        'ubermenu-item-.+? ubermenu-item-auto ubermenu-item-normal ubermenu-item-level-2 ubermenu-column '
        'ubermenu-column-auto" ><a class="ubermenu-target ubermenu-item-layout-default ubermenu-item-layout-text_only" '
        'href="(.+?)"><span class="ubermenu-target-title ubermenu-target-text">(.+?)</span>').findall(content)
    xbmcplugin.addSortMethod(int(sys.argv[1]), 1)
    for url, name in match:
        addDir2(name, url, 2, '')

def LISTVIDEOS(url):
    baseurl = url
    if '/?s=' in url:
        is_search = 1
    else:
        is_search = 0

    content = grab_url(url)

    # Match String 1: URL, Name, Thumbnail
    match_str1 = 'href="(.+?)" title="Permalink to (.+?)" rel="bookmark">\n\t\t\t\t<img width="300" height="160" src="(.+?)"'
    # Match String 2: Plot
    match_str2 = '<div class="entry">\n\t\t\t<p>(.+?)<\/p>'

    match1 = re.compile(match_str1).findall(content)
    match2 = re.compile(match_str2).findall(content)
    #Find Airdate: match2=re.compile('</a></span>\n\t\n\t\t\n\t<span class="tie-date">(.+?)</span>').findall(link)
    # Combine those two tuples:
    video_info = []
    for num,entry in enumerate(match1):
        new_entry = ()
        new_entry = new_entry + entry + (match2[num],)
        video_info.append(new_entry)

    # Get current page and max page number
    matchc = re.compile('class="pages">Page (.+?) of (.+?)</span>').findall(content)
    if matchc == []:
        print 'This show or search result only has one page'  #DEBUG INFO
        for url, name, thumbnail, plot in video_info:
            addLink(name, url, 4, thumbnail, plot)
        return
    else:
        curp = int(matchc[0][0])
        nextp = curp + 1
        prevp = curp - 1
        lastp = int(matchc[0][1])
        position = 'Page ' + str(curp) + ' of ' + str(lastp)
        addDir(position, baseurl, 7, '')

    if lastp < 100 and curp == 1 and is_search == 0:
        addDir('List All   (Warning!! This may take time!)', baseurl, 3, '')

    for url, name, thumbnail, plot in video_info:
        addLink(name, url, 4, thumbnail, plot)

    if is_search == 0:
        if '/page/' in baseurl:
            baseurl = re.sub("/page/.+", "/page/", baseurl)
        else:
            baseurl = baseurl + '/page/'

        if curp == 1:
            addDir('Prev Page (' + str(lastp) + ' of ' + str(lastp) + ')', baseurl + str(lastp), 2, '')
        else:
            addDir('Prev Page (' + str(prevp) + ' of ' + str(lastp) + ')', baseurl + str(prevp), 2, '')

        if curp < lastp:
            addDir('Next Page (' + str(nextp) + ' of ' + str(lastp) + ')', baseurl + str(nextp), 2, '')
    else:
        sstring = re.sub(".+?/?s=", "/?s=", baseurl)
        surl = 'http://channelawesome.com/page/'
        if curp == 1:
            addDir('Prev Page (' + str(lastp) + ' of ' + str(lastp) + ')', surl + str(lastp) + sstring, 2, '')
        else:
            addDir('Prev Page (' + str(prevp) + ' of ' + str(lastp) + ')', surl + str(prevp) + sstring, 2, '')

        if curp < lastp:
            addDir('Next Page (' + str(nextp) + ' of ' + str(lastp) + ')', surl + str(nextp) + sstring, 2, '')


def LISTALL(url): # WIP - Veeeery sloooow
    baseurl = url
    content = grab_url(url)
    # Get max page number
    matchc = re.compile('class="pages">Page (.+?) of (.+?)</span>').findall(content)
    lastp = int(matchc[0][1])

    for i in range(1, lastp + 1):
        url = baseurl + '/page/' + str(i)
        page_content = grab_url(url)
        match1 = re.compile(
            'href="(.+?)" title="Permalink to (.+?)" rel="bookmark">\n\t\t\t\t<img width="300" height="160" src="(.+?)"').findall(
            page_content)
        for url, name, thumbnail in match1:
            addLink(name, url, 4, thumbnail)


def SEARCHSITE(name):
    dialog = xbmcgui.Dialog()
    d = dialog.input('Search ChannelAwesome.com', type=xbmcgui.INPUT_ALPHANUM)
    d = d.replace(" ", "+")
    if d == '':
        CATEGORIES()
    else:
        LISTVIDEOS('http://channelawesome.com/?s=' + d)

def JUMPTO(url):
    dialog = xbmcgui.Dialog()
    d = dialog.input('Search ChannelAwesome.com', type=xbmcgui.INPUT_NUMERIC)
    print 'Dialog Input: ' + d
    if d == '':
        print 'No Input'
        xbmc.executebuiltin('Back')
    if ('/?s=' in url): # If URL is result of Search
        sstring = re.sub(".+?/?s=", "/?s=", url)
        surl = 'http://channelawesome.com/page/'
        goto_url = surl + d + sstring
    else:
        if '/page/' in url:
            baseurl = re.sub("/page/.+", "/page/", url)
        else:
            baseurl = url + '/page/'
        goto_url = baseurl + d
    if d:
        LISTVIDEOS(goto_url)

def FAVORITES(name):
    dialog = xbmcgui.Dialog()
    dialog.ok('Favorites', 'Not working yet! Sorry!!')
    CATEGORIES()


def RESOLVELINK(url): # Grab the urls of the embedded videos
    content = grab_url(url)
    screenwave = '<script src="(http:\/\/player[0-9].screenwavemedia.com/player.php\?id=.+)"><\/script>'
    youtube = 'youtube.com/embed/(.+?)"'
    dailymotion = '<iframe frameborder="[0-1]" width="[0-9]{3}" height="[0-9]{3}" src="(//www.dailymotion.com/embed/video/.+?)" allowfullscreen></iframe>'
    sw_match = re.compile(screenwave).findall(content)
    yt_match = re.compile(youtube).findall(content)
    dm_match = re.compile(dailymotion).findall(content)
    videos = sw_match + yt_match + dm_match
    if len(videos) > 1:
        print 'More than one Video on this page'
        video_lst = videos
        select_lst = []
        dialog = xbmcgui.Dialog()
        num = 0
        for entry in video_lst:
            num = num + 1
            selection = 'Part ' + str(num)
            select_lst.append(selection)
        print video_lst
        ret = dialog.select('Choose Part', select_lst)
        if ret == -1:
            print 'Canceled'
            dialog = xbmcgui.Dialog()
            dialog.notification('Selection canceled', 'No Video selected', xbmcgui.NOTIFICATION_INFO, 5000)
        else:
            print ret
            return get_video(video_lst[ret])
    elif len(videos) == 1:
        url = videos[0]
        print url
        return get_video(url)
    else:
        soup = BeautifulSoup(content, "html.parser")
        header = soup.find("span", {"itemprop" : "name"}).text
        entry = soup.find("div", class_='entry').text
        showText(header, entry)
        #listitem = xbmcgui.ListItem(path=url)
        #listitem.setProperty('isPlayable', 'false')
        return #xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

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

def showText(heading, text):
    id = 10147
    xbmc.executebuiltin('ActivateWindow(%d)' % id)
    xbmc.sleep(100)
    win = xbmcgui.Window(id)
    retry = 50
    while (retry > 0):
        try:
            xbmc.sleep(10)
            retry -= 1
            win.getControl(1).setLabel(heading)
            win.getControl(5).setText(text)
            return
        except:
            pass

def grab_url(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:24.0) Gecko/20100101 Firefox/24.0')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link

def get_video(url):
    # Determine if ScreenWave, DailyMotion or Youtube
    if url.startswith('http://play'): # ScreenWave
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
        listitem = xbmcgui.ListItem(path=video_url)
        return xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
    elif url.startswith('//www.daily'): #DailyMotion
        url = 'http:' + url
        video_id = url.split('/')[-1]
        content = grab_url(url)
        content =  content.replace('\\', '') # Remove all the backslashes from the htmlcode for easier re.compile
        match_mp4_str = '"video\/mp4","url":"(http:\/\/www.dailymotion.com\/cdn\/H264-[0-9]{{3}}x[0-9]{{3}}\/video\/{}.mp4\?auth=.+?)"'.format(video_id)
        match_mp4 = re.compile(match_mp4_str).findall(content)
        video_url =  match_mp4[-1] # Pick the last Found entry in the match, this is always best quality available
        print 'Video URL: ', video_url # Debug Info
        listitem = xbmcgui.ListItem(path=video_url)
        return xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

    else: # YouTube
        youtube_id = url
        if "?" in youtube_id:
            youtube_id = youtube_id[:youtube_id.find("?")]
        print 'Youtube Video ID: ', youtube_id
        url = "plugin://plugin.video.youtube/?action=play_video&videoid=" + youtube_id
        listitem = xbmcgui.ListItem(path=url)
        return xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

def cleanName(name):
    name = name.replace("&#8217;", "'").replace("&#8211;", "-").replace("&amp;", "&").replace("&#8220;", "\"").replace(
        "&#8221;", "\"").replace("&#8230;", "...")
    name = name.strip()
    return name


def addLink(name, url, mode, iconimage, plot='Plot Info'):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(cleanName(name), iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "plot" : cleanName(plot)})  #, "aired": date } )
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

def addDir2(name, url, mode, iconimage):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.addContextMenuItems([('Add to Addon Favorites', 'RunScript(TEMP)',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


params = get_params()
url = None
name = None
mode = None

try:
    url = urllib.unquote_plus(params["url"])
except:
    pass
try:
    name = urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode = int(params["mode"])
except:
    pass

print "Mode: " + str(mode)
print "URL: " + str(url)
print "Name: " + str(name)

if mode == None:
    print ""
    CATEGORIES()

elif mode == 1:
    print ""
    ALLSHOWS(url)

elif mode == 2:
    print "" + url
    LISTVIDEOS(url)

elif mode == 3:
    print "" + url
    LISTALL(url)

elif mode == 4:
    print "" + url
    RESOLVELINK(url)

elif mode == 5:
    print "" + name
    SEARCHSITE(name)

elif mode == 6:
    print "" + name
    FAVORITES(name)

elif mode == 7:
    print "" + name
    JUMPTO(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
