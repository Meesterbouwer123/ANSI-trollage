# Examples
random ramblings + commands that are a pain to type again

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

## print big colorful text:
```
text --figlet_font=standard --clean_mode=hide --repeat=100 --rgb_mode=gradient --gradient_size=10 Hey there >:D
```