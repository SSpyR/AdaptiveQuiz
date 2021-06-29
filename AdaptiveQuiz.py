import csv
import random
import re

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
    randidx=None
    for row in lreader:
        try:
            if row[0].__contains__('{'):
                    #fishing for variant questions
                    questionChoice=re.search(r"\{([A-Za-z0-9_\/]+)\}",row[0])
                    questionChoiceString=questionChoice.group(1)
                    questionChoiceSplit=questionChoiceString.split('/')
                    randVariant=random.choice(questionChoiceSplit)
                    randidx=questionChoiceSplit.index(randVariant)
                    row[0]=row[0].replace(questionChoiceString, randVariant)
                    row[0]=row[0].replace('{','')
                    row[0]=row[0].replace('}','')
            prompts.append(row[0])

            for cell in row:
                if cell.__contains__('Answer'):
                    ansidx=row.index(cell)
                if cell.__contains__('Option'):
                    options.append(row.index(cell))

            if row[ansidx].__contains__('{'):
                    #fishing for the variant answer based on what variant question was chosen
                    answerChoice=re.search(r"\{([A-Za-z0-9_\.\;\(\)\/]+)\}",row[ansidx])
                    answerChoiceString=answerChoice.group(1)
                    answerChoiceSplit=answerChoiceString.split('/')
                    answerChoiceFinal=answerChoiceSplit[randidx]
                    row[ansidx]=row[ansidx].replace(answerChoiceString, answerChoiceFinal)
                    print(row[ansidx])
                    row[ansidx]=row[ansidx].replace('{','')
                    row[ansidx]=row[ansidx].replace('}','')
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
    with open('Questions.csv', newline='') as csvfile:
        lreader=csv.reader(csvfile, delimiter=',', quotechar='|')
        for question, row in zip(questions, lreader):
            try:
                if "Question" in row[0]:
                    continue
                aux=options.copy()
                choices=[]
                for i in range(3): #randomizing what 3 of the 6 wrong answers to use
                    randchoice=random.choice(aux)
                    idx=aux.index(randchoice)
                    choices.append(row[randchoice])
                    del aux[idx]
                choices.append(question.ans)
                promptorder=[]
                for j in range(4): #randomizing choices altogether with correct answer
                    choice=random.choice(choices)
                    idx=choices.index(choice)
                    promptorder.append(choice)
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

