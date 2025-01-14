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
search_mode = False
search_results = {}

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


def add_book(stdscr):
    global run
    id = len(books) + 1
    title = get_input(stdscr, "Enter the title: ")
    author = get_input(stdscr, "Enter the author: ")
    quantity = get_input(stdscr, "Enter the quantity: ", "int")
    
    # Update the books dictionary with the new book details
    books.update({id: {"title": title, "author": author, "quantity": int(quantity)}})
    stdscr.refresh()
    run = False  # Exit the current loop to refresh the display with the new book


def search(books, query):
    global search_mode, run

    # Normalize the input to lowercase and split into keywords for better matching
    query = query.lower().split()
    results = {}

    for item in range(1, len(books), 1):
        string_lower = books[item]["title"].lower()
        current_index = 0
        match = True

        # Check if all query parts are in the book title in order
        for word in query:
            current_index = string_lower.find(word, current_index)
            if current_index == -1:  # Word not found
                match = False
                break
            current_index += len(word)  # Move index forward to maintain order

        if match:
            results[item] = books[item]

    if len(results) > 0:
        search_mode = True  # Enable search mode to display search results
        run = False  # Exit the current loop to refresh the display with search results

    return results


def display_books(stdscr):
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


def display_option_panel(stdscr):
    options = ["➕ New", "🔎 Search", "❌ Exit"]
    xpos = longest_line + 2
    ypos = 0
    width = stdscr.getmaxyx()[1] - (longest_line + 5)
    stdscr.move(ypos, xpos)
    stdscr.addstr("╦" + "═" * width + "╗")
    for item in options:
        ypos += 1
        stdscr.move(ypos, xpos)
        if search_results and ypos == 2:
            item = "📋 All"  # Change option to "All" if search results are displayed
        stdscr.addstr("║" + item + " " * (width - len(item) - 1) + "║")
    stdscr.move(ypos + 1, xpos)
    stdscr.addstr("╠" + "═" * width + "╣")


def display_book_options(stdscr):
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


def place_scrollbar(stdscr):
    global scroll
    if search_mode:
        scroll = 0  # Reset scroll if in search mode
        return
    
    max_scroll = len(text) - screen_height + 4
    try:
        scroll_pct = int((scroll / max_scroll) * 100)
    except ZeroDivisionError:
        scroll_pct = 0
    stdscr.move(int((screen_height - 5) * scroll_pct / 100) + 1, longest_line + 2)

    
def handle_click(stdscr, x, y):
    global selected, option, run, books
    if x <= longest_line:
        selected = math.ceil((y + scroll) / 5)
        stdscr.addstr(f"{selected}")
        stdscr.clrtoeol()
    else:
        if selected > 0:
            run = False

            try:
                key = list(search_results.keys())[selected - 1] if search_results else selected
            except IndexError:
                return

            if y == 5:
                books[key]["quantity"] += 1
            elif y == 6 and books[key]["quantity"] > 0:
                books[key]["quantity"] -= 1
            else:
                run = True

        if y > 0 and y < 3:
            option = y  # Set option based on click position
        elif y == 3:
            sys.exit()


def handle_options(stdscr):
    global search_results, search_mode, run, option
    if option > 0 and option < 3:
        curses.curs_set(2)
        stdscr.move(0, 0)
        stdscr.clrtobot()
        if option == 1:
            add_book(stdscr)
        else:
            if not search_results:
                search_results = search(books, get_input(stdscr, "Search: "))  # Perform search
            else:
                search_results = {}
                search_mode = True
                run = False
        option = 0
        curses.curs_set(1)
        display_menu(stdscr)


def handle_user_input(stdscr):
    global scroll, selected, screen_height, run, search_mode

    if search_mode:
        search_mode = False
        selected = 0  # Reset selection if in search mode
        return
    
    key = stdscr.getch()
    if key == 10:  # Enter key
        return
    elif key == curses.KEY_MOUSE:
        id, x, y, z, bstate = curses.getmouse()
        if bstate & curses.BUTTON4_PRESSED:
            scroll -= 1 if scroll > 0 else 0  # Scroll up
        elif bstate & curses.BUTTON5_PRESSED:
            scroll += 1 if scroll + screen_height - 4 < len(text) else 0  # Scroll down
        elif curses.BUTTON1_PRESSED:
            handle_click(stdscr, x, y)
    stdscr.clrtobot()
    screen_height = stdscr.getmaxyx()[0]


def display_menu(stdscr):
    display_books(stdscr)
    display_option_panel(stdscr)
    display_book_options(stdscr)
    stdscr.clrtobot()

    
def display_library(stdscr):
    global text, longest_line, screen_height, run, option, search_results, search_mode
    run = True
    text = []
    books_to_show = search_results if search_results else books

    # Display the books
    for book in books_to_show:
        text.append(f"ID: {book}")
        for item in books_to_show[book]:
            text.append(f"{item.capitalize()}: {books_to_show[book][item]}")

        text.append("")
        if len(search_results) == 1:
            text.append("")  # Append an extra space to cover up left out space

    longest_line = len(max(text, key=len))
    if longest_line > OPTIONS_MAX_WIDTH:
        longest_line = OPTIONS_MAX_WIDTH
    screen_height = stdscr.getmaxyx()[0]

    # Enable mouse support
    curses.mousemask(curses.ALL_MOUSE_EVENTS)

    while run:
        display_menu(stdscr)
        handle_options(stdscr)
        place_scrollbar(stdscr)
        handle_user_input(stdscr)
