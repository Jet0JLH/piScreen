# CMD documentation

## CMD 1 (stop-core)
**Description**:\
Stops the core service.\
**Packages**:\
```
{"cmd": 1}
```
**Return**:\
```
{"code": 0}
```

## CMD 2 (get-core-status)
**Description**:\
Function as ping. Does nothing in core.\
**Packages**:\
```
{"cmd": 2}
```
**Return**:\
When successfull:
```
{"code": 0}
```

When unreachable:
```
{"code": -1}
```

## CMD 3 (get-setting)
**Description**:\
Returns all or selected settings loaded in core.\
**Packages**:\
```
{"cmd": 3}
```
```
{"cmd": 3, "path": <str>}
```
**Return**:\
```
{"code": 0, "value": {}}
```

## CMD 4 (set-setting)
**Description**:\
Add, updates or remove elements in settings. The path paramenter is needed. If no value is given, the entry of the path will be deleted. If the value should have a fixed type, this can be specified. The following types are permitted: int, float, str, json, bool\
**Packages**:\
```
{"cmd": 4, "path": <str>}
```
```
{"cmd": 4, "path": <str>, "value": <value>}
```
```
{"cmd": 4, "path": <str>, "value": <value>, "type": <type>}
```

## CMD 5 (get-display-resolution)
**Description**:\
Returns the current resolution of both HDMI ports.\
**Packages**:\
```
{"cmd": 5}
```
**Return**:\
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
**Description**:\
    Set the resolution of the display. It will set the default output, if no output is specified.
    If width and height is not defined, the display resolution turns back to auto.\
**Packages**:\
```
{
    "cmd": 6,
    "output": <outputname>,
    "width": <width>,
    "height": <height>
}
```
**Return**:\
```
{"code": 0}
```

## CMD 7 (get-display-orientation)
**Description**:\
    Get the display orientation of both HDMI ports.\
**Packages**:\
```
{"cmd": 7}
```
**Return**:\
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
**Description**:\
    Set the orientation of the display. It will set the default output, if no output is specified.
    Possible values for orientation are:
    0 = Default
    1 = 270° clockwise
    2 = 180°
    3 = 90° clockwise
    4 = Default flipped
    5 = 270° clockwise flipped
    6 = 180° flipped
    7 = 90° clockwise flipped
**Packages**:\
```
{
    "cmd": 8,
    "output": <outputname>,
    "orientation": <orientation>
}
```
**Return**:\
```
{"code": 0}
```