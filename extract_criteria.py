import json


def extract_criteria(json_data):
    data = json.loads(json_data)['data'][0]  # Assuming there's only one item in 'data'
    result = []

    for item in data['information']['Question']:
        criteria = item['criteria']
        weightage = item['weightage']
        questions = item['questions']

        result.append(f"{criteria}")
        result.append(f"weightage : {weightage} \n" ) #: {data['Organization']['Rate']}\n")

        question_list = "\n".join([f"{i+1}. {question}" for i, question in enumerate(questions.keys())])
        result.append(question_list)
        result.append("\n")

    formatted_output = "\n".join(result)
    # print("Criteria : ", formatted_output)
    return formatted_output