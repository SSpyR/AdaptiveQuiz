import csv
import random

## Read into this later
#from flask import Flask

#app=Flask(__name__)

#@app.route('/')
#def test():
#    return 'Test'


#if __name__=='__main__':
#    app.run()


## Start just the general app here
## Need to catch the error of users not typing a number for the answer
## jQuery and Flask integration is main focus now
## Setup Variants
## Start scoring to track difficulty level to start at for each user (also have to log who is using it)

class Question:
    def __init__(self, ques, ans):
        self.ques=ques
        self.ans=ans

# Pull Questions from CSV
prompts=[]

# Assign Correct Answer from CSV
answers=[]

# Pull Options for Wrong Answers from CSV
options=[]

with open('Questions.csv', newline='') as csvfile:
    lreader=csv.reader(csvfile, delimiter=',', quotechar='|')
    ansidx=None
    for row in lreader:
        try:
            print(row)
            prompts.append(row[0])

            for cell in row:
                if cell.__contains__('Answer'):
                    ansidx=row.index(cell)
                if cell.__contains__('Option'):
                    options.append(row.index(cell))
            answers.append(row[ansidx])
        except IndexError:
            print('List Complete')

# Connecting Correct Answer to Prompt
questions=[]
x=0
while x < len(prompts):
    #questions.append("Question(prompts[{}], answers[{}])".format(x, x))
    questions.append(Question(prompts[x], answers[x]))
    x+=1

# Every time you rotate to a new question, grab the random answers to use and display
def run(questions):
    #options=[2,4,6,8,10,12]
    with open('Questions.csv', newline='') as csvfile:
        lreader=csv.reader(csvfile, delimiter=',', quotechar='|')
        for question, row in zip(questions, lreader):
            try:
                if "Question" in row[0]:
                    continue
                if row[0].__contains__('{'):
                    #finish variant stuff here
                aux=options.copy()
                choices=[]
                for i in range(3): #randomizing what 3 of the 6 wrong answers to use
                    randchoice=random.choice(aux)
                    idx=aux.index(randchoice)
                    choices.append(randchoice)
                    del aux[idx]
                choices.append(14)
                promptorder=[]
                for j in range(4): #randomizing choices altogether with correct answer
                    choice=random.choice(choices)
                    idx=choices.index(choice)
                    promptorder.append(row[choice])
                    del choices[idx]
                prompt=question.ques+"\n(1) {}\n(2) {}\n(3) {}\n(4) {}\n".format(promptorder[0], promptorder[1], promptorder[2], promptorder[3])
                selection=prompt.split('\n') #deleting the question itself from selection array
                del selection[0]
                del selection[4]
                answer=input(prompt) #getting input from user for answer
                actans=selection[(int(answer)-1)] #checking against selection array
                if question.ans in actans:
                    print('Correct!')
                else:
                    print('Incorrect!')
            except IndexError:
                print('List Complete')


run(questions)

