import curses
import math

NORMAL_COLOR = 0
SELECTED_COLOR = 1
ERROR_COLOR = 2

OPTIONS_MIN_WIDTH = 10

selected = 0
color = NORMAL_COLOR
scroll = 0
longest_line = 10
text = []
screen_height = 0


library = {
    1: {"title": "Python for everyone", "author": "John Doe", "quantity": 3},
    2: {"title": "Data and Structures", "author": "Anna Smith", "quantity": 5},
    3: {"title": "Introduction to OOP", "author": "Misco Jones", "quantity": 2},
    4: {"title": "Advanced Python", "author": "Jane Doe", "quantity": 4},
    5: {"title": "Machine Learning Basics", "author": "Tom Brown", "quantity": 6},
    6: {"title": "Deep Learning with Python", "author": "Sara White", "quantity": 3},
    7: {"title": "Data Science Handbook", "author": "Emily Davis", "quantity": 5},
    8: {"title": "Artificial Intelligence", "author": "Michael Green", "quantity": 2},
    9: {"title": "Python for Data Analysis", "author": "Laura Black", "quantity": 7},
    10: {"title": "Statistics for Data Science", "author": "Robert Gray", "quantity": 4}
}


def get_input(stdscr, msg, validator="str"):
    user_input = ""
    valid = False
    while not user_input or not valid:
        stdscr.move(0, 0)
        stdscr.addstr(msg)
        stdscr.clrtoeol()
        stdscr.refresh()
        curses.echo()  # Make user input visible
        user_input = stdscr.getstr().decode("utf-8").strip()  # Read user input as a string
        curses.noecho()  # Hide input again after capturing
        if validator == "int" and user_input.isnumeric() or validator == "str":
            valid = True

    return user_input


def addBook(stdscr):
    id = len(library) + 1
    title = get_input("Enter the title: ")
    author = get_input("Enter the author: ")
    quantity = get_input("Enter the quantity: ", "int")
    
    library.update({id: {"title": title, "author": author, "quantity": int(quantity)}})
    stdscr.addstr(f"\nBook added successfully\n")
    stdscr.refresh()


def searchBook():
    pass


def displayBooks(stdscr):
    global selected, text, scroll, longest_line, screen_height
    stdscr.move(0, 0)
    stdscr.addstr("╔" + "═" * longest_line + "╗\n")

    for line in range(scroll, len(text), 1):
        line_to_print = f"{text[line]}" + " " * (longest_line - len(text[line]))
        stdscr.addstr("║")
        color = SELECTED_COLOR if math.ceil((line + 1) / 5) == selected else NORMAL_COLOR
        stdscr.addstr(line_to_print, curses.color_pair(color))
        color = NORMAL_COLOR
        stdscr.addstr("║\n")
        if stdscr.getyx()[0] + 4 > screen_height:
            break

    stdscr.addstr("╚" + "═" * longest_line + "╝\n")


def displayOptionPanel(stdscr):
    options = ["➕ Add", "🔎 Search", "❌ Exit"]
    xpos = longest_line + 2
    ypos = 0
    width = stdscr.getmaxyx()[1] - (longest_line + 5)
    stdscr.move(ypos, xpos)
    stdscr.addstr("╔" + "═" * width + "╗")
    for item in options:
        ypos += 1
        stdscr.move(ypos, xpos)
        stdscr.addstr("║" + item + " " * (width - len(item) - 1) + "║")
    stdscr.move(ypos + 1, xpos)
    stdscr.addstr("╚" + "═" * width + "╝")
    

def handleUserInput(stdscr):
    global scroll, selected, screen_height
    key = stdscr.getch()
    if key == 10:  # Enter key
        return
    elif key == curses.KEY_MOUSE:
        id, x, y, z, bstate = curses.getmouse()
        if bstate & curses.BUTTON4_PRESSED:
            scroll -= 1 if scroll > 0 else 0
        elif bstate & curses.BUTTON5_PRESSED:
            scroll += 1 if scroll + screen_height - 4 < len(text) else 0
        elif curses.BUTTON1_PRESSED:
            selected = math.ceil((y + scroll) / 5)
            stdscr.addstr(f"{selected}")
            stdscr.clrtoeol()
    stdscr.clrtobot()
    screen_height = stdscr.getmaxyx()[0]
    


def display(stdscr):
    global text, longest_line, screen_height
    text = []
    for book in library:
        text.append(f"ID: {book}")
        for item in library[book]:
            text.append(f"{item.capitalize()}: {library[book][item]}")
        text.append("")

    longest_line = len(max(text, key=len))
    screen_height = stdscr.getmaxyx()[0]

    # Enable mouse support
    curses.mousemask(curses.ALL_MOUSE_EVENTS)

    while True:
        max_scroll = len(text) - screen_height + 4
        scroll_pct = int((scroll / max_scroll) * 100)
        displayBooks(stdscr)
        displayOptionPanel(stdscr)
        stdscr.move(int((screen_height - 5) * scroll_pct / 100) + 1, longest_line + 1)
        handleUserInput(stdscr)


    def borrowBook():
        pass


    def exit():
        stdscr.addstr("Exiting the menu...\n")
        stdscr.refresh()
