# ANSI trollage
A simple tool I made for myself to exploit ANSI injection vulnerabilites.
If you manage to find this useful, please let me know :D

## Usage
1. run the help command
2. ???????????
3. profit

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
- [ ] Crash terminal emulators (beginning has been made, looking for working crashes)
- [ ] Run commands on the target's pc (there are a lot of RCEs).
- [X] Scripting support (just executing the commands in a file line-by-line)
- [ ] Cache image conversions so frames that look the same will not be computed twice.
- [ ] Fix image aspect ratios (especially on the ascii mode).
- [ ] More image display modes (for example sixel, halfblocks).
- [ ] Plugin system to support private printers/payloads (we don't want to accidentally leak zerodays).
- [ ] Music playing maybe (probably not)

## references
In case you want to learn more about ANSI exploitation, here is a list of links that may or may not be useful:
- https://dgl.cx/2023/09/ansi-terminal-security
- https://github.com/dgl/vt-houdini
- https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
- https://www.cyberark.com/resources/threat-research-blog/dont-trust-this-title-abusing-terminal-emulators-with-ansi-escape-characters
- https://www.proteansec.com/linux/blast-past-executing-code-terminal-emulators-via-escape-sequences/
- https://www.youtube.com/watch?v=opW_Q7jvSbc