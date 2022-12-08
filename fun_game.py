# By submitting this assignment, I agree to the following:
#   "Aggies do not lie, cheat, or steal, or tolerate those who do."
#   "I have not given or received any unauthorized aid on this assignment."
#
# Names:        Sriram Gaddam
#               Taylor Bell
#               Kash Kalvakota
# Section:      510
# Assignment:   Lab 13
# Date:         7 December, 2022

# Based of Chat Noir originally created by Taro Ito in 2007

# Imports
from turtle import *
from tkinter import TclError
from random import randint
from time import ctime, time
from math import cos, sin, pi
from collections import deque
import sys

# Try importing winsound
winsound_imported = True
try:
    from winsound import PlaySound, SND_NODEFAULT
except ModuleNotFoundError:
    print("winsound was not imported.\n")
    winsound_imported = False

    import os

# Time since program started
begin_time = time()

# Variables
game_title = "Catch the Cat"
game_instructions = f"Don't let the {game_title.split()[-1]} escape! Try to trap the {game_title.split()[-1].lower()} \
by clicking on squares to build walls."
show_logo = True
show_end_screens = True
sound_on = False
hints_on = False

# Sound effects
click_sound_effect = "Click Sound Effect.wav"
move_sound_effect = "Move Sound Effect.wav"
win_sound_effect = "Win Sound Effect.wav"
lose_sound_effect = "Lose sound effect.wav"

start_game = False
game_end = False
game_end_count = 0

screen = Screen()
screen_width = 700
screen_height = 650
setup(screen_width, screen_height)
title(game_title)

# Matrix of the board
mat = []

wins = 0
losses = 0
total_num_clicks = 0
curr_num_clicks = 0
avg_num_clicks = 0

# Cat position
cat_x = 0
cat_y = 0
visited = set()
frontier = deque()
solution = {}

# Board dynamic variables
num_rows = 10
num_cols = 10
border_width = 2
cell_size = round((screen_width + screen_height) / (2 * max(num_rows, num_cols)))
cell_size = cell_size // 10 * 10 - 10  # Make the cell size a multiple of 10
border_col_weight = (border_width * (num_cols + 1))
border_row_weight = (border_width * (num_rows + 1))
horizontal_margin = (screen_width - (cell_size * num_cols) - border_col_weight) / 2 + num_cols
vertical_margin = (screen_height - (cell_size * num_rows) - border_row_weight) / 2 + num_rows + 30

# Console instructions
print(f"Welcome to {game_title}!\n")
print(game_instructions)


def default_functions():
    """Makes turtle fast, invisible, and background color black"""
    hideturtle()
    speed(0)
    tracer(0, 0)
    bgcolor("#000000")


default_functions()


def play_sound(sound):
    """Play a sound, but if not found output console message"""
    global sound_on

    if winsound_imported:
        try:
            if sound_on:
                PlaySound(sound, SND_NODEFAULT)
        except (RuntimeError, NameError) as error:
            print(f"{sound} was not found\n{error}\n")


def start_check(x, y):
    """Checks if the user clicked to start the game"""
    global start_game
    play_sound(click_sound_effect)
    start_game = True


screen.onclick(start_check)

# Draw logo
if show_logo:
    logo_color = 128 / 255
    logo_rotation = 59
    logo_weight = 0

    # Draw the red spiral
    for i in range(61):
        pensize(logo_weight)
        pencolor((logo_color, 0, 0))

        logo_color -= 0.0075
        logo_weight += 0.01

        if i % 2 < 1:
            forward(i * 10)
        else:
            back(i * 10)

        right(logo_rotation)

    penup()

    # Text
    setpos(0, 0)

    game_title_start = 100
    game_title_stop = 255
    for i in range(game_title_start, game_title_stop):
        pencolor((i - game_title_start) / game_title_stop, 0, 0)
        write(game_title, False, align="center", font=("Arial", round(i / 5) + 1, "normal"))

    setpos(0, -200)
    pencolor("#FFFFFF")
    write("Created by Sriram Gaddam, Taylor Bell, and Kash Kalvakota",
          False, align="center", font=("Arial", 8, "normal"))

    game_title_weight = 3
    game_title_weight_iterations = 20
    for i in range(game_title_weight_iterations):
        setpos(cos(i) * game_title_weight, sin(i) * game_title_weight)
        write(game_title, False, align="center", font=("Arial", round(game_title_stop / 5) + 1, "normal"))

    pencolor((game_title_stop - game_title_start) / game_title_stop, 0, 0)
    setpos(0, 0)
    write(game_title, False, align="center", font=("Arial", round(game_title_stop / 5) + 1, "normal"))

    setpos(0, -300)

    start_game_timer = 0
    while not start_game:
        start_game_timer_color = abs(sin(start_game_timer / 100))
        pencolor(start_game_timer_color, start_game_timer_color, start_game_timer_color)
        write("Click to continue", False, align="center", font=("Arial", 15, "normal"))
        start_game_timer += 1

        if start_game_timer > 1000 * pi:
            start_game_timer = 0
    else:
        reset()


