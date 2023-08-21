import pandas as pd
import numpy as np
import openai

from configs import config


openai.api_key = config.openai_api_key


def answer_multiple_choice(question, options, model=config.models[0]):
    options_text = '\n'.join(f'{i}. {option}' for i, option in enumerate(options, start=1))
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {'role': 'system', 'content': config.multiple_choice_system},
            {'role': 'user', 'content': f'{question}\n{options_text}'}
        ],
        temperature=0.0
    )

    return response['choices'][0]['message']['content']

def define_terms(question, model=config.models[0]):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {'role': 'system', 'content': config.longs_system},
            {'role': 'user', 'content': f'What is {question} in epidemiology?'}
        ],
        temperature=0.0
    )

    return response['choices'][0]['message']['content']

def answer_longs(question, model=config.models[0]):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {'role': 'system', 'content': config.longs_system},
            {'role': 'user', 'content': f'{question}'}
        ],
        temperature=0.0
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

def score_terms(questions, model_responds, answers, model=config.models[0]):
    scores = []
    for q, r, a in zip(questions, model_responds, answers):
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {'role': 'system', 'content': config.longs_examiner_system},
                {'role': 'user', 'content': f'question: "What is {q} in epidemiology?"\n\
                                              student response: "{r}"\n\
                                              true answer: "{a}"'}
            ],
            temperature=0.0
        )
        scores.append(int(response['choices'][0]['message']['content']))
    return scores

def score_longs(questions, model_responds, answers, model=config.models[0]):
    scores = []
    for question, respond, answer in zip((questions, model_responds, answers)):
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {'role': 'system', 'content': config.longs_examiner_system},
                {'role': 'user', 'content': f'question: "{question}"\n\
                                              student response: "{respond}"\n\
                                              true answer: "{answer}"'}
            ]
        )
        scores.append(int(response['choices'][0]['message']['content']))
    print(scores)
    return np.sum(scores) / len(scores)


def do_MCTest(
        questions_file='./Questions/MultipleChoice.csv',
        response_file='./AIResponses/MultipleChoiceT0.csv',
        ):

    mc = pd.read_csv(questions_file)
    questions = mc['Q']
    choices = mc[['A', 'B', 'C', 'D']]

    models = config.models

    results = {}

    for model in models:
        answers = []
        for q, c in zip(questions, choices.iterrows()):
            try:
                answer = answer_multiple_choice(q, list(c[1]), model)
            except:
                answer = answer_multiple_choice(q, list(c[1]), model)
            print(answer)
            answers.append(answer)

        results[model] = answers

    df = pd.DataFrame(results)
    df.to_csv(response_file, index=False)

def do_TerminologyTest(
        questions_file='./Questions/epidemiology_terminology.csv',
        response_file='./AIResponses/TerminologyTestT0.csv',
        ):

    terminology = pd.read_csv(questions_file)
    questions = terminology['Q']
    # ground_truth = terminology['A']

    models = config.models

    results = {}

    for model in models:
        answers = []
        for q in questions:
            try:
                answer = define_terms(q, model)
            except:
                answer = define_terms(q, model)

            print(answer)
            answers.append(answer)

        results[model] = answers

    df = pd.DataFrame(results)
    df.to_csv(response_file, index=False)
    return df


def score_terminology_test(
        questions_file='./Questions/epidemiology_terminology.csv',
        responses_file='./AIResponses/TerminologyTestT0.csv',
        scores_file='./Scores/TerminologyScoresT0.csv',
        ):
    
    terminology = pd.read_csv(questions_file)
    questions = terminology['Q']
    answers = terminology['A']
    
    responses = pd.read_csv(responses_file)

    df = pd.DataFrame()
    df['questions'] = questions
    scores = {}
    for model in responses:
        scores[model] = score_terms(questions, responses[model], answers)
        df[f'score_{model}'] = scores[model]
        print(np.sum(scores[model]))

    df.to_csv(scores_file, index=False)

if __name__ == '__main__':

    do_MCTest()
    # do_TerminologyTest()
    score_terminology_test()
