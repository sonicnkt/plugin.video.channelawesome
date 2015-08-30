#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
import sqlite3


addonID = 'plugin.video.channelawesome'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
addonDir = xbmc.translatePath(addon.getAddonInfo('path'))
icon = os.path.join(addonDir, 'icon.png')
profile = xbmc.translatePath(addon.getAddonInfo('profile'))
local_db = os.path.join(profile, 'local_db.db')
print 'DB PATH: ' + local_db
pluginDir = sys.argv[0]

if not os.path.isfile(os.path.join(profile, 'settings.xml')):
    addon.setSetting(id='user_data_folder', value='True')
    print 'File wasnt there but is now'


def CATEGORIES():
    addDir('Latest Videos', 'http://channelawesome.com', 2, icon)
    addDir('All Shows', 'http://channelawesome.com', 1, '')
    addDir('Search ChannelAwesome.com', '', 5, '')
    addDir('Favorites', '', 6, '')
    addDir('Local Database', '', 8, '')

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
    #Matches airdate
    match_str3 = '<span class="tie-date">(.+?)<\/span>\s\s\s<span class="post'

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
        print 'name: ' + name
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

    progress = xbmcgui.DialogProgress()
    progress.create('Progress', 'Listing all videos....')
    for i in range(1, lastp + 1):
        percent = int( (100 / lastp) * i)
        message = "Scraping page " + str(i) + " out of " + str(lastp)
        progress.update( percent, "", message, "" )
        xbmc.sleep( 1000 )
        url = baseurl + '/page/' + str(i)
        page_content = grab_url(url)
        match1 = re.compile(
            'href="(.+?)" title="Permalink to (.+?)" rel="bookmark">\n\t\t\t\t<img width="300" height="160" src="(.+?)"').findall(
            page_content)
        for url, name, thumbnail in match1:
            addLink(name, url, 4, thumbnail)
        if progress.iscanceled():
            break
    progress.close()




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
        xbmc.executebuiltin("Back")
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

def DISPLAY_FAVS(url):
    print 'Display Favorite Shows'
    conn = sqlite3.connect(local_db)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS fav_list (fav_name TEXT PRIMARY KEY, fav_url TEXT)')
    c.execute('SELECT fav_name, fav_url FROM fav_list')
    shows = c.fetchall()
    conn.close()
    if len(shows):
        print shows # DEBUG
        xbmcplugin.addSortMethod(int(sys.argv[1]), 1)
        for fav_name, fav_url in shows:
            addDir3(fav_name, fav_url, 2, '')
        #xbmc.executebuiltin("Container.SetSortMethod(1)")
    else:
        dialog = xbmcgui.Dialog()
        dialog.notification('Info', 'No shows were added to the addon favorites.', xbmcgui.NOTIFICATION_INFO, 5000)
        CATEGORIES()


def FAVORITES(data):
    print 'Favorites function activated'
    print 'Parameter: ' + str(data)
    data = data.split(';')
    fav_mode = data[0].replace('MODE:', '')
    fav_name = data[1].replace('NAME:', '')
    fav_url = data[2].replace('URL:', '')
    print 'Mode:',fav_mode
    print 'Url:',fav_url
    print 'Show name:',fav_name

    # Connect to DB
    conn = sqlite3.connect(local_db)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS fav_list (fav_name TEXT PRIMARY KEY, fav_url TEXT)')

    if fav_mode == 'ADD':
        print 'Adding Favorite'
        c.execute('INSERT OR REPLACE INTO fav_list VALUES ("{}", "{}")'.format(fav_name, fav_url))
    else:
        print 'Removing Favorite'
        c.execute('DELETE FROM fav_list WHERE fav_name="{}"'.format(fav_name))
    conn.commit()
    conn.close()
    xbmc.executebuiltin("Container.Refresh")