def reset_pen():
    """Reset turtle pen color and size"""
    pensize(border_width)
    pencolor("#FFFFFF")


def draw_rect(x=xcor(), y=ycor(), w=cell_size, h=cell_size, c="#000000", c2="#FFFFFF"):
    """Draws a rectangle at specified x-coordinate, y-coordinate, width, height, and color"""
    pencolor(c2)
    up()
    goto(x, y)
    seth(0)
    down()
    fillcolor(c)
    begin_fill()
    fd(w)
    left(90)
    fd(h)
    left(90)
    fd(w)
    left(90)
    fd(h)
    left(90)
    end_fill()
    pencolor("#FFFFFF")


def draw_circle(x=xcor(), y=ycor(), r=(cell_size / 2), c="#000000"):
    """Draws a circle at specified x-coordinate, y-coordinate, radius, and color"""
    up()
    goto(x, y - r)
    seth(0)
    down()
    fillcolor(c)
    begin_fill()
    circle(r, 360, 150)
    end_fill()


def draw_wall(x, y, c="#FFFFFF"):
    """Draws a wall which blocks the cat"""
    global mat
    mat[x][y] = "W"
    draw_rect((-screen_width / 2) + horizontal_margin + (y * cell_size),
              (-screen_height / 2) + vertical_margin + (x * cell_size), cell_size, cell_size, c)


def draw_empty_cell(x, y, c="#000000"):
    """Draws an empty cell of the game board"""
    global mat
    mat[x][y] = "0"
    draw_rect((-screen_width / 2) + horizontal_margin + (y * cell_size),
              (-screen_height / 2) + vertical_margin + (x * cell_size), cell_size, cell_size, c)


def draw_cat(x=xcor(), y=ycor(), w=cell_size, h=cell_size, c="#FFFFFF"):
    """Draws a cat at specified x-coordinate, y-coordinate, width, height, and color"""
    x += cell_size / 2
    y += cell_size / 2
    w *= 0.75
    h *= 0.75
    pensize(1)
    pencolor(c)
    up()
    goto(x, y)
    seth(0)
    down()

    # Body
    draw_circle(x, y, (w + h) / 4, c)

    # Left eye
    draw_circle(x - 10, y - 5, 5, "#000000")

    # Right eye
    draw_circle(x + 10, y - 5, 5, "#000000")

    # Left ear
    up()
    goto(x - 20, y + 20)
    seth(0)
    down()
    fillcolor(c)
    begin_fill()
    begin_poly()
    left(280)
    fd(20)
    right(240)
    fd(25)
    end_poly()
    end_fill()

    # Right ear
    up()
    goto(x + 20, y + 20)
    seth(0)
    down()
    fillcolor(c)
    begin_fill()
    begin_poly()
    left(260)
    fd(20)
    left(240)
    fd(25)
    end_poly()
    end_fill()

    # Reset to default
    reset_pen()


