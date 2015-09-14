# plugin.video.channelawesome README

## TODO List

- FORCE ViewMode 500 for FAVS and local DB
- Vimeo Support
- Colorcode the first two entries that are added on List Latest!
- Add Icons to favorites


Add:
- List Popular 
- List Recent 
    - Found on main site (#tab2, Recent)
    - Shows latest 12 posted articels/videos but no Description found on this one
    - 
- By Year (Reviews by Decade)
    Ad those by decade reviews
    Directories:
        - 2010s -> 1930s (like main page)
        - Custom Year (with number dialog)

- All Producers List (Description and Icon on this page to be scraped):
    http://channelawesome.com/author-list/
    Add this to a directory, custom context menu item to display discription.

- All Shows List (Complete List of All Shows on the Site) 
    - Complete List of all shows but needs to filtered a bit (Videos, Producers, and so on)
    - No Real URL found but it shows up as 404 Error
- From the Archives (Main Page bottom)

REDO grab_icon because of new producers section which feature icon on every page, it needs to detect if its a show or author link and work accordingly
Add authors page to the db for easier access to icons?   



## Ideas:

- Automatic Updates for DB?
    Add last scrape time to the db, check when it was last and run the scrape automaticly when you open the container
 
- Add custom favorites (input tag links for example) from settings menu

- GOTO Creator Page from Latest Videos (context menu item)

## Problems:

- SEARCH Function: if not input or cancel go back not working
- If no embedded Video was found and the addon displays the entry text, stop kodi from trying to still playback this!
- Displaying Names and Plots from the DB results in excepetiion, cleanName is not working here:
    WORKAROUND: .encode('ascii', 'ignore')