def DISPLAY_DB(url):
    print 'Display stored Shows'
    conn = sqlite3.connect(local_db)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS show_list (table_name TEXT PRIMARY KEY, show_name TEXT, show_url TEXT)')
    c.execute("SELECT table_name, show_name FROM show_list")
    shows = c.fetchall()
    conn.close()
    if len(shows):
        print shows # DEBUG
        xbmcplugin.addSortMethod(int(sys.argv[1]), 1)
        for table_name, show_name in shows:
            addDir4(show_name, table_name, 9, '')
    else:
        dialog = xbmcgui.Dialog()
        dialog.notification('Info', 'No shows were added to the local db.', xbmcgui.NOTIFICATION_INFO, 5000)
        CATEGORIES()

def DISPLAY_DB_SHOW(table_name):
    conn = sqlite3.connect(local_db)
    c = conn.cursor()
    c.execute('SELECT name, url, thumb, plot, airdate FROM {}'.format(table_name))
    video_info = c.fetchall()
    conn.close()
    for name, url, thumbnail, plot, airdate in video_info:
        addLink(name.encode('ascii', 'ignore'), url, 4, thumbnail, plot.encode('ascii', 'ignore'), airdate)
        #addLink(name, url, 4, thumbnail, plot)
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)
    xbmc.executebuiltin("Container.SetSortMethod(2)")