def game_text():
    """Displays GUI (score, wins, losses, instructions, buttons, etc.)"""
    global wins, losses, curr_num_clicks, avg_num_clicks, game_end, sound_on, show_end_screens

    # Wins and losses
    up()
    score_box_width = 60 + len(str(wins)) * 5 + len(str(losses)) * 5
    draw_rect(-score_box_width, screen_height / 2 - 35, score_box_width * 2, 30)

    up()
    setpos(0, screen_height / 2 - 30)
    write(f"Wins: {wins} Losses: {losses}", align="center", font=("Arial", 12, "normal"))

    # Current number of clicks in game and average number of clicks per game
    up()
    draw_rect(-screen_width / 2 + 165 - 140, screen_height / 2 - 35, 140, 30)

    up()
    setpos(95 - screen_width / 2, screen_height / 2 - 30)
    write(f"Clicks: {curr_num_clicks} Avg: {avg_num_clicks:.1f}", align="center", font=("Arial", 12, "normal"))

    # Instructions
    up()
    draw_rect(-screen_width / 2, -screen_height / 2 + 10, screen_width, 35, "#1f1f1f", "#1f1f1f")

    up()
    setpos(0, -screen_height / 2 + 20)
    write(game_instructions, align="center", font=("Arial", 12, "normal"))

    # Draw quit button
    draw_rect(screen_width / 2 - 50, screen_height / 2 - 30, 50, 30, "#800000", "#000000")
    up()

    # Draw quit button text
    setpos(screen_width / 2 - 50 + 20, screen_height / 2 - 30 + 5)
    write("Quit", align="center", font=("Arial", 12, "normal"))

    if winsound_imported:
        # Draw sound button
        if sound_on:
            draw_rect(screen_width / 2 - 150, screen_height / 2 - 30, 80, 30, "#778899", "#000000")

            up()
            setpos(screen_width / 2 - 150 + 40, screen_height / 2 - 30 + 5)
            write("Sound on", align="center", font=("Arial", 12, "normal"))
        else:
            draw_rect(screen_width / 2 - 150, screen_height / 2 - 30, 80, 30, "#808080", "#000000")

            up()
            setpos(screen_width / 2 - 150 + 40, screen_height / 2 - 30 + 5)
            write("Sound off", align="center", font=("Arial", 12, "normal"))

    # Draw show_end_screens button
    if show_end_screens:
        draw_rect(screen_width / 2 - 250, screen_height / 2 - 30, 80, 30, "#778899", "#000000")

        up()
        setpos(screen_width / 2 - 250 + 40, screen_height / 2 - 30 + 10)
        write("Hide", align="center", font=("Arial", 10, "normal"))
    else:
        draw_rect(screen_width / 2 - 250, screen_height / 2 - 30, 80, 30, "#808080", "#000000")

        up()
        setpos(screen_width / 2 - 250 + 40, screen_height / 2 - 30 + 10)
        write("Show", align="center", font=("Arial", 10, "normal"))
    up()
    setpos(screen_width / 2 - 250 + 40, screen_height / 2 - 30)
    write("Game end", align="center", font=("Arial", 8, "normal"))


def reset_board():
    """Resets the game board"""
    global cat_x, cat_y, mat, game_end, game_end_count

    game_end = False
    game_end_count = 0

    bgpic("nopic")
    bgcolor("#000000")
    reset_pen()
    mat = []

    # Set all elements of mat to 0 (empty)
    for i in range(num_cols):
        temp = []
        for j in range(num_rows):
            temp.append("0")
        mat.append(temp)

    # Draw empty board
    for i in range(num_rows):
        for j in range(num_cols):
            draw_empty_cell(i, j)

            # Make outer edge red
            if mat[i][j] == "0" and i == 0 or i == num_cols - 1 or j == 0 or j == num_rows - 1:
                draw_empty_cell(i, j, "#210000")
            # Draw checkerboard pattern
            elif (i + j) % 2 == 0:
                draw_empty_cell(i, j, "#141414")

    # Randomize cat position
    cat_x = randint(4, 6)
    cat_y = randint(4, 6)
    mat[cat_x][cat_y] = "X"
    draw_cat((-screen_width / 2) + horizontal_margin + (cat_y * cell_size),
             (-screen_height / 2) + vertical_margin + (cat_x * cell_size))

    # Draw random walls
    max_num_walls = 3
    curr_num_walls = 0
    for x in range(max_num_walls):
        i = randint(0, 9)
        j = randint(0, 9)

        if curr_num_walls < max_num_walls and mat[i][j] == "0":
            draw_wall(i, j)
            curr_num_walls += 1

    # Draw game GUI such as score, buttons, and instructions
    if not game_end:
        game_text()


def game_win_screen():
    """Draws fallback game win screen"""
    reset()
    bgpic("nopic")
    up()
    setpos(0, 0)
    pencolor("#FFFFFF")

    write("You won!", align="center", font=("Arial", 32, "normal"))
    print("Game Win image not found")

    reset_pen()


def game_over_screen():
    """Draws fallback game over screen"""
    reset()
    bgpic("nopic")
    up()
    setpos(0, 0)
    pencolor("#FFFFFF")

    write("You lose...", align="center", font=("Arial", 32, "normal"))
    print("Game Over image not found")

    reset_pen()


