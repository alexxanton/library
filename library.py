import curses
import math
import sys

NORMAL_COLOR = 0
SELECTED_COLOR = 1
ERROR_COLOR = 2
OPTIONS_MAX_WIDTH = 40
MIN_HEIGHT = 8

selected = 0
color = NORMAL_COLOR
scroll = 0
longest_line = 10
text = []
screen_height = 0
run = True
option = 0
searchMode = False
searchResults = {}


books = {
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
    global run
    id = len(books) + 1
    title = get_input(stdscr, "Enter the title: ")
    author = get_input(stdscr, "Enter the author: ")
    quantity = get_input(stdscr, "Enter the quantity: ", "int")
    
    books.update({id: {"title": title, "author": author, "quantity": int(quantity)}})
    stdscr.refresh()
    run = False


def search(books, query):
    global searchMode, run

    # Normalize the input
    query = query.lower().split()  # Split query into keywords
    results = {}

    for item in range(1, len(books), 1):
        string_lower = books[item]["title"].lower()
        # Check if all query parts are in the book in order
        current_index = 0
        match = True

        for word in query:
            current_index = string_lower.find(word, current_index)
            if current_index == -1:  # Word not found
                match = False
                break
            current_index += len(word)  # Move index forward to maintain order

        if match:
            results[item] = books[item]

    if len(results) > 0:
        searchMode = True
        run = False

    return results


def displayBooks(stdscr):
    global selected, text, scroll, longest_line, screen_height
    stdscr.move(0, 0)
    stdscr.addstr("╔" + "═" * longest_line + "╦\n")

    for line in range(scroll, len(text), 1):
        line_to_print = f"{text[line][0:longest_line:1]}" + " " * (longest_line - len(text[line]))
        stdscr.addstr("║")
        color = SELECTED_COLOR if math.ceil((line + 1) / 5) == selected else NORMAL_COLOR
        stdscr.addstr(line_to_print, curses.color_pair(color))
        color = NORMAL_COLOR
        stdscr.addstr("║\n")
        if stdscr.getyx()[0] + 4 > screen_height:
            break

    stdscr.addstr("╚" + "═" * longest_line + "╩\n")


def displayOptionPanel(stdscr):
    options = ["➕ New", "🔎 Search", "❌ Exit"]
    xpos = longest_line + 2
    ypos = 0
    width = stdscr.getmaxyx()[1] - (longest_line + 5)
    stdscr.move(ypos, xpos)
    stdscr.addstr("╦" + "═" * width + "╗")
    for item in options:
        ypos += 1
        stdscr.move(ypos, xpos)
        if searchResults and ypos == 2:
            item = "📋 All"
        stdscr.addstr("║" + item + " " * (width - len(item) - 1) + "║")
    stdscr.move(ypos + 1, xpos)
    stdscr.addstr("╠" + "═" * width + "╣")


def displayBookOptions(stdscr):
    options = ["➕ Add", "➖ Remove"]
    width = stdscr.getmaxyx()[1] - (longest_line + 5)
    height = stdscr.getmaxyx()[0]
    if height > len(text):
        height = len(text) + 4
    stdscr.move(5, longest_line + 2)
    stdscr.addstr("║" + " " * width + "║")

    for y in range(6, height - 3, 1):
        stdscr.move(y, longest_line + 2)
        stdscr.addstr("║" + " " * width + "║\n")

    if selected > 0 and selected <= len(books):
        for i in range(2):
            stdscr.move(5 + i, longest_line + 2)
            stdscr.addstr("║" + options[i])

    stdscr.move(height - 3, longest_line + 2)
    stdscr.addstr("╩" + "═" * width + "╝")


def placeScrollbar(stdscr):
    global scroll
    if searchMode:
        scroll = 0
        return
    
    max_scroll = len(text) - screen_height + 4
    try:
        scroll_pct = int((scroll / max_scroll) * 100)
    except:
        scroll_pct = 0
    stdscr.move(int((screen_height - 5) * scroll_pct / 100) + 1, longest_line + 2)
    

def handleClick(stdscr, x, y):
    global selected, option, run, books
    if x <= longest_line:
        selected = math.ceil((y + scroll) / 5)
        stdscr.addstr(f"{selected}")
        stdscr.clrtoeol()
    else:
        if selected > 0:
            run = False
            key = list(searchResults.keys())[selected - 1] if searchResults else selected

            if y == 5:
                books[key]["quantity"] += 1
            elif y == 6 and books[key]["quantity"] > 0:
                books[key]["quantity"] -= 1
            else:
                run = True

        if y > 0 and y < 3:
            option = y
        elif y == 3:
            sys.exit()


def handleOptions(stdscr):
    global searchResults, searchMode, run, option
    if option > 0 and option < 3:
        curses.curs_set(2)
        stdscr.move(0, 0)
        stdscr.clrtobot()
        if option == 1:
            addBook(stdscr)
        else:
            if not searchResults:
                searchResults = search(books, get_input(stdscr, "Search: "))
            else:
                searchResults = {}
                searchMode = True
                run = False
        option = 0
        curses.curs_set(1)
        displayMenu(stdscr)


def handleUserInput(stdscr):
    global scroll, selected, screen_height, run, searchMode

    if searchMode:
        searchMode = False
        selected = 0
        return
    
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
            handleClick(stdscr, x, y)
    stdscr.clrtobot()
    screen_height = stdscr.getmaxyx()[0]


def displayMenu(stdscr):
    displayBooks(stdscr)
    displayOptionPanel(stdscr)
    displayBookOptions(stdscr)
    stdscr.clrtobot()
    

def displayLibrary(stdscr):
    global text, longest_line, screen_height, run, option, searchResults, searchMode
    run = True
    text = []
    booksToShow = searchResults if searchResults else books

    for book in booksToShow:
        text.append(f"ID: {book}")
        for item in booksToShow[book]:
            text.append(f"{item.capitalize()}: {booksToShow[book][item]}")

        text.append("")
        if len(searchResults) == 1:
            text.append("")  # Append an extra space to cover up left out space

    longest_line = len(max(text, key=len))
    if longest_line > OPTIONS_MAX_WIDTH:
        longest_line = OPTIONS_MAX_WIDTH
    screen_height = stdscr.getmaxyx()[0]

    # Enable mouse support
    curses.mousemask(curses.ALL_MOUSE_EVENTS)

    while run:
        displayMenu(stdscr)
        handleOptions(stdscr)
        placeScrollbar(stdscr)
        handleUserInput(stdscr)
