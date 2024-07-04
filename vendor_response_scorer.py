from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_community.document_loaders import DirectoryLoader, TextLoader
import os
    
class VendorResponseScorer:
    def __init__(self, criteria, response_file_path):
        self.criteria = criteria
        self.response_file_path = response_file_path
        self.chat = ChatGroq(temperature=0, model_name="llama3-8b-8192", groq_api_key="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")
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
            3. question3: 0(answer not provided)
            Score : (8+10+0)/3 = 6
            weighted score :Average*weighted, example: 6.3*10/100 = 0.63
        End of Criteria don't print anything after this.
        the format should be like this:
        [
          Technical Competence, weightage = 20:
          1. Can you provide case studies or references?: 10
          2. What certifications does your team hold?: 9
          3. What is your experience with similar projects?: 9
          Average score: (10+9+9)/3 = 9
          Weighted score: 9*20/100 = 1.8
          Financial Stability, weightage = 20:
          1. Do you have any outstanding debts or liabilities?: 0 (no answer provided)
          2. Can you provide financial statements for the last three years?: 10
          3. What is your annual revenue?: 10
          Average score: (0+10+10)/3 = 6.7
          Weighted score: 6.7*20/100 = 1.34
          Project Management, weightage = 15:
          1. How do you handle project timelines and deadlines?: 9
          2. What project management methodology do you use?: 9
          3. Can you provide a sample project plan?: 9
          Average score: (9+9+9)/3 = 9
          Weighted score: 9*15/100 = 1.35
          Quality Assurance, weightage = 10:
          1. Can you provide examples of your QA documentation?: 8
          2. What is your quality assurance process?: 9
          3. How do you handle defects and bugs?: 0 (no answer provided)
          Average score: (8+9+0)/3 = 5.3
          Weighted score: 5.3*10/100 = 0.53
          Customer Support, weightage = 25:
          1. What customer support do you offer post-implementation?: 10
          2. What is your average response time for support requests?: 10
          3. Do you provide training for our staff?: 10
          Average score: (10+10+10)/3 = 10
          Weighted score: 10*25/100 = 2.5
          End of Criteria.
        ]
        """
        system = documents[0].page_content
        prompt = ChatPromptTemplate.from_messages([("system", system), ("human", query)])
        chain = prompt | self.chat
        result = chain.invoke({
            "criteria": self.criteria,
            "vendor_response": system
        })
        return result.content    