def end_game():
    """Close game, output time played and score to catchTheCatScore.txt"""
    global begin_time, wins, losses, avg_num_clicks, game_end
    # Output game session score to console
    print("\nSuccessfully exited!\n")

    try:
        # Time calculations
        m, s = divmod(time() - begin_time, 60)
        h, m = divmod(m, 60)

        print(f"Start time: {ctime(begin_time)}")
        # print(f"End time: {ctime()}")  # Redundant information
        print(f"Played for: {h:.0f}:{m:.0f}:{s:.0f}\n")

        print(f"Wins: {wins} Losses: {losses}")
        print(f"Average number of clicks per game: {avg_num_clicks:.1f}")

        # Write game session score to catchTheCatScore.txt as well
        output_file = open("catchTheCatScore.txt", "a")

        output_file.write(f"Start time: {ctime(begin_time)}\n")
        # output_file.write(f"End time: {ctime()}\n")
        output_file.write(f"Played for: {h:.0f}:{m:.0f}:{s:.0f}\n")

        output_file.write(f"Wins: {wins} Losses: {losses}\n")
        output_file.write(f"Average number of clicks per game: {avg_num_clicks:.1f}\n\n")
        output_file.close()
    except TypeError:
        print("Error computing time")

    game_end = True
    bye()
    sys.exit()


def cat_up_check(x, y):
    """Check if the cell above the cat is not a wall"""
    global game_end, num_rows, mat

    if not game_end and x + 1 < num_rows and mat[x + 1][y] != "W":
        return True
    return False


def cat_down_check(x, y):
    """Check if the cell below the cat is not a wall"""
    global game_end, mat

    if not game_end and x - 1 >= 0 and mat[x - 1][y] != "W":
        return True
    return False


def cat_left_check(x, y):
    """Check if the cell west of the cat is not a wall"""
    global game_end, mat

    if not game_end and y - 1 >= 0 and mat[x][y - 1] != "W":
        return True
    return False


def cat_right_check(x, y):
    """Check if the cell east of the cat is not a wall"""
    global game_end, num_cols, mat

    if not game_end and y + 1 < num_cols and mat[x][y + 1] != "W":
        return True
    return False


def cat_move_up():
    """Move cat left 1 cell if there is not a wall"""
    global game_end, num_rows, num_cols, cat_x, cat_y, mat

    if cat_up_check(cat_x, cat_y):
        draw_empty_cell(cat_x, cat_y)
        cat_x += 1
        mat[cat_x][cat_y] = "X"

        return True
    return False


def cat_move_down():
    """Move cat down 1 cell if there is not a wall"""
    global game_end, num_rows, num_cols, cat_x, cat_y, mat

    if cat_down_check(cat_x, cat_y):
        draw_empty_cell(cat_x, cat_y)
        cat_x -= 1
        mat[cat_x][cat_y] = "X"

        return True
    return False


def cat_move_left():
    """Move cat left 1 cell if there is not a wall"""
    global game_end, num_rows, num_cols, cat_x, cat_y, mat

    if cat_left_check(cat_x, cat_y):
        draw_empty_cell(cat_x, cat_y)
        cat_y -= 1
        mat[cat_x][cat_y] = "X"

        return True
    return False


def cat_move_right():
    """Move cat right 1 cell if there is not a wall"""
    global game_end, num_rows, num_cols, cat_x, cat_y, mat

    if cat_right_check(cat_x, cat_y):
        draw_empty_cell(cat_x, cat_y)
        cat_y += 1
        mat[cat_x][cat_y] = "X"

        return True
    return False


