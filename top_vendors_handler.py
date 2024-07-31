import json
import requests
import top_vendors
import math
def cors_setting(body, status):
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
        # Load the request body

        body = json.loads(event['body'])
        # print(body)

        # URL to fetch JSON data
        url = "https://cldxpildma.execute-api.ap-south-1.amazonaws.com/dev/vendors?limit=999999999"
        # print("Request body:", body)

        # Fetch JSON data from the URL
        response = requests.get(url)
        response.raise_for_status()  # Ensure we notice bad responses

        # Convert the response text to JSON
        json_data = response.json()  # This returns a Python dictionary

        # Prepare data
        df_from_json = top_vendors.load_and_prepare_data(json_data)

        # Get industry, location, and top_n from event
        industry = body.get('industry')
        location = body.get('location')
        top_n = body.get('top_n', 5)
        # print('Industry:', industry)
        # Validate required parameters
        if not industry:
            return cors_setting({
                'error': 'Industry and location are required parameters'
            }, 400)

        # Recommend top vendors
        recommended_vendors = top_vendors.recommend_vendors(industry,df_from_json, top_n=top_n)
        # print("Recommended vendors: ",recommended_vendors)
        # Convert to JSON with orient='records'
        recommended_vendors_list = recommended_vendors.to_dict(orient='records')
        # print(recommended_vendors_list)

        if location:
            recommended_vendors_list = [vendor for vendor in recommended_vendors_list if location.lower() in vendor['Location'].lower()]
        # Return JSON response
        for vendor in recommended_vendors_list:
            email = vendor.get('email') or vendor.get('Email')
            if 'email' not in vendor or not vendor['email'] or (isinstance(vendor['email'], float) and math.isnan(vendor['email'])):
                vendor['email'] = 'dummy@example.com'
            else:
                 vendor['email'] = email    

        if not recommended_vendors_list:
            return cors_setting({'message': 'No recommended vendors found for the given parameters'}, 404)

        return cors_setting(recommended_vendors_list, 200)

    except json.JSONDecodeError as e:
        print("JSON decode error:", str(e))
        return cors_setting({
            'error': 'Invalid JSON input'
        }, 400)

    except requests.RequestException as e:
        print("Request error:", str(e))
        return cors_setting({
            'error': 'Error fetching data from URL'
        }, 500)

    except Exception as e:
        print("An unexpected error occurred:", str(e))
        return cors_setting({
            'error': 'Internal Server Error'
        }, 500)

# if __name__ == "__main__":
#     # Example event JSON for local testing
#     event = {
#         "body": json.dumps({
#             "industry": "Building & Construction",
#             # "location": "Sydney",
#             "top_n": 5
#         })
#     }
#     context = {}  # Dummy context for local testing
#     result = lambda_handler(event, context)
#     print(result)
