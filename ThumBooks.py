'''
ThumBooks is an eBook reader for the TinyCircuits Thumby. It can only handle plain
text files, so you'll want to convert your eBooks to .txt files. Also, the default
fonts on Thumby can't display certain special characters, so you may want to check
your text files for special characters and replace or remove them. Place .txt files
in the root directory. After opening ThumBooks, use up and down on the D-pad to
select a book from the menu, and press A to open the book or B to close ThumBooks.
Use left and right on the D-pad to turn pages. Press A to set a bookmark or B to
close the book. Closing a book automatically sets a bookmark at the current page.
Reopening the book returns to the last page bookmarked. When reading a book, use
up on the D-pad to return to the beginning of the book and down to return to the
last page bookmarked.
'''

import thumby
import os

# Constants
LINES_PER_PAGE = 6
CHARS_PER_LINE = 18
MENU_ITEMS_VISIBLE = 5

# Set the smaller font
thumby.display.setFont("/lib/font3x5.bin", 3, 5, 1)

# Set save data directory
thumby.saveData.setName("ThumBooks")

# Load bookmarks
def load_bookmark(filename):
    if thumby.saveData.hasItem(filename):
        return thumby.saveData.getItem(filename)
    return 0

# Save bookmark
def save_bookmark(filename, page):
    thumby.saveData.setItem(filename, page)
    thumby.saveData.save()

# Get list of text files
def list_files():
    try:
        all_files = os.listdir("/")
        return [f for f in all_files if f.lower().endswith('.txt')]
    except Exception as e:
        return ["Error: " + str(e)]

# Read and format text with word wrapping

def read_page(filename, start_index):
    try:
        lines = []
        text_lines = []
        current_index = 0

        with open("/" + filename, "r") as f:
            for raw_line in f:
                raw_words = raw_line.strip().split()
                temp_line = ""

                for word in raw_words:
                    if len(temp_line) + len(word) + (1 if temp_line else 0) <= CHARS_PER_LINE:
                        temp_line += (" " if temp_line else "") + word
                    else:
                        text_lines.append(temp_line)
                        temp_line = word

                    if len(text_lines) >= start_index + LINES_PER_PAGE:
                        break

                if temp_line:
                    text_lines.append(temp_line)

                if len(text_lines) >= start_index + LINES_PER_PAGE:
                    break

        text_lines = text_lines[start_index:start_index + LINES_PER_PAGE]

        if not text_lines:
            return ["EOF reached"], True

        return text_lines, len(text_lines) < LINES_PER_PAGE
    except Exception as e:
        return ["Read error", "Check file!", str(e)], True

# Main menu logic
def main_menu():
    files = list_files()
    if not files or files[0].startswith("Error"):
        thumby.display.fill(0)
        thumby.display.drawText(files[0] if files else "No files", 0, 0, 1)
        thumby.display.update()
        while not thumby.buttonB.justPressed():
            pass
        return

    selected = 0
    top_index = 0

    while True:
        thumby.display.fill(0)
        thumby.display.drawText("Select File:", 0, 0, 1)

        for i in range(MENU_ITEMS_VISIBLE):
            idx = top_index + i
            if idx < len(files):
                marker = ">" if idx == selected else " "
                thumby.display.drawText(marker + files[idx][:18], 0, 6 + (i * 6), 1)

        thumby.display.update()

        if thumby.buttonU.justPressed():
            selected = (selected - 1) % len(files)
            if selected < top_index:
                top_index = selected
            elif selected == len(files) - 1:
                top_index = max(0, len(files) - MENU_ITEMS_VISIBLE)

        if thumby.buttonD.justPressed():
            selected = (selected + 1) % len(files)
            if selected >= top_index + MENU_ITEMS_VISIBLE:
                top_index += 1
            elif selected == 0:
                top_index = 0

        if thumby.buttonA.justPressed():
            read_book(files[selected])

        if thumby.buttonB.justPressed():
            return

# Book reading logic
def read_book(filename):
    start_index = load_bookmark(filename)
    eof_reached = False

    while True:
        text_lines, eof_reached = read_page(filename, start_index)
        thumby.display.fill(0)

        for i, line in enumerate(text_lines):
            thumby.display.drawText(line, 0, i * 6, 1)

        thumby.display.update()

        if thumby.buttonL.justPressed() and start_index > 0:
            start_index -= LINES_PER_PAGE
        if thumby.buttonR.justPressed() and not eof_reached:
            start_index += LINES_PER_PAGE
        if thumby.buttonB.justPressed():
            save_bookmark(filename, start_index)
            return

        if thumby.buttonU.justPressed():
            start_index = 0

        if thumby.buttonD.justPressed():
            start_index = load_bookmark(filename)

        if thumby.buttonA.justPressed():
            save_bookmark(filename, start_index)

# Start the app
main_menu()
