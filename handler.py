import json
import re
from extract_criteria import extract_criteria
from format_vendor_response import format_vendor_response
from vendor_response_scorer import VendorResponseScorer

def cors_setting(body,status):
    response = {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Content-Type": "application/json",
        },
        "body": json.dumps(body)
    }
    return response

def lambda_handler(event, context):
    try:
        event_body = json.loads(event['body'])

        # Parse the inner body containing the data list
        data_list = event_body['body']
       
        formatted_criteria = extract_criteria(json.dumps(data_list))
        formatted_vendor_response = format_vendor_response(json.dumps(data_list))
        scorer = VendorResponseScorer(formatted_criteria, formatted_vendor_response)
        score = scorer.load_and_score_vendor_response()
        
        criteria_pattern = re.compile(r'(\w+ \w+), weightage = (\d+):')
        question_pattern = re.compile(r'\d+\. [^?]+\?: (\d+)?')
        # Extracting the data
        criteria_matches = criteria_pattern.findall(score)
        questions_matches = question_pattern.findall(score)
        # Initialize result storage
        results = []
        # Process each criteria
        start = 0
        for criteria, weightage in criteria_matches:
            weightage = int(weightage)
            scores = questions_matches[start:start+3]
            scores = [int(score) if score else 0 for score in scores]  # Assign 0 if no score
            average_score = sum(scores) / len(scores)
            weighted_score = average_score * (weightage / 100)
            results.append((criteria, average_score, weighted_score))
            start += 3
        # Output the results
        averagee_score = []
        weightedd_score = []
        for criteria, average_score, weighted_score in results:
            
            averagee_score.append(average_score)
            weightedd_score.append(weighted_score)
        
        total_weighted_score = sum(weightedd_score)
        total_average_score = sum(averagee_score)/len(averagee_score)
        
        return cors_setting({
                    'Total_percentage': round(total_weighted_score * 10,2),
                'Total_Weighted_Score': round(total_weighted_score,2),
                'Total_Average_Score': round(total_average_score,2)
            }, 200)
      
    except Exception as e:
        return cors_setting({
        
            'body': str(e)
        }, 500)

