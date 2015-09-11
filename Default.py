#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ChannelAwesome Addon
import urllib
import socket
import re
import sys
import os
from bs4 import BeautifulSoup
import sqlite3
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc
import utils


addonID = 'plugin.video.channelawesome'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
addonDir = xbmc.translatePath(addon.getAddonInfo('path'))
icon = os.path.join(addonDir, 'icon.png')
profile = xbmc.translatePath(addon.getAddonInfo('profile'))
local_db = os.path.join(profile, 'local_db.db')
pluginDir = sys.argv[0]

# Create addon folder in user_data, necessary for the sqlite db
if addon.getSetting("firstrun") != 'false':
	addon.setSetting("firstrun", 'false')


# Main List View
def CATEGORIES():
    addDir('Latest Videos', 'http://channelawesome.com', 2, icon)
    addDir('All Shows', 'http://channelawesome.com', 1, '')
    addDir('Search ChannelAwesome.com', '', 4, '')
    addDir('Addon Favorites', '', 5, '')
    addDir('Local Database', '', 7, '')
    xbmcplugin.endOfDirectory(pluginhandle)

def ALLSHOWS(url):
    content =  utils.grab_url(url)
    match = re.compile(
        '<li id="menu-item-.+?" class="ubermenu-item ubermenu-item-type-taxonomy ubermenu-item-object-category '
        'ubermenu-item-.+? ubermenu-item-auto ubermenu-item-normal ubermenu-item-level-2 ubermenu-column '
        'ubermenu-column-auto" ><a class="ubermenu-target ubermenu-item-layout-default ubermenu-item-layout-text_only" '
        'href="(.+?)"><span class="ubermenu-target-title ubermenu-target-text">(.+?)</span>').findall(content)
    xbmcplugin.addSortMethod(int(sys.argv[1]), 1)
    for url, name in match:
        addDir2(name, url, 2, '')
    xbmcplugin.endOfDirectory(pluginhandle)

def LISTVIDEOS(url):
    baseurl = url
    if '/?s=' in url:
        is_search = 1
    else:
        is_search = 0

    content = utils.grab_url(url)
    video_info = utils.scrape_data(content)

    if is_search and (len(video_info) < 1):
        print 'No search results'
        dialog = xbmcgui.Dialog()
        dialog.notification('No results!', 'No videos found with this search!', xbmcgui.NOTIFICATION_INFO, 1000)
        # TODO: Go Back to Mode 1
        return

    # Get current page and max page number
    matchc = re.compile('class="pages">Page (.+?) of (.+?)</span>').findall(content)
    if matchc == []:
        print 'This show or search result only has one page'  #DEBUG INFO
        for url, name, thumbnail, plot in video_info:
            addLink(name, url, 3, thumbnail, plot)
        return
    else:
        curp = int(matchc[0][0])
        nextp = curp + 1
        prevp = curp - 1
        lastp = int(matchc[0][1])
        position = 'Page ' + str(curp) + ' of ' + str(lastp)
        # Display Page Indicator if activated in settings!
        if get_bool_settings('page_indicator'):
            addInfo(matchc[0][0], matchc[0][1], baseurl)

    for url, name, thumbnail, plot in video_info:
        addLink(name, url, 3, thumbnail, plot, 'airdate', baseurl, lastp)

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

def RESOLVELINK(url): # Grab the urls of the embedded videos
    content = utils.grab_url(url)
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
            return
        else:
            print ret
            video_url = utils.get_video(video_lst[ret])
    elif len(videos) == 1:
        url = videos[0]
        video_url = utils.get_video(url)
    else:
        soup = BeautifulSoup(content, "html.parser")
        header = soup.find("span", {"itemprop" : "name"}).text
        entry = soup.find("div", class_='entry').text
        showText(header, entry)
        return #xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
    listitem = xbmcgui.ListItem(path=video_url)
    return xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

def SEARCHSITE(name):
    dialog = xbmcgui.Dialog()
    d = dialog.input('Search ChannelAwesome.com', type=xbmcgui.INPUT_ALPHANUM)
    d = d.replace(" ", "+")
    if d == '':
        print 'No input' #Debug Info
        # TODO: Go Back to Mode 1
    else:
        kodi_url = pluginDir + '?mode=2&url=' + urllib.quote_plus('http://channelawesome.com/?s=' + d)
        builtin = 'ReplaceWindow(10025,{})'.format(kodi_url)
        #builtin = 'Container.Update({})'.format(kodi_url)
        xbmc.executebuiltin(builtin)
        # NOT Perfect! with Container.Update you will be presented with the search dialog again if you go back
        #              with Replace.Window you kinda messup kodis windows and wont end up where you started from
        #              after leaving the addon with "back"

