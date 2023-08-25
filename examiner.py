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

    c = 0
    for respond, answer in zip(model_responds, answers):
        c += 1
        res = respond[-1]
        if res == '.': res = respond[-2]
        if res == '1':
            res = 'a'
        elif res == '2':
            res = 'b'
        elif res == '3':
            res = 'c'
        elif res == '4':
            res = 'd'
        else:
            print(c, res, answer)
            # print(respond)

        
        if res == answer:
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
        score = response['choices'][0]['message']['content']
        print(score)
        scores.append(int(score))
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
        questions_file='./Questions/MultipleChoiceA.csv',
        response_file='./AIResponses/MultipleChoiceT0.csv',
        ):

    mc = pd.read_csv(questions_file)
    questions = mc['Q']
    choices = mc[['A', 'B', 'C', 'D']]
    answers = mc['Answer']

    models = config.models

    results = {}

    for model in models:
        responses = []
        for q, c in zip(questions, choices.iterrows()):
            try:
                response = answer_multiple_choice(q, list(c[1]), model)
            except:
                response = answer_multiple_choice(q, list(c[1]), model)
            print(response)
            responses.append(response)

        results[model] = responses

    df = pd.DataFrame(results)
    df.to_csv(response_file, index=False)
    results = pd.read_csv(response_file)

    for model in models:
        score = score_multiple_choice(results[model], answers)
        print(model, score)

def do_TerminologyTest(
        questions_file='./Questions/epidemiology_terminology.csv',
        response_file='./AIResponses/TerminologyTestT0.csv',
        ):

    terminology = pd.read_csv(questions_file)
    questions = terminology['Q']

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

def do_longs(
        questions_file='./Questions/Longs.csv',
        response_file='./AIResponses/LongsTestT0.csv',
        ):

    longs = pd.read_csv(questions_file)
    questions = longs['Q']

    models = config.models

    results = {}

    for model in models:
        answers = []
        for q in questions:
            try:
                answer = answer_longs(q, model)
            except:
                answer = answer_longs(q, model)

            print(answer)
            answers.append(answer)

        results[model] = answers

    df = pd.DataFrame(results)
    df.to_csv(response_file, index=False)
    return df


def score_terminology_test(
        questions_file='./Questions/epidemiology_terminology.csv',
        response_file='./AIResponses/TerminologyTestT0.csv',
        scores_file='./Scores/TerminologyScoresT0.csv',
        ):

    terminology = pd.read_csv(questions_file)
    questions = terminology['Q']
    answers = terminology['A']

    responses = pd.read_csv(response_file)

    df = pd.DataFrame()
    df['questions'] = questions
    scores = {}
    for model in responses:
        scores[model] = score_terms(questions, responses[model], answers)
        df[f'score_{model}'] = scores[model]
        print(np.sum(scores[model]), np.sum(scores[model]) / (len(scores[model]) * 10))

    df.to_csv(scores_file, index=False)

def score_MCTest(
        questions_file='./Questions/MultipleChoiceA.csv',
        response_file='./AIResponses/MultipleChoiceT0.csv',
        ):

    mc = pd.read_csv(questions_file)
    answers = mc['Answer']
    models = config.models
    results = pd.read_csv(response_file)

    for model in models:
        score = score_multiple_choice(results[model], answers)
        print(model, score)

if __name__ == '__main__':

    # tag = '_T0_PE12'
    # response_filename = f'./AIResponses/terminology{tag}.csv'
    # score_filename = f'./Scores/terminology{tag}.csv'
    # do_TerminologyTest(response_file=response_filename)
    # score_terminology_test(response_file=response_filename, scores_file=score_filename)

    # tag = '_T0_PE8'
    # response_filename = f'./AIResponses/multiple_choice{tag}.csv.csv'
    # score_filename = f'./Scores/multiple_choice{tag}.csv'
    # do_MCTest(response_file=response_filename)
    # score_MCTest(response_file=response_filename)

    tag = '_T0_PE2'
    response_filename = f'./AIResponses/Longs{tag}.csv.csv'
    # score_filename = f'./Scores/Longs{tag}.csv'
    do_longs(response_file=response_filename)
