import json
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_community.document_loaders import DirectoryLoader, TextLoader


def extract_criteria(data):
    # data = json.loads(json_data)['data'][0]  # Assuming there's only one item in 'data'
    result = []

    for item in data['information']['Question']:
        criteria = item['criteria']
        weightage = item['weightage']
        questions = item['questions']

        result.append(f"{criteria} : {data['Organization']['Name']}\n")
        result.append(f"weightage : {weightage} \n")

        question_list = "\n".join([f"{i+1}. {question}" for i, question in enumerate(questions.keys())])
        result.append(question_list)
        result.append("\n")

    formatted_output = "\n".join(result)
    return formatted_output

def format_vendor_response(data):
    # json_data = json.loads(event['body'])  # Access the data from event.body
    # data = data['data'][0]  # Assuming there's only one item in 'data'
    vendor_name = data['SupplierName']
    vendor_id = data['VendorID']
    criteria_data = data['information']['Question']
    additional_notes = data['additionalNotes']
    
    result = []
    result.append(f"{vendor_name}\n")
    result.append(f"{vendor_id}\n")

    for criterion in criteria_data:
        criteria_name = criterion['criteria']
        questions = criterion['questions']

        result.append(f"{criteria_name}:\n")
        result.append("\n".join([f"{i+1}. {question}: {answer}" for i, (question, answer) in enumerate(questions.items())]))
        result.append("\n")

    result.append(f"additionalNotes1: {additional_notes}\n")
    formatted_output = "\n".join(result)
    
    filename = '/tmp/vendor_response.txt'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as file:
        file.write(formatted_output)
    
    return {
        'statusCode': 200,
        'body': json.dumps({'file_path': filename})
    }

class VendorResponseScorer:
    def __init__(self, criteria, response_file_path):
        self.criteria = criteria
        self.response_file_path = response_file_path
        self.chat = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768", groq_api_key="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")

    def load_and_score_vendor_response(self):
        temp_dir = '/tmp/vendor_responses'
        os.makedirs(temp_dir, exist_ok=True)

        # Copy the uploaded file to the temporary directory
        temp_file_path = os.path.join(temp_dir, 'vendor_response.txt')
        with open(temp_file_path, 'w', encoding='utf-8') as f:
            with open(self.response_file_path, 'r', encoding='utf-8') as original_file:
                f.write(original_file.read())

        # Load the document using DirectoryLoader and TextLoader
        text_loader_kwargs = {'autodetect_encoding': True}
        loader = DirectoryLoader(temp_dir, glob="vendor_response.txt", loader_cls=TextLoader, loader_kwargs=text_loader_kwargs)
        documents = loader.load()
        # print(documents[0])

        # Define the evaluation query
        query = f"""As an evaluator, your job is to carefully evaluate and score the responses of respective Supplier on a total scale of 1 to 10 where :
         1-3: Poor
         4-6: Fair
         7-8: Good
         9-10: Excellent


        Here is a brief explanation of all the criteria:
        {self.criteria}

        Evaluate Supplier for all the parameters carefully, score them and return the average score.
        For No answer provided assume score as 0.
        for example: 
        CriteriaName(specify name of the criteria), weightage= 25: 
            
            1. question1: 10
            2. question2: 10
            3. question3: 8

            Score : (10+10+8)/3 = 9.3
            weighted score : Average*weighted, example: 9.3*25/100 = 2.325
          
        CriteriaName(name of the criteria), weightage=10: 
            
            1. question1: 8
            2. question2: 10
            3. question3: 1(answer not provided)

            Score : (8+10+1)/3 = 6.3
            weighted score :Average*weighted, example: 6.3*10/100 = 0.63
        End of Criteria don't print anything after this.

        """

        system = documents[0].page_content
        prompt = ChatPromptTemplate.from_messages([("system", system), ("human", query)])
        chain = prompt | self.chat
        result = chain.invoke({
            "criteria": self.criteria,
            "vendor_response": system
        })
        return result.content
    

# event = {
#     "body": json.dumps({
#         "data": [
#     {
#       "additionalNotes": "Please include all shipping and handling costs in the proposal.",
#       "information": {
#         "Question": [
#           {
#             "questions": {
#               "Can you provide case studies or references?": "Absolutely, we have a collection of detailed case studies and references that we can share, highlighting our success stories.",
#               "What certifications does your team hold?": "Our team members are certified in PMP, AWS Certified Solutions Architect, Certified ScrumMaster, and various other industry-recognized credentials.",
#               "What is your experience with similar projects?": "We have completed over 50 similar projects in the past 5 years, consistently meeting client expectations and industry standards."
#             },
#             "weightage": 20,
#             "criteria": "Technical Competence"
#           },
#           {
#             "questions": {
#               "Do you have any outstanding debts or liabilities?": "We maintain a strong financial position with minimal outstanding debts and no significant liabilities.",
#               "Can you provide financial statements for the last three years?": "Yes, we have audited financial statements for the past three years available for review.",
#               "What is your annual revenue?": "Our annual revenue for the most recent fiscal year was $60 million."
#             },
#             "weightage": 20,
#             "criteria": "Financial Stability"
#           },
#           {
#             "questions": {
#               "How do you handle project timelines and deadlines?": "Timelines and deadlines are managed through advanced tools like Jira and MS Project, ensuring we stay on track and meet all project milestones.",
#               "What project management methodology do you use?": "We utilize Agile methodologies as our primary approach, with flexibility to adapt to Waterfall or hybrid methods as needed.",
#               "Can you provide a sample project plan?": "Certainly, we can furnish a sample project plan to illustrate our approach and methodologies."
#             },

