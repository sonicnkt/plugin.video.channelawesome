# plugin.video.channelawesome README

## TODO List

- Vimeo Support




## Ideas:

- Automatic Updates?
    Add last scrape time to the db, check when it was last and run the scrape automaticly when you open the container

- Remove Nostalgia Critic from Display Name to implement better Sorting by name
    "Nostalgia Critic:" -> ""
    "Nostalgia Critic;" -> ""
    "Nostalgia Critic Editorial:" -> "Editorial:"
 
- Add custom favorites (input tag links for example) from settings menu

## Problems:

- SEARCH Function (no input and open results)
- If no embedded Video was found and the addon displays the entry text, stop kodi from trying to still playback this!
- Get Rid of "Blue Dots" in the main view (Xperience1080 skin)
- Displaying Names and Plots from the DB results in excepetiion, cleanName is not working here:
    WORKAROUND: .encode('ascii', 'ignore')