# plugin.video.channelawesome README

## TODO List

- move jumpt to page function to context menu?
- Vimeo Support
- Settings


## Ideas:

- Automatic Updates?
    Add last scrape time to the db, check when it was last and run the scrape automaticly when you open the container

- Remove Nostalgia Critic from Display Name to implement better Sorting by name
    "Nostalgia Critic:" -> ""
    "Nostalgia Critic;" -> ""
    "Nostalgia Critic Editorial:" -> "Editorial:"
 
- DB Adding and Structure:
    - add the scraped data to the db using the cleanname function
        --> Results in Problem with " Character
    - add integer primary key
    - while adding or updating a show put the scraped data into a list first, after its finished turn the list around (first entry becomes last entry)
        and then add it to the db using execute many.
        This way everything would be in the correct order and you could use the integer PK for labeling the episodes.

## Problems:

- If GOTO Function is canceled, dont open empty folder!
- If no embedded Video was found and the addon displays the entry text, stop kodi from trying to still playback this!

- Get Rid of "Blue Dots" in the main view (Xperience1080 skin)
- Displaying Names and Plots from the DB results in excepetiion, cleanName is not working here:
    WORKAROUND: .encode('ascii', 'ignore')