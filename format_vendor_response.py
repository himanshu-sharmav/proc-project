import os
import json


def format_vendor_response(json_data):
    # print(type(json_data))
    data = json.loads(json_data)['data'][0]  # Assuming there's only one item in 'data'
    vendor_name = data['SupplierName']
    vendor_id = data['VendorID']
    criteria_data = data['information']['Question']
    additional_notes = data['additionalNotes']

    result = []
    result.append(f"{vendor_name}\n")
    result.append(f"{vendor_id}\n")

    for idx, criterion in enumerate(criteria_data, 1):
        criteria_name = criterion['criteria']
        questions = criterion['questions']

        result.append(f"criteria{idx}:\n")
        for i, (question, answer) in enumerate(questions.items(), 1):
            if not answer:
                answer = "No answer provided"
            result.append(f"{i}. {question}: {answer}")
        result.append(f"additionalNotes{idx} : {additional_notes}\n\n")

    formatted_output = "\n".join(result)
    filename = '/tmp/vendor_response.txt'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as file:
        file.write(formatted_output)
    return filename