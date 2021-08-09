import csv
import random
import re
import os
from itertools import islice
import threading, time
import json

# Read into this later

from flask import Flask, flash, render_template, request, session, redirect

app = Flask(__name__)
app.secret_key = os.urandom(24)

questions = [] # Holds Question objects
options = [] # Determines all the columns that contain options for answers
difficulty_markers = [] # Marks where the first question in a given difficulty is
users = [] # Stores users here until db is up and running
current_questions = [] # Ties users to their current questions and deletes after

class Question:
    def __init__(self, question, answer, options):
        self.question = question # The prompt
        self.answer = answer # The correct answer
        self.options = options # Array with all options to choose from

class User:
    def __init__(self, cookie, score = 0):
        self.cookie = cookie
        self.score = score
        self.timer_thread = None

    def reduce_score(self):
        if self.score > 0:
            self.score -= 1
            print(self.score)

    def add_score(self):
        self.score += 1
        print(self.score)

class CurrentQuestion:

    kill_thread = False

    def __init__(self, user, question):
        self.user = user
        self.question = question

    def __str__(self):
        return f'{self.user.cookie}, {self.question.question}'

# Checks the given cell/string for a variant question, choosing randomly
                # Only occurs if there is an option built into the question
                # For right now, this is a copy paste until I can confirm
                #   it works.
def check_for_variant(cell, index, regex):
    if cell.__contains__('{'):

        question_choice = re.search(regex, cell) 
        question_choice_string = question_choice.group(1)
        question_choice_split = question_choice_string.split('/')

        random_variant = None
        if index is None:
            random_variant = random.choice(question_choice_split)
            index = question_choice_split.index(random_variant)
        else:
            random_variant = question_choice_split[index]
        cell = cell.replace(question_choice_string, random_variant)
        cell = cell.replace('{', '')
        cell = cell.replace('}', '')
    return cell, index   

# Reads through the entire CSV and pulls valid questions
def read_file():
    with open('Questions_1.csv', newline = '') as csv_file:
        # Open csv and split into nested arrays
        csv_reader = csv.reader(csv_file, delimiter=',', quotechar='|')
        first_row = next(csv_reader) # Need to check separately

        answer_index = None
        random_index = None # Used to detect changes in questions with variants

        # Get all the option columns and the answer index
        index = 0
        for cell in first_row:
            if cell.__contains__('Option'):
                options.append(index)
            elif cell.__contains__('Correct Answer'):
                answer_index = index
            index += 1

        for row in csv_reader: # Check each row in split CSV file
            try:
                # Skips current row from being added to questions
                if row[0] == '':
                    continue

                # Checks where difficulty begins
                if row[0].__contains__('Assigned Difficulty:'):
                    difficulty_markers.append(len(questions))
                    continue
                
                # Checking question
                row[0], random_index = check_for_variant(row[0], random_index,
                    r"\{([A-Za-z0-9_\/]+)\}") 
                if random_index is not None: 
                    # If question changed, answer needs to change too
                    row[answer_index], random_index = check_for_variant(
                        row[answer_index], random_index, r"\{([A-Za-z0-9_\.\;\(\)\/]+)\}")
                    random_index = None

                # Gets options from option columns for given question
                answer_options = []
                for index in options:
                    if row[index] != '':
                        answer_options.append(row[index])
                
                # Append question to list
                questions.append(Question(row[0], row[answer_index],
                                          answer_options))

            except IndexError:
                print('List Complete')

# Chooses a random question in the provided range
def get_question(min, max):
    return questions[random.choice(range(min, max))]

def choose_question(score):
    # Question chosen through ranomization within point thresholds
    chosen_question = None

    if score >= difficulty_markers[0] and score < difficulty_markers[1]:
        chosen_question = get_question(difficulty_markers[0],
                                          difficulty_markers[1])
    elif score >= difficulty_markers[1] and score < difficulty_markers[2]:
        chosen_question = get_question(difficulty_markers[1],
                                          difficulty_markers[2])
    else:
        chosen_question = get_question(difficulty_markers[2],
                                          len(questions))
    return chosen_question


def get_quiz_field_values(user):
    chosen_question = choose_question(user.score)
    
    # Get the 4 choices to present to user
    option_copy = chosen_question.options.copy()
    presented_options = []
    presented_options.append(chosen_question.answer)
    
    # Choose 3 random options
    for _ in range(3):
        index = random.choice(range(0, len(option_copy)))
        presented_options.append(option_copy[index])
        del option_copy[index]
    
    # Randomize the 3 options with the answer
    random.shuffle(presented_options)
    return chosen_question, presented_options

# Determines if correct answer given
def check_correct(question, provided_answer):
    return question.answer == provided_answer

# Eventually replace with db calls ##
def create_user(cookie):
    user = User(cookie) ##
    users.append(user) ##
    return user

# Eventually replace with db calls ##
def find_user(cookie):
    user = None
    for loop_user in users:
        if loop_user.cookie != cookie:
            continue
        user = loop_user
    if user is None:
        user = create_user(cookie)
    return user

# Finds thread associated with user
def find_current_question(user):
    for current_question in current_questions:
        print(f'{current_question.user}, {user}')
        if current_question.user != user:
            continue
        return current_question
    return None

# Removes thread
def remove_current_question(user_question):
    print('removing' + str(user_question))
    current_questions.remove(user_question)
    user_question.user.timer_thread = None

# Waits for user to send an answer
def await_answer(user_question):
    start_time = time.time()
    while True:
        if user_question.kill_thread:
            print(str(current_questions))
            remove_current_question(user_question)
            print('thread killed early')
            break

        if time.time() - start_time > 45:
            print(str(current_questions))
            print('time exceeded')
            user = user_question.user
            user.reduce_score()
            remove_current_question(user_question)
            break
    print(str(current_questions))
    print('loop broken')


# Methods to be called by client

# Displays the main home page
@app.route('/')
def home():
    return render_template('index.html')

# Send the next question to the proper user
@app.route('/send', methods=['POST'])
def send():
    print("\n")
    print(str(current_questions))
    # Find correct user in list or create user
    user = find_user(request.cookies.get('username'))

    # Get a question and possible answer list
    question, options_list = get_quiz_field_values(user)

    # Create tie between question and user
    current_question = CurrentQuestion(user, question)
    current_questions.append(current_question)

    # Start thread to determine when to auto-fail question
    user.timer_thread = threading.Thread(target=await_answer, args=[current_question])
    user.timer_thread.start()

    return json.dumps({
        'prompt': question.question,
        'ans1': options_list[0],
        'ans2': options_list[1],
        'ans3': options_list[2],
        'ans4': options_list[3]
    })

# Receive the answer provided by user
@app.route('/receive', methods=["POST"])
def receive():
    print("\n")
    print(str(request.form.get('answer-choice')))

    # Find correct user in list
    user = find_user(request.cookies.get('username'))

    # Find active question for user
    user_question = find_current_question(user)
    if user_question is None:
        print('error, user_question is none')
        return ''
    
    # Kill current thread and join to main
    user_question.kill_thread = True
    user.timer_thread.join()

    # Determine if score needs to increase or decrease
    if check_correct(user_question.question, request.form.get('answer-choice')):
        user.add_score()
    else:
        user.reduce_score()
    print('reached end of receive')
    return ''

if __name__ == '__main__':
    read_file()
    app.run(debug = False, port = 5000)