def DISPLAY_FAVS():
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
    else:
        dialog = xbmcgui.Dialog()
        dialog.notification('Info', 'No shows were added to the addon favorites.', xbmcgui.NOTIFICATION_INFO, 1000)
        #xbmc.executebuiltin("ActivateWindow(10024,{})".format(pluginDir))
        #xbmc.executebuiltin("PreviousMenu")
        #xbmc.executebuiltin("Back")

def EDIT_FAVS(fav_arg):
    print 'Favorites function activated'
    print 'Parameter: ' + str(fav_arg)
    data = fav_arg.split(';')
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

def DISPLAY_DB():
    print 'Display stored Shows'
    conn = sqlite3.connect(local_db)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS show_list (table_name TEXT PRIMARY KEY, show_name TEXT, show_url TEXT)')
    c.execute("SELECT table_name, show_name, show_url FROM show_list")
    shows = c.fetchall()
    conn.close()
    if len(shows):
        print shows # DEBUG
        xbmcplugin.addSortMethod(int(sys.argv[1]), 1)
        for table_name, show_name, show_url in shows:
            addDir4(show_name, table_name, 8, '', show_url)
    else:
        dialog = xbmcgui.Dialog()
        dialog.notification('Info', 'No shows were added to the local db.', xbmcgui.NOTIFICATION_INFO, 2000)
        # TODO: Go Back to Mode 1

def DISPLAY_DB_SHOW(db_table):
    conn = sqlite3.connect(local_db)
    c = conn.cursor()
    try:
        c.execute('SELECT id, name, url, thumb, plot, airdate FROM {}'.format(db_table))
    except:
        dialog = xbmcgui.Dialog()
        dialog.notification('DB Error', 'Try readding the show or clear DB', xbmcgui.NOTIFICATION_ERROR, 3000)
        # TODO: Go Back
    else:
        video_info = c.fetchall()
        conn.close()
        for id, name, url, thumbnail, plot, airdate in video_info:
            if get_bool_settings('episode_num'):
                display_name = str(id) + '. ' + name.encode('ascii', 'ignore')
            else:
                display_name = name
            addLink(display_name, url, 3, thumbnail, plot.encode('ascii', 'ignore'), airdate)
            # .encode(...) is needed because coming from the DB python cant display some utf8 symbols
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)
        xbmc.executebuiltin("Container.SetSortMethod(2)")

