# CMD documentation

## CMD 1 (stop-core)
**Description**:  
Stops the core service.\
**Packages**:
```
{"cmd": 1}
```
**Return**:  
```
{"code": 0}
```

## CMD 2 (get-core-status)
**Description**:  
Function as ping. Does nothing in core.  
**Packages**:  
```
{"cmd": 2}
```
**Return**:  
When successfull:  
```
{"code": 0}
```

When unreachable:  
```
{"code": -1}
```

## CMD 3 (get-setting)
**Description**:  
Returns all or selected settings loaded in core.  
**Packages**:  
```
{"cmd": 3}
```
```
{"cmd": 3, "path": <str>}
```
**Return**:  
```
{"code": 0, "value": {}}
```

## CMD 4 (set-setting)
**Description**:  
Add, updates or remove elements in settings. The path paramenter is needed. If no value is given, the entry of the path will be deleted. If the value should have a fixed type, this can be specified. The following types are permitted: int, float, str, json, bool  
**Packages**:  
```
{"cmd": 4, "path": <str>}
```
```
{"cmd": 4, "path": <str>, "value": <value>}
```
```
{"cmd": 4, "path": <str>, "value": <value>, "type": <type>}
```
**Return**:  
```
{"code": 0}
```

## CMD 5 (get-display-resolution)
**Description**:  
Returns the current resolution of both HDMI ports.  
**Packages**:  
```
{"cmd": 5}
```
**Return**:  
```
{
    "code": 0,
    "currentResolution": {
        [
            {"width": <widthHDMI1>, "height": <heightHDMI1>},
            {"width": <widthHDMI2>, "height": <heightHDMI2>}
        ]
    }
}
```

## CMD 6 (set-display-resolution)
**Description**:  
Set the resolution of the display. It will set the default output, if no output is specified.
If width and height is not defined, the display resolution turns back to auto.  
**Packages**:  
```
{
    "cmd": 6,
    "output": <outputname>,
    "width": <width>,
    "height": <height>
}
```
**Return**:  
```
{"code": 0}
```

## CMD 7 (get-display-orientation)
**Description**:  
Get the display orientation of both HDMI ports.  
**Packages**:  
```
{"cmd": 7}
```
**Return**:  
```
{
    "code": 0,
    "orientation": {
        [
            <orientationHDMI1>, <orientationHDMI2>
        ]
    }
}
```

## CMD 8 (set-display-orientation)
**Description**:  
Set the orientation of the display. It will set the default output, if no output is specified.
Possible values for orientation are:
- 0 = Default
- 1 = 270° clockwise
- 2 = 180°
- 3 = 90° clockwise
- 4 = Default flipped
- 5 = 270° clockwise flipped
- 6 = 180° flipped
- 7 = 90° clockwise flipped  
**Packages**:  
```
{
    "cmd": 8,
    "output": <outputname>,
    "orientation": <orientation>
}
```
**Return**:  
```
{"code": 0}
```

## CMD 9 (get-display-status)
**Description**:  
Get the current display status of both HDMI outputs.  
0 for off and 1 for on  
**Packages**:  
```
{"cmd": 9}
```
**Return**:  
```
{
    "code": 0,
    "status": {
        [
            <statusHDMI1>, <statusHDMI2>
        ]
    }
}
```

## CMD 10 (set-display-status)
**Description**:  
Set the display status to on or off with value 1 for on and 0 for off. If you dosen't define the output parameter, it will use the default output.  
**Packages**:  
```
{
    "cmd": 8,
    "output": <outputname>,
    "value": <status>
}
```
**Return**:  
```
{"code": 0}
```

## CMD 11 (do-reboot)
**Description**:  
Stops piScreen and performs a reboot of the whole system.  
**Packages**:  
```
{"cmd": 11}
```
**Return**:  
```
{"code": 0}
```

## CMD 12 (do-shutdown)
**Description**:  
Stops piScreen and performs a shutdown of the whole system.  
**Packages**:  
```
{"cmd": 12}
```
**Return**:  
```
{"code": 0}
```

## CMD 13 (set-desktop-configuration)
**Description**:  
Changes the settings of the desktop.  
You can set the mode of the desktop background image. Possible modes are: color, stretch, fit, crop, center, title, screen  
You can set the path of the desktop background image.  
You can set the desktop background color.  
And you can enable or disable desktop icons. 1 for enable, 0 for disable.  
**Packages**:  
```
{
    "cmd": 13,
    "mode": <mode>,
    "wallpaper": <pathOfWallpaper>,
    "background-color": <colorInHex>,
    "show-trash": <0/1>,
    "show-documents": <0/1>,
    "show-mounts": <0/1>
}
```
**Return**:  
```
{"code": 0}
```

## CMD 14 (get-desktop-configuration)
**Description**:  
Returns the current desktopconfiguration as json object  
**Packages**:  
```
{"cmd": 14}
```
**Return**:  
```
{
    "code": 0,
    "config": {
        "desktop_bg": <colorInHex>,
        "wallpaper": <pathOfWallpaper>,
        "wallpaper_mode": <mode>,
        "show_trash": <0/1>,
        "show_documents": <0/1>,
        "show_mounts": <0/1>
    }
}
```

