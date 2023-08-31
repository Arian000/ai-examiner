import pandas as pd
import numpy as np
import openai

from configs import config


openai.api_key = config.openai_api_key


def answer_multiple_choice(question, options, system_prompt, model=config.models[0]):
    options_text = '\n'.join(f'{i}. {option}' for i, option in enumerate(options, start=1))
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f'{question}\n{options_text}'}
        ],
        temperature=0.0
    )

    return response['choices'][0]['message']['content']

def define_terms(question, system_prompt, model=config.models[0]):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f'What is {question} in epidemiology?'}
        ],
        temperature=0.0
    )

    return response['choices'][0]['message']['content']

def answer_longs(question, system_prompt, model=config.models[0]):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f'{question}'}
        ],
        temperature=0.0
    )

    return response['choices'][0]['message']['content']

def score_multiple_choice(model_responds, answers, verbose=True):
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
        elif verbose: print(c, res, answer)
            # print(respond)

        
        if res == answer:
            corrects += 1
        else:
            wrongs += 1
    return 100 * corrects / (corrects + wrongs)

def score_terms(questions, model_responds, answers, model=config.models[0], verbose=False):
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
        if verbose: print(score)
        scores.append(int(score))
    return scores

def score_longs(questions, model_responds, answers, model=config.models[0], verbose=True):
    scores = []
    for q, r, a in zip(questions, model_responds, answers):
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {'role': 'system', 'content': config.longs_examiner_system},
                {'role': 'user', 'content': f'question: "{q}"\n\
                                              student response: "{r}"\n\
                                              true answer: "{a}"'}
            ],
            temperature=0.0
        )
        score = response['choices'][0]['message']['content']
        if verbose: print(score)
        scores.append(int(score))
    return scores


def do_MCTest(
        system_prompt,
        questions_file='./Questions/MultipleChoiceA.csv',
        response_file='./AIResponses/MultipleChoiceT0.csv',
        verbose=False
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
                response = answer_multiple_choice(q, list(c[1]), system_prompt, model)
            except:
                response = answer_multiple_choice(q, list(c[1]), system_prompt, model)
            if verbose: print(response)
            responses.append(response)

        results[model] = responses

    df = pd.DataFrame(results)
    df.to_csv(response_file, index=False)
    results = pd.read_csv(response_file)

    for model in models:
        score = score_multiple_choice(results[model], answers)
        if verbose: print(model, score)

def do_TerminologyTest(
        system_prompt,
        questions_file='./Questions/epidemiology_terminology.csv',
        response_file='./AIResponses/TerminologyTestT0.csv',
        verbose=False
        ):

    terminology = pd.read_csv(questions_file)
    questions = terminology['Q']

    models = config.models

    results = {}

    for model in models:
        answers = []
        for q in questions:
            try:
                answer = define_terms(q, system_prompt, model)
            except:
                answer = define_terms(q, system_prompt, model)

            if verbose: print(answer)
            answers.append(answer)

        results[model] = answers

    df = pd.DataFrame(results)
    df.to_csv(response_file, index=False)
    return df

def do_longs(
        system_prompt,
        questions_file='./Questions/Longs.csv',
        response_file='./AIResponses/LongsTestT0.csv',
        verbose=False
        ):

    longs = pd.read_csv(questions_file)
    questions = longs['Q']

    models = config.models

    results = {}

    for model in models:
        answers = []
        for q in questions:
            try:
                answer = answer_longs(q, system_prompt, model)
            except:
                answer = answer_longs(q, system_prompt, model)

            if verbose: print(answer)
            answers.append(answer)

        results[model] = answers

    df = pd.DataFrame(results)
    df.to_csv(response_file, index=False)
    return df


def score_terminology_test(
        questions_file='./Questions/epidemiology_terminology.csv',
        response_file='./AIResponses/terminology_test_r0.csv',
        scores_file='./Scores/terminology_scores_r0.csv',
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

def score_longs_test(
        questions_file='./Book1.csv',
        response_file='./AIResponses/longs_r0.csv',
        scores_file='./Scores/longs_r0.csv',
        ):

    terminology = pd.read_csv(questions_file)
    questions = terminology['Q']
    answers = terminology['A']

    responses = pd.read_csv(response_file)

    df = pd.DataFrame()
    df['questions'] = questions
    scores = {}
    for model in responses:
        scores[model] = score_longs(questions, responses[model], answers)
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


    for level in range(2, 3):
        tag = f'_r{level}'
        system_prompt = config.reported_system_prompts['terms'][level]
        response_filename = f'./AIResponses/terminology{tag}.csv'
        score_filename = f'./Scores/terminology{tag}.csv'
        do_TerminologyTest(system_prompt, response_file=response_filename, verbose=True)
        score_terminology_test(response_file=response_filename, scores_file=score_filename)

        # system_prompt = config.reported_system_prompts['multiple_choice'][level]
        # response_filename = f'./AIResponses/multiple_choice{tag}.csv.csv'
        # do_MCTest(system_prompt, response_file=response_filename, verbose=True)
        # score_MCTest(response_file=response_filename)

        # system_prompt = config.reported_system_prompts['longs'][level]
        # response_filename = f'./AIResponses/longs{tag}.csv.csv'
        # score_filename = f'./Scores/longs{tag}.csv'
        # do_longs(system_prompt, response_file=response_filename, verbose=True)
        # score_longs_test(response_file=response_filename, scores_file=score_filename)