def EDIT_DB(db_arg):
    print 'Scrape for DB Activated'
    #print 'Parameter: ' + str(db_arg)
    aborted = 0
    data = db_arg.split(';')
    db_mode = data[0].replace('MODE:', '')
    db_name = data[1].replace('NAME:', '')
    db_url = data[2].replace('URL:', '')
    show_name = db_name
    db_name = db_name.replace(' ', '').lower()
    print 'DB Mode: ' + db_mode
    print 'DB Url:' + db_url
    print 'DB name:' + db_name
    print 'Show name:' + show_name

    # Connect to DB
    conn = sqlite3.connect(local_db)
    c = conn.cursor()
    if db_mode == 'UPDATE':
        print 'UPDATE STARTED!!!'
        print 'Show URL: '+ db_url
        # Get max page number
        content = utils.grab_url(db_url)
        matchc = re.compile('class="pages">Page (.+?) of (.+?)</span>').findall(content)
        lastp = int(matchc[0][1])

        # Progress Dialog
        progress = xbmcgui.DialogProgress()
        progress.create('Updating Show', 'Scraping new videos...')
        counter = 0
        video_list = []
        for i in range(1, lastp + 1):
            allready_in_db = 0
            percent = int( (100 / lastp) * i)
            message = "Scraping page " + str(i) + " out of " + str(lastp)
            progress.update( percent, "", message, "" )
            xbmc.sleep( 1000 )
            url = db_url + 'page/' + str(i)
            page_content = utils.grab_url(url)

            video_info = utils.scrape_data(page_content, 'DB')

            for url, name, thumbnail, plot, airdate in video_info:
                # Test to see if entry is allready in DB
                c.execute('SELECT airdate FROM {} WHERE name="{}"'.format(db_name, name))
                test = c.fetchone()
                if test is None:
                    print 'Episode: "{}" not in DB, adding to update list now!'.format(name)
                    entry = (name, url, thumbnail, plot, airdate)
                    video_list.append(entry)
                    counter = counter + 1
                else: # Entry available in local DB
                    print 'Episode: "{}" Allready in DB, breaking loop now!'.format(name)
                    print 'Stopping update process but will commit changes (if any) to DB'
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
            dialog = xbmcgui.Dialog()
            dialog.notification('Update canceled!', 'No updates were stored in the DB', xbmcgui.NOTIFICATION_WARNING, 3000)
        else:
            dialog = xbmcgui.Dialog()
            if len(video_list) > 0:
                video_list.reverse()
                c.executemany('INSERT INTO {} (name, url, thumb, plot, airdate) VALUES (?,?,?,?,?)'.format(db_name), video_list)
                conn.commit()
                dialog.notification('Update Successfull', '{} entries added to the DB'.format(str(counter)), xbmcgui.NOTIFICATION_INFO, 3000)
            else:
                dialog.notification('No Updates', 'No updates were found for this show', xbmcgui.NOTIFICATION_INFO, 3000)
        conn.close()

    elif db_mode == 'ADD':
        c.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="{}"'.format(db_name))
        test = c.fetchone()
        if test is None:
            print 'Table: "{}" does not exist in DB, i will continue'.format(db_name)
            # Create DB entries
            c.execute('CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY, name TEXT, url TEXT, thumb TEXT, plot TEXT, airdate TEXT)'.format(db_name))
            c.execute('CREATE TABLE IF NOT EXISTS show_list (table_name  TEXT PRIMARY KEY, show_name TEXT, show_url TEXT)')
            c.execute('INSERT OR REPLACE INTO show_list VALUES ("{}", "{}", "{}")'.format(db_name, show_name, db_url))
            # Get max page number
            content = utils.grab_url(db_url)
            matchc = re.compile('class="pages">Page (.+?) of (.+?)</span>').findall(content)
            lastp = int(matchc[0][1])
            # Progress Dialog
            progress = xbmcgui.DialogProgress()
            progress.create('Adding Show to local Database', 'Scraping all videos...')
            video_list = []
            for i in range(1, lastp + 1):
                percent = int( (100 / lastp) * i)
                message = "Scraping page " + str(i) + " out of " + str(lastp)
                progress.update( percent, "", message, "" )
                xbmc.sleep( 1000 )
                url = db_url + 'page/' + str(i) # Modified "/page/" to "page/"
                page_content = utils.grab_url(url)

                video_info = utils.scrape_data(page_content, 'DB')

                for url, name, thumbnail, plot, airdate in video_info:
                    print 'name: ' + utils.cleanName(name) # + '\nplot: ' + utils.cleanName(plot) # DEBUG INFO
                    entry = (name, url, thumbnail, plot, airdate)
                    video_list.append(entry)
                if progress.iscanceled():
                    aborted = True
                    break

            progress.close()
            if aborted:
                print 'Scrape was aborted!' # DEBUG INFO
                c.execute('DROP TABLE IF EXISTS "{}"'.format(db_name))
                c.execute('DELETE FROM show_list WHERE table_name="{}"'.format(db_name))
                conn.commit()
                dialog = xbmcgui.Dialog()
                dialog.notification('Process canceled!', 'The show was not added to the local DB.', xbmcgui.NOTIFICATION_WARNING, 3000)
            else:
                if len(video_list) > 0:
                    # Turn List of Videos arround to get accurate list based on release date
                    video_list.reverse()
                    c.executemany('INSERT INTO {} (name, url, thumb, plot, airdate) VALUES (?,?,?,?,?)'.format(db_name), video_list)
                    conn.commit()
        else:
            print 'Table: "{}" does exist in DB, i will not continue'.format(db_name)
            dialog = xbmcgui.Dialog()
            dialog.ok('Database', 'Show "{}" is allready in the local DB. Update from there.'.format(show_name))
        conn.close()

    elif db_mode == 'REMOVE':
        dialog = xbmcgui.Dialog()
        if dialog.yesno("Remove from local DB", 'Dou you really want to remove the show:','{}'.format(show_name), "",'No','Yes'):
            c.execute('DROP TABLE IF EXISTS "{}"'.format(db_name))
            c.execute('DELETE FROM show_list WHERE table_name="{}"'.format(db_name))
            conn.commit()
        conn.close()
        xbmc.executebuiltin("Container.Refresh")