#             "weightage": 15,
#             "criteria": "Project Management"
#           },
#           {
#             "questions": {
#               "Can you provide examples of your QA documentation?": "Yes, we have examples of our detailed QA documentation from previous projects that we can share.",
#               "What is your quality assurance process?": "Our QA process includes thorough automated and manual testing, code reviews, and continuous integration practices to ensure high standards.",
#               "How do you handle defects and bugs?": ""
#             },
#             "weightage": 10,
#             "criteria": "Quality Assurance"
#           },
#           {
#             "questions": {
#               "What customer support do you offer post-implementation?": "We provide round-the-clock customer support via phone, email, and chat, ensuring any issues are swiftly addressed.",
#               "What is your average response time for support requests?": "Our support team typically responds to requests within an average of 1 hour, ensuring quick resolution.",
#               "Do you provide training for our staff?": "Yes, we offer extensive training programs tailored to your staff's needs to ensure smooth adoption of the new system."
#             },
#             "weightage": 25,
#             "criteria": "Customer Support"
#           }
#         ]
#       },
#       "Organization": {
#         "Entity": "VENDOR",
#         "Organization": "Beta Group",
#         "auditLog": [
#           {
#             "message": "New Vendor Was Created ",
#             "date": "2024-06-14T06:03:34.584Z"
#           }
#         ],
#         "Rate": 4.7,
#         "Total_Business": 2500000,
#         "Service": [
#           "Financial Advisory",
#           "Risk Management"
#         ],
#         "Segment": "SMB",
#         "Contact": {
#           "Phone": "+1-415-555-0198",
#           "Email": "info@betaenterprises.com"
#         },
#         "Name": "Beta Enterprises",
#         "Industry": "Finance",
#         "SK": "VENDOR#Beta Enterprises",
#         "PK": "VENDOR#d55f6a00-2a13-11ef-8790-5f857d34170f",
#         "Location": "San Francisco, USA"
#       },
#       "status": "Active",
#       "SK": "RFXRES#5832bca0-2fde-11ef-82c7-41df899d07ce",
#       "attachments": [
#         "terms.pdf",
#         "requirements.docx"
#       ],
#       "PK": "RFX#af7fd4a0-2fae-11ef-bad8-4393f2371061",
#       "SupplierName": "Beta Group",
#       "VendorID": "VENDOR#d55f6a00-2a13-11ef-8790-5f857d34170f",
#       "Entity": "RFX_RESPONSE"
#     }
#   ]
#     })
# }
import re
def lambda_handler(event, context):
    try:
        json_data = json.loads(event['body'])
        data = json_data['data'][0]

        # Extract criteria and format vendor response
        formatted_criteria = extract_criteria(data)
        formatted_vendor_response = format_vendor_response(data)
        scorer = VendorResponseScorer(formatted_criteria, json.loads(formatted_vendor_response['body'])['file_path'])
        score = scorer.load_and_score_vendor_response()
        # print(json.dumps(score))
        match = re.search(r'Total weighted score: (\d+\.\d+)', score)
        if match:
          total_weighted_score = match.group(1)
        # print(f"Total weighted score: {total_weighted_score}")
          average_scores_pattern = re.compile(r'Average scores:\s*- [A-Za-z ]+: ([\d.]+)\s*- [A-Za-z ]+: ([\d.]+)\s*- [A-Za-z ]+: ([\d.]+)\s*- [A-Za-z ]+: ([\d.]+)\s*- [A-Za-z ]+: ([\d.]+)')

        # Find the match in the string
        match = average_scores_pattern.search(score)
    
        if match:
        # Extract the average scores from the match groups
          average_scores = [float(match.group(i)) for i in range(1, 6)]

        # Calculate the sum of the average scores
        total_average_score = sum(average_scores)
        # print(total_average_score)
        # print(score)
        return {
            'Total_percentage': float(total_weighted_score)*10,
            'Total_Weighted_Score': float(total_weighted_score),
            'Total_Average_Score': total_average_score
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }
# Define the event object with sample data


# Call the lambda_handler function with the event object
# lambda_handler(event, None)