def cat_random_move():
    """Moves the cat up, down, left or right 1 space randomly once while checking for walls"""
    global game_end, num_rows, num_cols, cat_x, cat_y, mat

    # If above, below, right, left of cat's position is open
    north, south, east, west = False, False, False, False

    # The number of directions open for the cat
    random_move_total = 0

    # Check position above cat
    if cat_up_check(cat_x, cat_y):
        north = True
        random_move_total += 1
    # Check position below cat
    if cat_down_check(cat_x, cat_y):
        south = True
        random_move_total += 1
    # Check position left of cat
    if cat_left_check(cat_x, cat_y):
        west = True
        random_move_total += 1
    # Check position right of cat
    if cat_right_check(cat_x, cat_y):
        east = True
        random_move_total += 1

    # Move randomly
    if random_move_total > 0:
        random_move_num = randint(1, random_move_total)
        if random_move_num == 1:
            while True:
                if north:
                    south = False
                    west = False
                    east = False
                    break
                if south:
                    north = False
                    west = False
                    east = False
                    break
                if west:
                    south = False
                    north = False
                    east = False
                    break
                if east:
                    south = False
                    west = False
                    north = False
                    break
        elif random_move_num == 2:
            while True:
                if south:
                    north = False
                    west = False
                    east = False
                    break
                if west:
                    south = False
                    north = False
                    east = False
                    break
                if east:
                    south = False
                    west = False
                    north = False
                    break
                if north:
                    south = False
                    west = False
                    east = False
                    break
        elif random_move_num == 3:
            while True:
                if west:
                    south = False
                    north = False
                    east = False
                    break
                if east:
                    south = False
                    west = False
                    north = False
                    break
                if north:
                    south = False
                    west = False
                    east = False
                    break
                if south:
                    north = False
                    west = False
                    east = False
                    break
        else:
            while True:
                if east:
                    south = False
                    west = False
                    north = False
                    break
                if north:
                    south = False
                    west = False
                    east = False
                    break
                if south:
                    north = False
                    west = False
                    east = False
                    break
                if west:
                    south = False
                    north = False
                    east = False
                    break

    # Check position above cat
    if north:
        cat_move_up()
    # Check position below cat
    elif south:
        cat_move_down()
    # Check position left of cat
    elif west:
        cat_move_left()
    # Check position right of cat
    elif east:
        cat_move_right()
    else:
        return False
    return True


def reset_search():
    """Resets searching variables"""
    global visited, frontier, solution
    visited = set()
    frontier = deque()
    solution = {}


def back_route(x, y):
    """Path from the edge of the board back to current cat position"""
    global game_end, num_rows, num_cols, cat_x, cat_y, mat, visited, frontier, solution

    # Destination coordinate for cat to reach border
    destination_x = x
    destination_y = y

    # List of all moves the cat needs to reach the border
    move_list = []

    while (x, y) != (cat_x, cat_y):  # Stop loop when current cells == start cell
        x, y = solution[x, y]  # "key value" now becomes the new key

        move_list.append([x, y])

        if hints_on:
            draw_empty_cell(x, y, "#0000ff")

    # The difference in where the cat currently is and where the next step to reaching the border is
    x_diff = 0
    y_diff = 0

    if len(move_list) > 1:
        x_diff = move_list[-2][0] - move_list[-1][0]
        y_diff = move_list[-2][1] - move_list[-1][1]
    else:
        x_diff = destination_x - move_list[0][0]
        y_diff = destination_y - move_list[0][1]

    # Difference from where the cat should go and currently is
    if x_diff > 0:
        cat_move_up()
    elif x_diff < 0:
        cat_move_down()
    elif y_diff > 0:
        cat_move_right()
    elif y_diff < 0:
        cat_move_left()


def search(x, y):
    """Calculates the shortest path from the cat's current position to the end of the board"""
    global game_end, num_rows, num_cols, cat_x, cat_y, mat, visited, frontier, solution

    frontier.append((x, y))
    solution[x, y] = x, y

    while len(frontier) > 0:  # Exit while loop when frontier queue equals zero
        x, y = frontier.popleft()  # Pop next entry in the frontier queue an assign to x and y location

        # Check the cell on the left
        if cat_left_check(x, y) and (x, y - 1) not in visited:
            cell = (x, y - 1)
            solution[cell] = x, y  # Backtracking routine [cell] is the previous cell. x, y is the current cell

            frontier.append(cell)  # Add cell to frontier list
            visited.add((x, y - 1))  # Add cell to visited list

        # Check the cell below
        if cat_down_check(x, y) and (x - 1, y) not in visited:
            cell = (x - 1, y)
            solution[cell] = x, y

            frontier.append(cell)
            visited.add((x - 1, y))

        # Check the cell on the right
        if cat_right_check(x, y) and (x, y + 1) not in visited:
            cell = (x, y + 1)
            solution[cell] = x, y

            frontier.append(cell)
            visited.add((x, y + 1))

        # Check the cell above
        if cat_up_check(x, y) and (x + 1, y) not in visited:
            cell = (x + 1, y)
            solution[cell] = x, y

            frontier.append(cell)
            visited.add((x + 1, y))

        # If the cat found the edge of the board
        if x == 0 or x == num_cols - 1 or y == 0 or y == num_rows - 1:
            # The path from the destination to the current position
            back_route(x, y)

            # Show the path the cat will take to escape
            if hints_on:
                draw_empty_cell(x, y, "#ff0000")

            reset_search()
            return True

    cat_random_move()
    reset_search()
    return False


