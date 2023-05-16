import textwrap

text = """This is a very long string that I want to wrap and this is not only string, 
but also it's great stuff, which me and my guys - really love. And I want to wrap it, really hard.
Harry Potter is a great movie, but I don't like it.
And for example, my dawgs, my friends, my colleagus and my other; friends, are all very good people.
Let's put even more stress here, to better, with ass, node and pose and with nice, beautiful and funny people.
Entrepeneurshipers are people from other dimenssssiohsddfeg, please never ever forget - that you are great guys, cheers."""

for line in text.split("."):
    lines = textwrap.wrap(line, 15, break_long_words=False)
    print(lines)