# Remove local DB (can be run from settings)
def CLEAR_DB():
    dialog1 = xbmcgui.Dialog()
    dialog2 = xbmcgui.Dialog()
    if dialog1.yesno("Clear local DB", 'Dou you really want to clear local DB','and remove all saved favorites and shows', "",'No','Yes'):
        os.remove(os.path.join(profile, 'local_db.db'))
        dialog2.notification('Removed', 'Local DB was removed!', xbmcgui.NOTIFICATION_INFO, 3000)
    else:
        dialog2.notification('Cancled', 'Local DB was not removed!', xbmcgui.NOTIFICATION_INFO, 3000)

def JUMPTO(url, max_page):
    print 'Max Page:' + str(max_page)
    dialog = xbmcgui.Dialog()
    d = dialog.input('Jump to page', type=xbmcgui.INPUT_NUMERIC)
    print 'Dialog input: ' + d
    if (d == ''):
        print 'No dialog input' #DEBUG INFO
    elif (int(d) > max_page):
        dialog.notification('Page not available!', 'Entered page number to high!', xbmcgui.NOTIFICATION_WARNING, 3000)
    else:
        if ('/?s=' in url): # If URL is result of Search
            sstring = re.sub(".+?/?s=", "/?s=", url)
            surl = 'http://channelawesome.com/page/'
            goto_url = surl + d + sstring
        else:
            if '/page/' in url:
                baseurl = re.sub("/page/.+", "page/", url)
            else:
                baseurl = url + '/page/'
            goto_url = baseurl + d
        if d:
            kodi_url = pluginDir + '?mode=2&url={}'.format(urllib.quote_plus(goto_url))
            builtin = 'Container.Update({})'.format(kodi_url)
            xbmc.executebuiltin(builtin)

def LISTALL1(url):
    kodi_url = pluginDir + '?mode=13&url={}'.format(urllib.quote_plus(url))
    builtin = 'Container.Update({})'.format(kodi_url)
    xbmc.executebuiltin(builtin)

def LISTALL2(url):
    baseurl = url
    content = utils.grab_url(url)
    # Get max page number
    matchc = re.compile('class="pages">Page (.+?) of (.+?)</span>').findall(content)
    lastp = int(matchc[0][1])

    progress = xbmcgui.DialogProgress()
    progress.create('Progress', 'Listing all videos...')
    for i in range(1, lastp + 1):
        percent = int( (100 / lastp) * i)
        message = "Scraping page " + str(i) + " out of " + str(lastp)
        progress.update( percent, "", message, "" )
        xbmc.sleep( 1000 )
        url = baseurl + '/page/' + str(i)
        page_content = utils.grab_url(url)
        video_info = utils.scrape_data(page_content)
        for url, name, thumbnail, plot in video_info:
            addLink(name, url, 4, thumbnail, plot)
        if progress.iscanceled():
            break
    progress.close()

def addInfo(curp, lastp, show_url):
    liz = xbmcgui.ListItem('[COLOR yellow]Page ' + curp + ' of ' + lastp + '[/COLOR]')
    liz.setProperty('IsPlayable', 'false')
    RunPlugin1 = 'RunPlugin({}?mode=11&url={}&max_page={})'.format(sys.argv[0], urllib.quote_plus(show_url), lastp)
    RunPlugin2 = 'RunPlugin({}?mode=12&url={})'.format(sys.argv[0], urllib.quote_plus(show_url))
    # Only Display List all function if not a search result and if first page
    no_list_all = ['/?s=', '/page/']
    if any(x in urllib.unquote_plus(show_url) for x in no_list_all) or (int(lastp) > 100):
        liz.addContextMenuItems([('Jump to page', RunPlugin1,),])
    else:
        liz.addContextMenuItems([('Jump to page', RunPlugin1,), ('List all', RunPlugin2,)])
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=None, listitem=liz)

