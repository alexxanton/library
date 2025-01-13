import curses
import math

NORMAL_COLOR = 0
SELECTED_COLOR = 1
ERROR_COLOR = 2
OPTIONS_MAX_WIDTH = 40

selected = 0
color = NORMAL_COLOR
scroll = 0
longest_line = 10
text = []
screen_height = 0
run = True
option = 0


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
        stdscr.move(stdscr.getmaxyx()[0] // 2 + 1, 0)
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
    id = len(books) + 1
    title = get_input(stdscr, "Enter the title: ")
    author = get_input(stdscr, "Enter the author: ")
    quantity = get_input(stdscr, "Enter the quantity: ", "int")
    
    books.update({id: {"title": title, "author": author, "quantity": int(quantity)}})
    stdscr.addstr(f"\nBook added successfully (Press enter)\n")
    stdscr.refresh()


def search(strings, query):
    # Normalize the input
    query = query.lower().split()  # Split query into keywords
    results = []

    for string in strings:
        string_lower = string.lower()
        # Check if all query parts are in the string in order
        current_index = 0
        match = True

        for word in query:
            current_index = string_lower.find(word, current_index)
            if current_index == -1:  # Word not found
                match = False
                break
            current_index += len(word)  # Move index forward to maintain order

        if match:
            results.append(string)

    return results


search_query = "py everyone"
matches = search(books, search_query)
print(matches)



def displayBooks(stdscr):
    global selected, text, scroll, longest_line, screen_height
    stdscr.move(0, 0)
    stdscr.addstr("╔" + "═" * longest_line + "╗\n")

    for line in range(scroll, len(text), 1):
        line_to_print = f"{text[line][0:longest_line:1]}" + " " * (longest_line - len(text[line]))
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


def displayInputField(stdscr):
    global option
    width = stdscr.getmaxyx()[1] - (longest_line + 5)
    height = stdscr.getmaxyx()[0]
    stdscr.move(5, longest_line + 2)
    stdscr.addstr("╔" + "═" * width + "╗\n")
    for x in range(6, height - 3, 1):
        stdscr.move(x, longest_line + 2)
        stdscr.addstr("║" + " " * width + "║\n")
    stdscr.move(height - 3, longest_line + 2)
    stdscr.addstr("╚" + "═" * width + "╝")
    if option == 1:
        curses.curs_set(2)
        stdscr.move(height // 2, 0)
        stdscr.addstr("═" * width)
        stdscr.clrtobot()
        addBook(stdscr)
    curses.curs_set(1)
    option = 0


def placeScrollIndicator(stdscr):
    max_scroll = len(text) - screen_height + 4
    scroll_pct = int((scroll / max_scroll) * 100)
    stdscr.move(int((screen_height - 5) * scroll_pct / 100) + 1, longest_line + 1)
    

def handleClick(stdscr, x, y):
    global selected, option, run
    if x <= longest_line:
        selected = math.ceil((y + scroll) / 5)
        stdscr.addstr(f"{selected}")
        stdscr.clrtoeol()
    else:
        if y > 0 and y < 3:
            option = y
        elif y == 3:
            run = False


def handleUserInput(stdscr):
    global scroll, selected, screen_height, run
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
    


def display(stdscr):
    global text, longest_line, screen_height
    text = []
    for book in books:
        text.append(f"ID: {book}")
        for item in books[book]:
            text.append(f"{item.capitalize()}: {books[book][item]}")
        text.append("")

    longest_line = len(max(text, key=len))
    if longest_line > OPTIONS_MAX_WIDTH:
        longest_line = OPTIONS_MAX_WIDTH
    screen_height = stdscr.getmaxyx()[0]

    # Enable mouse support
    curses.mousemask(curses.ALL_MOUSE_EVENTS)

    while run:
        displayBooks(stdscr)
        displayOptionPanel(stdscr)
        displayInputField(stdscr)
        placeScrollIndicator(stdscr)
        handleUserInput(stdscr)


    def borrowBook():
        pass


    def exit():
        stdscr.addstr("Exiting the menu...\n")
        stdscr.refresh()
