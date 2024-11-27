# ANSI trollage
A simple tool I made for myself to exploit ANSI injection vulnerabilites.
If you manage to find this useful, please let me know :D

## Usage
1. run the help command
2. ???????????
3. profit

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
### How can I make this exploit software X?
If you want to add a new exploit to this tool you need to make a new printer (see `printer.py`).

You need to make a new class that:
- extends the `Printer` class.
- has a `print(bytes)` function to send those raw bytes to the target's terminal. expect this function to be called a lot, so try to avoid expensive computations.
- (optionally) has a `close()` function. this will be called once the program exits.

Afterwards you can add the required argument parsing to `get_printer()` (`main.py`) and you are done!

### I found this funny thing you can do with ANSI injection, how can I add it?
If you want to add a new payload (see `payload.py`) first think if it's not just some special case of an already existing payload. If it is: add it to that payload.

Otherwise, you need to make a class that:
- extends the `Payload` class.
- has a `tick(Printer)` function to send the ANSI codes required to the printer. this function will be called *a lot*, so don't do unnessacary computations.

Once you are done adding or extending a payload, you need to make a command for it in `main()` (`main.py`). Think again if it makes sense to merge it with an already existing command. Also don't forget to update the help command!

### IDK what to add, where can I help?
We have a small backlog of ideas in case you want to contribute:
- [ ] More image display modes (for example sixel, halfblocks).
- [ ] Cache image conversions so frames that look the same will not be computed twice.
- [ ] Fix image aspect ratios (especially on the ascii mode).
- [ ] Weren't there sequences that could crash terminal emulators?
- [ ] Scripting support (just executing the commands in a file line-by-line)
- [ ] Music playing maybe (probably not)