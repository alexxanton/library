import curses

NORMAL_COLOR = 0
SELECTED_COLOR = 1
ERROR_COLOR = 2
START_MSG = "\nPress the key for the action you want to do.\n"

key = ""
output = START_MSG
color = NORMAL_COLOR

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


def main(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    

    def get_input(msg, validator="str"):
        user_input = ""
        valid = False
        while not user_input or not valid:
            stdscr.move(7, 0)
            stdscr.addstr(msg)
            stdscr.clrtoeol()
            stdscr.refresh()
            curses.echo()  # Make user input visible
            user_input = stdscr.getstr().decode("utf-8").strip()  # Read user input as a string
            curses.noecho()  # Hide input again after capturing
            if validator == "int" and user_input.isnumeric() or validator == "str":
                valid = True

        return user_input
    

    def addBook():
        id = len(library) + 1
        title = get_input("Enter the title: ")
        author = get_input("Enter the author: ")
        quantity = get_input("Enter the quantity: ", "int")
        
        library.update({id: {"title": title, "author": author, "quantity": int(quantity)}})
        stdscr.addstr(f"\nBook added successfully\n")
        stdscr.refresh()


    def searchBook():
        pass


    def showBooks():
        text = []
        for book in library:
            text.append(f"ID: {book}")
            for item in library[book]:
                text.append(f"{item.capitalize()}: {library[book][item]}")
            text.append("")

        index = 0
        longest_line = len(max(text, key=len))

        # Enable mouse support
        curses.mousemask(curses.ALL_MOUSE_EVENTS)

        while True:
            stdscr.move(7, 0)
            stdscr.addstr("╔" + "═" * longest_line + "╗\n")
            for line in range(index, len(text), 1):
                stdscr.addstr(f"║{text[line]}" + " " * (longest_line - len(text[line])) + "║\n")
                if stdscr.getyx()[0] + 4 > stdscr.getmaxyx()[0]:
                    break
            stdscr.addstr("╚" + "═" * longest_line + "╝\n")

            stdscr.refresh()

            # Handle user input
            key = stdscr.getch()
            if key == 10:  # Enter key
                break
            elif key == curses.KEY_MOUSE:  # Mouse event
                id, x, y, z, bstate = curses.getmouse()
                if bstate & curses.BUTTON4_PRESSED:  # Scroll up
                    index -= 1 if index > 0 else 0
                elif bstate & curses.BUTTON5_PRESSED:  # Scroll down
                    index += 1 if index + stdscr.getmaxyx()[0] - 10 < len(text) else 0
                elif curses.BUTTON1_PRESSED:  # Scroll down
                    stdscr.addstr(f"{y}")


            stdscr.addstr(f"{index}")


    def borrowBook():
        pass


    def exit():
        stdscr.addstr("Exiting the menu...\n")
        stdscr.refresh()


    options = {
        "1": {"desc": "Add a new book\n", "func": addBook},
        "2": {"desc": "Search for a book\n", "func": searchBook},
        "3": {"desc": "Show all books\n", "func": showBooks},
        "4": {"desc": "Borrow a book\n", "func": borrowBook},
        "5": {"desc": "Exit\n", "func": exit}
    }
    

    def get_option():
        global key, output, color
        stdscr.clear()

        for opt in options:
            stdscr.addstr(f"{opt}. ", curses.color_pair(1))
            stdscr.addstr(f"{options[opt]['desc']}")
        stdscr.addstr(output, curses.color_pair(color))

        if key in options:
            options[key]["func"]()
            key = ""
            output = START_MSG
            color = NORMAL_COLOR
            stdscr.addstr("Press enter to continue...")
            while True:
                if stdscr.getch() == 10:
                    break
            return

        key = chr(stdscr.getch())
        if key in options:
            output = f"\n{options[key]['desc']}"
            color = SELECTED_COLOR
        else:
            output = "\nInvalid option\n"
            color = ERROR_COLOR

        stdscr.refresh()


    while True:
        get_option()

curses.wrapper(main)
