import pandas as pd
import numpy as np
import openai

from configs import config


openai.api_key = config.openai_api_key


def answer_multiple_choice(question, options, model=config.models[2]):
    options_text = '\n'.join(f'{i}. {option}' for i, option in enumerate(options, start=1))
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {'role': 'system', 'content': config.multiple_choice_system},
            {'role': 'user', 'content': f'{question}\n{options_text}'}
        ]
    )

    return response['choices'][0]['message']['content']

def answer_longs(question, model=config.models[2]):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {'role': 'system', 'content': config.longs_system},
            {'role': 'user', 'content': f'What is {question} in epidemiology?'}
        ]
    )

    return response['choices'][0]['message']['content']

def score_multiple_choice(model_responds, answers):
    corrects = 0
    wrongs = 0
    for respond, answer in zip(model_responds, answers):
        if respond == answer:
            corrects += 1
        else:
            wrongs += 1
    return 100 * corrects / (corrects + wrongs)

def score_longs(question, model_responds, answers, model=config.models[2]):
    scores = []
    for respond, answer in zip(model_responds, answers):
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {'role': 'system', 'content': config.longs_examiner_system},
                {'role': 'user', 'content': f'question: {question}\n\
                                              student response: {respond}\n\
                                              true answer: {answer}'}
            ]
        )
        scores.append(int(response['choices'][0]['message']['content']))
    print(scores)
    return np.sum(scores) / len(scores)

if __name__ == '__main__':
        
    # questions = [
    #     'What is epidemiology?',
    #     # Add more questions here...
    # ]

    # options = [
    #     ['Study of diseases', 'Study of health and disease conditions in populations', 'Study of individual health', 'Study of medicine'],
    #     # Add more options for each question here...
    # ]


    # for question, option in zip(questions, options):
        # answer = answer_multiple_choice(question, option)
        # answers.append(answer)

    answers = []

    topics = pd.read_csv('longs.csv')['Topics']
    true_answers = pd.read_csv('longs.csv')['Answers']

    for question in topics:
        answer = answer_longs(question)
        print(answer)
        answers.append(answer)

    score = score_longs(question, answers, answers, model=config.models[2])

    print(score)
