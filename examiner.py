import openai

openai.api_key = '<openai-api-key>'

def answer_question(question, options):
    options_text = "\n".join(f"{i}. {option}" for i, option in enumerate(options, start=1))
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a exam taker. User will give you a question and four options. Respond just a number, number of the correct answer"},
            {"role": "user", "content": f"{question}\n{options_text}"}
        ]
    )

    return response['choices'][0]['message']['content']

questions = [
    "What is epidemiology?",
    # Add more questions here...
]

options = [
    ["Study of diseases", "Study of health and disease conditions in populations", "Study of individual health", "Study of medicine"],
    # Add more options for each question here...
]

answers = []

for question, option in zip(questions, options):
    answer = answer_question(question, option)
    print(answer)
    answers.append(answer)

print(answers)
