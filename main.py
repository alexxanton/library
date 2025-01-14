import curses
from library import displayLibrary

def main(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.curs_set(1)

    while True:
        displayLibrary(stdscr)

curses.wrapper(main)
