# ANSI fucker
A simple tool I made for myself to exploit ANSI injection vulnerabilites.
If you manage to find this useful, please let me know :D

## Usage
If you are too stupid to find out how to use the help command, you are also too stupid to use this tool.
This tool's most powerful feature is the ease with which you can add new targeted applications, so it's only really useful if you know how to code.

## Text formatting:
The idea is to have the normal text with style formattings in the middle. These style formattings will be words describing what formatting you want, placed between ( and ). To get an opening round bracket in the text you need to escape it with a backslash `\(`, an ending bracked doesn't need to be escaped. A backslash can be placed by escaping it again (like `\\`). 

The final result will be in UTF-8 (maybe we can make this be decided by the printer later).

Some examples:
```
(red)
(reset) and (wipe)
(link https://example.com) and (nolink)
(bell)
(CRLF)
```

## For programmers:
### WTF is a printer
A printer is an abstraction layer that can be used to print arbitrary bytes to another computer's terminal. Most payloads assume that this happens during the `print` call to give the right timings, so that's a thing to keep in mind.
Adding a new printer is straightforward: You first make a new class in `printer.py` that extends the existing Printer class, and implement the `print(bytes)` function. After that you need to add the argument parsing for the new printer in the `get_printer()` in main.py. At this point your new printer should be ready to go!

### WTF is a payload?
A payload is an abstraction layer for any action you can do when you have a working printer: from printing basic ascii to wiping the entire terminal screen. Each payload represents a different action that the user can take.
Adding a new payload is also straightforward: Make a new class in payload.py that extends from the base `Payload` class and implements the `tick(printer)` function. Then you need to add a new command in the `main` function to actually start your new payload (don't forget to add it to the help command too!). After that your new paylaod is ready to use!

### TODO
In case you want to contribute to this project but don't have any idea on what to add, here are some ideas:
- [X] Sending hyperlinks using OSC 8
- [ ] Image and GIF rendering using a graphics protocol such as sixel, I tried this before but couldn't find any cross-platform implementation that could transform the images in-memory.