def check_click(x, y):
    """Checks mouse position to draw walls and interact with buttons"""
    global total_num_clicks, curr_num_clicks, avg_num_clicks, cat_x, cat_y, mat, wins, losses, game_end, \
        game_end_count, sound_on, show_end_screens

    try:
        default_functions()

        # After game over or win
        if game_end:
            play_sound(click_sound_effect)
            game_end_count += 1

        # If mouse clicked after game over or win
        if game_end_count > 0:
            reset_board()
        else:

            # Check mouse position to click quit button
            if screen_width / 2 - 50 < x < screen_width / 2 and screen_height / 2 - 30 < y < screen_height:
                play_sound(click_sound_effect)
                end_game()

            # Toggle sound
            if winsound_imported and \
                    screen_width / 2 - 150 < x < screen_width / 2 - 70 and screen_height / 2 - 30 < y < screen_height:
                play_sound(click_sound_effect)
                sound_on = not sound_on

            # Toggle show_end_screens
            if screen_width / 2 - 250 < x < screen_width / 2 - 170 and screen_height / 2 - 30 < y < screen_height:
                play_sound(click_sound_effect)
                show_end_screens = not show_end_screens

            for i in range(num_rows):
                for j in range(num_cols):
                    x_min = (-screen_width / 2) + horizontal_margin + (j * cell_size)
                    x_max = (-screen_width / 2) + horizontal_margin + (j * cell_size) + cell_size
                    y_min = (-screen_height / 2) + vertical_margin + (i * cell_size)
                    y_max = (-screen_height / 2) + vertical_margin + (i * cell_size) + cell_size

                    # Place a wall down
                    if not game_end and mat[i][j] == "0" and x_min < x < x_max and y_min < y < y_max:
                        play_sound(move_sound_effect)
                        draw_wall(i, j)

                        curr_num_clicks += 1
                        total_num_clicks += 1

                        # Make the cat move randomly, return false if it can't move
                        if search(cat_x, cat_y):
                            pass
                        # Cat is trapped
                        else:
                            play_sound(win_sound_effect)
                            wins += 1
                            game_end = True

                            # Reset game immediately if show_end_screens is False
                            if not show_end_screens:
                                reset_board()
                            else:
                                # Try to get game win image
                                try:
                                    reset()
                                    bgpic("Game Win Image.gif")
                                except TclError:
                                    game_win_screen()

                            avg_num_clicks = total_num_clicks / (wins + losses)
                            curr_num_clicks = 0

                        # If the cat reaches the edge of the board
                        if cat_x == 0 or cat_x == num_cols - 1 or cat_y == 0 or cat_y == num_rows - 1:
                            play_sound(lose_sound_effect)
                            losses += 1
                            game_end = True

                            # Reset game immediately if show_end_screens is False
                            if not show_end_screens:
                                reset_board()
                            else:
                                # Try to get game over image
                                try:
                                    reset()
                                    bgpic("Game Over Image.gif")
                                except TclError:
                                    game_over_screen()

                            avg_num_clicks = total_num_clicks / (wins + losses)
                            curr_num_clicks = 0

                        # Draw cat
                        if not game_end:
                            draw_cat((-screen_width / 2) + horizontal_margin + (cat_y * cell_size),
                                     (-screen_height / 2) + vertical_margin + (cat_x * cell_size))

                    # Draw checkerboard pattern
                    if not game_end and mat[i][j] == "0" and (i + j) % 2 == 0 and \
                            not(i == 0 or i == num_cols - 1 or j == 0 or j == num_rows - 1):
                        draw_empty_cell(i, j, "#141414")

            # Draw game GUI such as score, buttons, and instructions
            if not game_end:
                game_text()

    # Close the game if turtle.Terminator throws an error
    except (Terminator, KeyboardInterrupt):
        end_game()


# Start the game by resetting the board for the first time
reset_board()

# Check clicks in game
screen.onclick(check_click)

# Starts event loop
done()