def LOCAL_DB(data):
    print 'Scrape for DB Activated'
    print 'Parameter: ' + str(data)
    aborted = 0
    data = data.split(';')
    db_mode = data[0].replace('MODE:', '')
    db_name = data[1].replace('NAME:', '')
    db_url = data[2].replace('URL:', '')
    show_name = db_name
    db_name = db_name.replace(' ', '').lower()
    print 'Mode:',db_mode
    print 'Url:',db_url
    print 'Show name:',show_name
    print 'DB name:',db_name

    # Connect to DB
    conn = sqlite3.connect(local_db)
    c = conn.cursor()
    if db_mode == 'UPDATE':
        print 'UPDATE STARTED!!!'
        c.execute('SELECT show_url FROM show_list WHERE table_name="{}"'.format(db_name))
        show_url = c.fetchone()
        show_url = show_url[0]
        print 'Show URL: '+ show_url
        # Get max page number
        content = grab_url(show_url)
        matchc = re.compile('class="pages">Page (.+?) of (.+?)</span>').findall(content)
        lastp = int(matchc[0][1])

        # Progress Dialog
        progress = xbmcgui.DialogProgress()
        progress.create('Updating Show', 'Scraping new videos...')

        for i in range(1, lastp + 1):
            allready_in_db = 0
            percent = int( (100 / lastp) * i)
            message = "Scraping page " + str(i) + " out of " + str(lastp)
            progress.update( percent, "", message, "" )
            xbmc.sleep( 1000 )
            url = show_url + 'page/' + str(i) # Modified "/page/" to "page/"
            page_content = grab_url(url)

            # Match String 1: URL, Name, Thumbnail
            match_str1 = 'href="(.+?)" title="Permalink to (.+?)" rel="bookmark">\n\t\t\t\t<img width="300" height="160" src="(.+?)"'
            # Match String 2: Plot
            match_str2 = '<div class="entry">\n\t\t\t<p>(.+?)<\/p>'
            #Matches airdate
            match_str3 = '<span class="tie-date">(.+?)<\/span>\s\s\s<span class="post'

            match1 = re.compile(match_str1).findall(page_content)
            match2 = re.compile(match_str2).findall(page_content)
            match3 = re.compile(match_str3).findall(page_content)

            # Combine those 3 tuples:
            airdates = []
            for entry in match3:
                airdates.append(convert_airdate(entry))
            video_info = []
            for num, entry in enumerate(match1):
                new_entry = ()
                new_entry = new_entry + entry + (match2[num],) + (airdates[num],)
                video_info.append(new_entry)

            for url, name, thumbnail, plot, airdate in video_info:
                # Add Test to see if entry is allready there, if yes break this loop and set allready_in_db = True
                c.execute('SELECT airdate FROM {} WHERE name="{}"'.format(db_name, name))
                test = c.fetchone()
                if test is None:
                    print 'Entry: "{}" not in DB!'.format(name)
                    c.execute('INSERT INTO {} VALUES ("{}","{}","{}","{}","{}")'.format(db_name, name, url, thumbnail, plot, airdate))
                else: # Entry available in local DB
                    print 'Entry: "{}" allready in DB'.format(name)
                    print 'Stopping update progress but will commit changes to DB'
                    allready_in_db = 1
                    break

            if progress.iscanceled():
                aborted = True
                break
            if allready_in_db:
                break

        progress.close()
        if aborted:
            print 'Scrape was aborted!' # DEBUG INFO
        else:
            conn.commit()
        conn.close()

    elif db_mode == 'ADD':
        c.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="{}"'.format(db_name))
        test = c.fetchone()
        if test is None:
            print 'Table: "{}" does not exist in DB, i will continue'.format(db_name)
            # Create DB entries
            c.execute('CREATE TABLE IF NOT EXISTS {} (name TEXT PRIMARY KEY, url TEXT, thumb TEXT, plot TEXT, airdate TEXT)'.format(db_name))
            c.execute('CREATE TABLE IF NOT EXISTS show_list (table_name  TEXT PRIMARY KEY, show_name TEXT, show_url TEXT)')
            c.execute('INSERT OR REPLACE INTO show_list VALUES ("{}", "{}", "{}")'.format(db_name, show_name, db_url))
            # Get max page number
            content = grab_url(db_url)
            matchc = re.compile('class="pages">Page (.+?) of (.+?)</span>').findall(content)
            lastp = int(matchc[0][1])
            # Progress Dialog
            progress = xbmcgui.DialogProgress()
            progress.create('Adding Show to local Database', 'Scraping all videos...')

            for i in range(1, lastp + 1):
                allready_in_db = 0
                percent = int( (100 / lastp) * i)
                message = "Scraping page " + str(i) + " out of " + str(lastp)
                progress.update( percent, "", message, "" )
                xbmc.sleep( 1000 )
                url = db_url + 'page/' + str(i) # Modified "/page/" to "page/"
                page_content = grab_url(url)

                # Match String 1: URL, Name, Thumbnail
                match_str1 = 'href="(.+?)" title="Permalink to (.+?)" rel="bookmark">\n\t\t\t\t<img width="300" height="160" src="(.+?)"'
                # Match String 2: Plot
                match_str2 = '<div class="entry">\n\t\t\t<p>(.+?)<\/p>'
                #Matches airdate
                match_str3 = '<span class="tie-date">(.+?)<\/span>\s\s\s<span class="post'

                match1 = re.compile(match_str1).findall(page_content)
                match2 = re.compile(match_str2).findall(page_content)
                match3 = re.compile(match_str3).findall(page_content)

                # Combine those 3 tuples:
                airdates = []
                for entry in match3:
                    airdates.append(convert_airdate(entry))
                video_info = []
                for num, entry in enumerate(match1):
                    new_entry = ()
                    new_entry = new_entry + entry + (match2[num],) + (airdates[num],)
                    video_info.append(new_entry)

                for url, name, thumbnail, plot, airdate in video_info:

                    # Add Test to see if entry is allready there, if yes break this loop and set allready_in_db = True

                    c.execute('INSERT INTO {} VALUES ("{}","{}","{}","{}","{}")'.format(db_name, name, url, thumbnail, plot, airdate))

                if progress.iscanceled():
                    aborted = True
                    break
                if allready_in_db:
                    break

            progress.close()
            if aborted:
                print 'Scrape was aborted!' # DEBUG INFO
                c.execute('DROP TABLE IF EXISTS "{}"'.format(db_name))
                c.execute('DELETE FROM show_list WHERE table_name="{}"'.format(db_name))
                conn.commit()
            else:
                conn.commit()
        else:
            print 'Table: "{}" does exist in DB, i will not continue'.format(db_name)
            dialog = xbmcgui.Dialog()
            ok = dialog.ok('Database', 'Show "{}" is allready in the local DB. Update from there.'.format(show_name))
        conn.close()

    elif db_mode == 'REMOVE':
        dialog = xbmcgui.Dialog()
        if dialog.yesno("Remove from local DB", 'Dou you really want to remove the show:','{}'.format(show_name), "",'No','Yes'):
            c.execute('DROP TABLE IF EXISTS "{}"'.format(db_name))
            c.execute('DELETE FROM show_list WHERE table_name="{}"'.format(db_name))
            conn.commit()
        conn.close()
        xbmc.executebuiltin("Container.Refresh")
        # Remove list item and/or go back one step