## CMD 15 (get-status)
**Description**:  
Returns the status of the active mode, infos of the mode and informations of the display.  
**Packages**:  
```
{"cmd": 15}
```
**Return**:  
```
{
    "code": 0,
    "status": {
        "mode": <modeNumber>,
        "modeInfo": {},
        "displayInfo": {}
    }
}
```

## CMD 16 (get-schedule)
**Description**:  
Returns all or selected schedule entries loaded in core.  
**Packages**:  
```
{"cmd": 16}
```
```
{"cmd": 16, "path": <str>}
```
**Return**:  
```
{"code": 0, "value": {}}
```

## CMD 17 (set-setting)
**Description**:  
Add, updates or remove elements in the schedule. The path paramenter is needed. If no value is given, the entry of the path will be deleted. If the value should have a fixed type, this can be specified. The following types are permitted: int, float, str, json, bool  
**Packages**:  
```
{"cmd": 17, "path": <str>}
```
```
{"cmd": 17, "path": <str>, "value": <value>}
```
```
{"cmd": 17, "path": <str>, "value": <value>, "type": <type>}
```
**Return**:  
```
{"code": 0}
```

## CMD 18 (add-cron-entry)
**Description**:  
Adds a cron entrie to the cron section of the schedule.  
The trigger pattern is builed like the linux crontab.  
If a pattern is not set, it would be set to *  
If enabled is not set, it would be set to 1  
**Packages**:  
```
{
    "cmd": 18,
    "enabled": <0/1>,
    "minute": <pattern>,
    "hour": <pattern>,
    "day": <pattern>,
    "month": <pattern>,
    "year": <pattern>,
    "weekday": <pattern>,
    "action": {
        "cmd": <cmdID>,
        "parameter": {}
    }
    "commandset": <commandsetID>
}
```
**Return**:  
```
{"code": 0, "value": <idOfTheCreatedEntry>}
```

## CMD 19 (delete-cron-entry)
**Description**:  
Removes a cron entrie of the cron section by id.  
**Packages**:  
```
{
    "cmd": 19,
    "id": <cronID>
}
```
**Return**:  
```
{"code": 0}
```

## CMD 20 (update-cron-entry)
**Description**:  
Updates a cron entry by id.   
**Packages**:  
```
{
    "cmd": 20,
    "id": <cronID>
    "enabled": <0/1>,
    "minute": <pattern>,
    "hour": <pattern>,
    "day": <pattern>,
    "month": <pattern>,
    "year": <pattern>,
    "weekday": <pattern>,
    "action": {
        "cmd": <cmdID>,
        "parameter": {}
    }
    "commandset": <commandsetID>
}
```
**Return**:  
```
{"code": 0}
```

## CMD 21 (add-commandset)
**Description**:  
Adds a commandset entry to the commandset section of the schedule.  
Name is optional.  
**Packages**:  
```
{
    "cmd": 21,
    "value": {
        "name": <name>,
        "commands": []
    }
}
```
**Return**:  
```
{"code": 0, "value": <idOfTheCreatedEntry>}
```

## CMD 99 (stop-modes)
**Description**:
Stops the active mode and returns to mode 0 (idle).  
**Packages**:  
```
{"cmd": 99}
```
**Return**:  
```
{"code": 0}
```

## CMD 100 (start-firefox)
**Description**:
Starts firefox to given url.  
**Packages**:  
```
{
    "cmd": 10,
    "value": <url>
}
```
**Return**:  
```
{"code": 0}
```

## CMD 101 (do-firefox-restart)
**Description**:
Quit firefox and restart it to last url.  
**Packages**:  
```
{"cmd": 101}
```
**Return**:  
```
{"code": 0}
```

## CMD 102 (do-firefox-refresh)
**Description**:
Reloads active site in firefox.  
**Packages**:  
```
{"cmd": 102}
```
**Return**:  
```
{"code": 0}
```

## CMD 200 (start-vlc)
**Description**:
Starts given media in vlc.  
**Packages**:  
```
{
    "cmd": 200,
    "value": <file>
}
```
**Return**:  
```
{"code": 0}
```

## CMD 201 (do-vlc-play)
**Description**:
Resume media playback.  
**Packages**:  
```
{"cmd": 201}
```
**Return**:  
```
{"code": 0}
```

## CMD 202 (do-vlc-toggle-play-pause)
**Description**:
Switch between pause and playback.  
**Packages**:  
```
{"cmd": 202}
```
**Return**:  
```
{"code": 0}
```

## CMD 203 (do-vlc-pause)
**Description**:
Pause media playback.  
**Packages**:  
```
{"cmd": 202}
```
**Return**:  
```
{"code": 0}
```

## CMD 204 (do-vlc-restart)
**Description**:
Restart the media playback.  
**Packages**:  
```
{"cmd": 202}
```
**Return**:  
```
{"code": 0}
```

## CMD 205 (set-vlc-volume)
**Description**:
Adjusts the playback volume.  
**Packages**:  
```
{
    "cmd": 205,
    "value": <value>
}
```
**Return**:  
```
{"code": 0}
```