def addLink(name, url, mode, iconimage, plot='Plot Info', airdate='airdate', show_url='show_url', max_page=None):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(utils.cleanName(name), iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    if airdate != 'airdate':
        labels = {"Title": utils.cleanName(name), "plot" : utils.cleanName(plot), "date" : airdate}
    else:
        labels = {"Title": utils.cleanName(name), "plot" : utils.cleanName(plot)}
    liz.setInfo(type="Video", infoLabels=labels)
    liz.setProperty('IsPlayable', 'true')
    if show_url != 'show_url' and max_page:
        #print 'Show URL: ' + show_url
        #print 'Max. Page No.' + str(max_page)
        RunPlugin = 'RunPlugin({}?mode=11&url={}&max_page={})'.format(sys.argv[0], urllib.quote_plus(show_url), str(max_page))
        liz.addContextMenuItems([('Jump to page', RunPlugin,),])
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
    RunPlugin1 = 'RunPlugin({}?mode=9&db_arg={})'.format(sys.argv[0], add_db_cmd)
    RunPlugin2 = 'RunPlugin({}?mode=6&fav_arg={})'.format(sys.argv[0], add_fav_cmd)
    liz.addContextMenuItems([('Add content to DB', RunPlugin1,), ('Add addon Favorites', RunPlugin2,)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

def addDir3(name, url, mode, iconimage): # Directories in local favorites
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    rem_fav_cmd = 'MODE:REMOVE;NAME:{};URL:{}'.format(urllib.quote_plus(name), urllib.quote_plus(url))
    RunPlugin = 'RunPlugin({}?mode=6&fav_arg={})'.format(sys.argv[0], rem_fav_cmd)
    liz.addContextMenuItems([('Remove from Addon Favorites', RunPlugin,)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

def addDir4(name, db_table, mode, iconimage, show_url): # Directories in local DB
    u = sys.argv[0] + "?db_table=" + urllib.quote_plus(db_table) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    upd_db_cmd = 'MODE:UPDATE;NAME:{};URL:{}'.format(urllib.quote_plus(name), urllib.quote_plus(show_url))
    rem_db_cmd = 'MODE:REMOVE;NAME:{};URL:{}'.format(urllib.quote_plus(name), urllib.quote_plus(show_url))
    RunPlugin1 = 'RunPlugin({}?mode=9&db_arg={})'.format(sys.argv[0], upd_db_cmd)
    RunPlugin2 = 'RunPlugin({}?mode=9&db_arg={})'.format(sys.argv[0], rem_db_cmd)
    liz.addContextMenuItems([('Update this show', RunPlugin1,), ('Remove from local DB', RunPlugin2,)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

def showText(heading, text):
    id = 10147
    xbmc.executebuiltin('ActivateWindow({})'.format(id))
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

# Get Bool Settings
def get_bool_settings(id):
    if addon.getSetting(id=id) == 'true':
        return True
    else:
        return False


params = utils.get_params()
url = None
name = None
mode = None
max_page = None
fav_arg = None
db_arg = None
db_table = None

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
try:
    db_table = urllib.unquote_plus(params["db_table"])
except:
    pass
try:
    max_page = int(params["max_page"])
except:
    pass
try:
    fav_arg = urllib.unquote_plus(params["fav_arg"])
except:
    pass
try:
    db_arg = urllib.unquote_plus(params["db_arg"])
except:
    pass

print "Mode: " + str(mode)
print "URL: " + str(url)
print "Name: " + str(name)
print "DB Table: " + str(db_table)
print "Fav. Arg.: " + str(fav_arg)
print "DB Arg.: " + str(db_arg)


if mode == None: # Function to display main view
    print "Main View"
    CATEGORIES()

elif mode == 1: # Function di List all available shows linked on the main page
    print "All Shows"
    ALLSHOWS(url)

elif mode == 2: # Function to List Videos on a page
    print "List Videos: " + url
    LISTVIDEOS(url)

elif mode == 3: # Function to resolve video links
    print "Resolve Link: " + url
    RESOLVELINK(url)

elif mode == 4: # Function to search site
    print "" + name
    SEARCHSITE(name)

elif mode == 5: # Function to display addon favorites
    print "" + name
    DISPLAY_FAVS()

elif mode == 6: # Function to edit favorites
    print "Edit Favorites"
    EDIT_FAVS(fav_arg)

elif mode == 7: # Function to list all shows in db
    print "" + name
    DISPLAY_DB()

elif mode == 8: # Function to Display a show in DB
    print "Display DB Show: " + name
    DISPLAY_DB_SHOW(db_table)

elif mode == 9: # Function to modifiy shows stored in local db
    print "Edit Database"
    EDIT_DB(db_arg)

elif mode == 10: # Function to remove local DB
    print "Clear DB"
    CLEAR_DB()

elif mode == 11: # Function to jump to a certain page
    print "Jump to page"
    JUMPTO(url, max_page)

elif mode == 12: # Function to initialize LIST ALL Function
    LISTALL1(url)

elif mode == 13: # Function to list all videos of a show
    LISTALL2(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