def RESOLVELINK(url): # Grab the urls of the embedded videos
    content = grab_url(url)
    screenwave = 'src="(http:\/\/player(?:[0-9]|).screenwavemedia.com(?:\/play|)\/player.php\?id=.+)"(?:\s|\>\<\/s)'
    # This should capture all embedded screenwavemedia videos (i have encountered yet)
    # The brackets that begin with "?:" are non capturing brackets.

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


def addLink(name, url, mode, iconimage, plot='Plot Info', airdate='airdate'):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(cleanName(name), iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": cleanName(name), "plot" : cleanName(plot), "aired" : airdate, "date" : airdate})
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage): # Standard
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

def addDir2(name, url, mode, iconimage): # All Shows Directory
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    add_db_cmd = 'MODE:ADD;NAME:{};URL:{}'.format(urllib.quote_plus(name), urllib.quote_plus(url))
    add_fav_cmd = 'MODE:ADD;NAME:{};URL:{}'.format(urllib.quote_plus(name), urllib.quote_plus(url))
    RunPlugin1 = 'RunPlugin({}?mode=10&url={})'.format(sys.argv[0], add_db_cmd)
    RunPlugin2 = 'RunPlugin({}?mode=11&url={})'.format(sys.argv[0], add_fav_cmd)
    liz.addContextMenuItems([('Add content to DB', RunPlugin1,), ('Add addon Favorites', RunPlugin2,)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

def addDir3(name, url, mode, iconimage): # Favorites Directory
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    rem_fav_cmd = 'MODE:REMOVE;NAME:{};URL:{}'.format(urllib.quote_plus(name), urllib.quote_plus(url))
    RunPlugin = 'RunPlugin({}?mode=11&url={})'.format(sys.argv[0], rem_fav_cmd)
    liz.addContextMenuItems([('Remove from Addon Favorites', RunPlugin,)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

def addDir4(name, url, mode, iconimage): # Local DB Directory
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    upd_db_cmd = 'MODE:UPDATE;NAME:{};URL:{}'.format(urllib.quote_plus(name), urllib.quote_plus(url))
    rem_db_cmd = 'MODE:REMOVE;NAME:{};URL:{}'.format(urllib.quote_plus(name), urllib.quote_plus(url))
    RunPlugin1 = 'RunPlugin({}?mode=10&url={})'.format(sys.argv[0], upd_db_cmd)
    RunPlugin2 = 'RunPlugin({}?mode=10&url={})'.format(sys.argv[0], rem_db_cmd)
    liz.addContextMenuItems([('Update this show', RunPlugin1,), ('Remove from local DB', RunPlugin2,)])
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
    DISPLAY_FAVS(name)

elif mode == 7:
    print "" + name
    JUMPTO(url)

elif mode == 8:
    print "" + name
    DISPLAY_DB(url)

elif mode == 9:
    print "" + name
    DISPLAY_DB_SHOW(url)

elif mode == 10:
    # print "" + name
    LOCAL_DB(url)

elif mode == 11:
    #print "" + name
    FAVORITES(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
