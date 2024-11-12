import requests

def query_model(model, prompt):
    response = requests.post(
        "https://api.example.com/v1/models",
        headers={"Authorization": "Bearer api_key"},
        json={"model": model, "prompt": prompt, "max_tokens": 150}
    )
    return response.json()

# trigger_point = logic to get the trigger points to start the survey based on the available info.

overall_rating = 3.5
negative_reviews_in_last_month = 30
css = 50
detractor_score = 70

def get_trigger_points(overall_rating,negative_reviews_in_last_month,css,detractor_score):
    prompt =""
    if overall_rating < 4:
        prompt += f"the overall rating is {overall_rating} which is less than expected."
    if negative_reviews_in_last_month > 15:
        prompt += f" most of the negative reviews last month."
    if css <= 60:
        prompt += f" css score is only {css}%."
    if detractor_score >= 50:
        prompt += " more than the 50% of the customers are detractors."
    return prompt


trigger_points = get_trigger_points(overall_rating,negative_reviews_in_last_month,css,detractor_score)
business_name = "Curry pizza"
trigger_prompt = f"{business_name} having issue of {trigger_points}"
initial_question_prompt = f"""Trigger points for the business - {trigger_prompt}\n 
Based on the trigger points for the business, what should be the initial question for {business_name}?"""

model = "O1-mini"

initial_question = query_model(model,initial_question_prompt)

initial_question = "We've noticed that your overall rating is lower than expected, and many recent reviews have been negative. Could you share more about the common customer feedback or complaints you've received recently?"

# for the initial question users reply is like 

user_reply = "Yes, we've been getting feedback about long wait times and inconsistent pizza quality. Some customers are unhappy with the toppings not being fresh or the pizza being cold upon delivery. We've also had a few complaints about the customer service being slow to respond to issues. We're trying to address these concerns, but it’s been challenging to keep up with the volume of negative feedback lately."

# next question based on previous user reply
def next_question(user_previous_reply):
    next_question_prompt = """Based on the below reply of user generate the next question to proceed the further informative conversation.
    previous reply is - {user_previous_reply}
    """
    next_question = query_model(model,next_question_prompt)
    return next_question


data = {
    "css":40,
    "detractors":40,
    "negative reviews":[
                        "The food was bland and lacked seasoning. I expected much better.",
                        "Service was extremely slow, and the staff seemed uninterested in helping.",
                        "Overpriced dishes for such small portions. Definitely not worth it.",
                        "The restaurant was dirty, and the tables were sticky. Very disappointing.",
                        "I found a hair in my food, and the manager didn’t even apologize.",
                        "The atmosphere was loud and chaotic. Not a pleasant dining experience.",
                        "The steak was overcooked, tough, and had no flavor.",
                        "I waited over an hour for my order, only to receive cold food.",
                        "The menu was limited and lacked any interesting options.",
                        "I got food poisoning after eating here. Never coming back!"
                    ],
    "negative reviews last month": 10,
    "positive reviews last month":1,
    "competitor": [
                    {
                      "name": "Backstage Lounge & Bar, ",
                      "value": [
                        {
                          "attribute": "Satisfaction",
                          "reviewRating": 4.45
                        },
                        {
                          "attribute": "Service",
                          "reviewRating": 4.21
                        },
                        {
                          "attribute": "Location",
                          "reviewRating": 4.17
                        },
                        {
                          "attribute": "Price",
                          "reviewRating": 4.85
                        },
                        {
                          "attribute": "Quality",
                          "reviewRating": 4.69
                        }
                      ],
                      "status": "success"
                    },
                    {
                      "name": "The Irish House, Viman Nagar, ",
                      "value": [
                        {
                          "attribute": "Satisfaction",
                          "reviewRating": 4.19
                        },
                        {
                          "attribute": "Location",
                          "reviewRating": 3.15
                        },
                        {
                          "attribute": "Service",
                          "reviewRating": 3.1
                        },
                        {
                          "attribute": "Quality",
                          "reviewRating": 2.0
                        },
                        {
                          "attribute": "Price",
                          "reviewRating": 1.86
                        }
                      ],
                      "status": "success"
                    }
                  ],
    "business attribute rating":[
                                  {
                                    "attribute": "Satisfaction",
                                    "reviewRating": 3.35
                                  },
                                  {
                                    "attribute": "Service",
                                    "reviewRating": 3.01
                                  },
                                  {
                                    "attribute": "Location",
                                    "reviewRating": 2.87
                                  },
                                  {
                                    "attribute": "Price",
                                    "reviewRating": 2.5
                                  },
                                  {
                                    "attribute": "Quality",
                                    "reviewRating": 2.34
                                  }
                                ],
    "overall_rating decreased by": 0.59
}

def generate_prompt_for_gpt(business_data):
    prompt = "Based on the following business data, generate a question to help the business owner identify potential issues: \n\n"

    # Add business ratings summary
    prompt += "Customer Satisfaction Score (CSS): {}\n".format(business_data.get("css", "N/A"))
    prompt += "Detractors: {}\n".format(business_data.get("detractors", "N/A"))
    
    # Add review stats
    prompt += "Negative Reviews: {}\n".format(len(business_data.get("negative reviews", [])))
    prompt += "Negative Reviews Last Month: {}\n".format(business_data.get("negative reviews last month", "N/A"))
    prompt += "Positive Reviews Last Month: {}\n".format(business_data.get("positive reviews last month", "N/A"))
    
    # Add competitor data
    prompt += "Competitor Comparisons:\n"
    for competitor in business_data.get("competitor", []):
        prompt += "  - {}: Satisfaction Rating: {}, Price Rating: {}, Quality Rating: {}\n".format(
            competitor["name"].strip(),
            next((item["reviewRating"] for item in competitor["value"] if item["attribute"] == "Satisfaction"), "N/A"),
            next((item["reviewRating"] for item in competitor["value"] if item["attribute"] == "Price"), "N/A"),
            next((item["reviewRating"] for item in competitor["value"] if item["attribute"] == "Quality"), "N/A")
        )
    
    # Add business attribute ratings
    prompt += "\nBusiness Attribute Ratings compared to competitors:\n"
    for attribute in business_data.get("business attribute rating", []):
        prompt += "  - {}: {}\n".format(attribute["attribute"], attribute["reviewRating"])
    
    # Mention the overall rating drop
    prompt += "\nOverall rating decreased in last month by: {}\n".format(business_data.get("overall_rating decreased by", "N/A"))

    # Add instruction for GPT
    prompt += "\nGenerate a question that addresses any of the issues from the provided business data, addressing the business owner directly with 'your' perspective that we obeserved the issue.generate question with max token of 30."
    prompt += "if user asked for the suggestion then give the suggestions in a simple way."
    return prompt

prompt = generate_prompt_for_gpt(data)

print(prompt)

from openai import OpenAI

client = OpenAI(api_key="api_key")


def get_response(client,prompt):
    response = client.chat.completions.create(
        model="o1-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            },
        ]    
    )
    
    response = response.choices[0].message.content
    return response

initial_question = get_response(client,prompt)

print(initial_question)

def generate_follow_up_prompt(user_reply):
    prompt = f"""
Based on the user's reply: {user_reply}

The response should be simple and concise, with a maximum of 30-50 tokens. If the user asks for suggestions, provide straightforward suggestions instead of complicated questions.Generate a follow-up question that delves deeper into their response, helping them think about further actions, improvements, or clarifications regarding their business. The follow-up question should use 'your' language and encourage a thoughtful answer from the user.
"""

    return prompt


user_reply = "We're aware that our satisfaction and quality ratings are below competitors. We're addressing this by improving staff training, revising our menu, and focusing on consistent food quality to enhance the overall customer experience."
follow_up_prompt = generate_follow_up_prompt(user_reply)
get_response(client,follow_up_prompt)

user_reply = "i thought to conduct the training sessions,it this a good idea?"
follow_up_prompt = generate_follow_up_prompt(user_reply)
get_response(client,follow_up_prompt)

user_reply = "We aim to improve customer service skills, ensure consistent product knowledge, and enhance team communication. Our goal is to create a more efficient and customer-focused team."
follow_up_prompt = generate_follow_up_prompt(user_reply)
get_response(client,follow_up_prompt)

user_reply = "can you suggest something to enhance the team's communication and customer service skills"
follow_up_prompt = generate_follow_up_prompt(user_reply)
get_response(client,follow_up_prompt)

user_reply = "thanks for your suggestion. i was implemented and i see the good difference."
follow_up_prompt = generate_follow_up_prompt(user_reply)
get_response(client,follow_up_prompt)

user_reply = "i am not able to reduce the churn rate. i'm loosing my old customers..how can i get back them? any suggestion?"
follow_up_prompt = generate_follow_up_prompt(user_reply)
get_response(client,follow_up_prompt)

user_reply = "they said that the service is bad,waiting time is more and the taste of veg cuisines are not that much as of non veg cusines."
follow_up_prompt = generate_follow_up_prompt(user_reply)
get_response(client,follow_up_prompt)

user_reply = "can u suggest something to reduce the waiting time?"
follow_up_prompt = generate_follow_up_prompt(user_reply)
get_response(client,follow_up_prompt)

user_reply = "i thought about the trained chef for veg menu"
follow_up_prompt = generate_follow_up_prompt(user_reply)
get_response(client,follow_up_prompt)

user_reply = "it all about the taste .so that the trained chef’s skills enhance my restaurent's vegan menu"
follow_up_prompt = generate_follow_up_prompt(user_reply)
get_response(client,follow_up_prompt)

user_reply = "can you suggest the veg menu that is famous in India"
follow_up_prompt = generate_follow_up_prompt(user_reply)
get_response(client,follow_up_prompt)

user_reply = "i'll thought over it."
follow_up_prompt = generate_follow_up_prompt(user_reply)
get_response(client,follow_up_prompt)

user_reply = "i'll let you know if i need anything else."
follow_up_prompt = generate_follow_up_prompt(user_reply)
get_response(client,follow_up_prompt)

survey_data = [
    {
        "question":'How are you addressing your low satisfaction and service ratings compared to competitors?',
        "reply":"We're aware that our satisfaction and quality ratings are below competitors. We're addressing this by improving staff training, revising our menu, and focusing on consistent food quality to enhance the overall customer experience."
    },
    {
        "question":"What specific measures will you use to track the success of your staff training and menu changes in boosting customer satisfaction?",
        "reply":"i thought to conduct the training sessions,it this a good idea?"
    },
    {
        "question":"Yes, conducting training sessions can effectively enhance your team’s skills and performance. What specific goals do you have for your training sessions?",
        "reply":"We aim to improve customer service skills, ensure consistent product knowledge, and enhance team communication. Our goal is to create a more efficient and customer-focused team."

    },
    {
        "question":"What specific methods will you use to enhance your team's communication and customer service skills?",
        "reply":"can you suggest something to enhance the team's communication and customer service skills"

    },
    {
        "question":"**Suggestion:** Schedule regular team meetings and provide communication training. Enhance customer service by training in active listening and establishing a customer feedback system.\n\n**Follow-up Question:** How are you currently supporting your team's communication and customer service, and where do you see opportunities for further improvement?",
        "reply":"thanks for your suggestion. i was implemented and i see the good difference."

    },
    {
        "question":"I'm glad to hear that! What other areas are you looking to improve in your business?",
        "reply":"i am not able to reduce the churn rate. i'm loosing my old customers..how can i get back them? any suggestion?"

    },
    {
        "question":"I'm sorry to hear you're facing this. Consider offering loyalty rewards, personalizing communications, and seeking feedback to understand their needs.\n\nWhat feedback have you received from customers who left?",
        "reply":"they said that the service is bad,waiting time is more and the taste of veg cuisines are not that much as of non veg cusines."

    },
    {
        "question":"Thank you for sharing your feedback. Could you provide more details on how you plan to reduce waiting times and enhance the taste of your vegetarian dishes to better match your non-vegetarian offerings?",
        "reply":"can u suggest something to reduce the waiting time?"

    },
    {
        "question":"To reduce waiting time, you can:\n- Implement an appointment system\n- Optimize staff schedules\n- Streamline service processes\n- Use queue management software\n\nHow can these changes enhance your customers' experience and your business operations?",
        "reply":"i thought about the trained chef for veg menu"

    },
    {
        "question":"How will your trained chef’s skills enhance your vegan menu and attract more customers?",
        "reply":"it all about the taste .so that the trained chef’s skills enhance my restaurent's vegan menu"

    },
    {
        "question":"That's wonderful! How do you plan to leverage your chef's expertise to create unique and memorable vegan dishes for your menu?",
        "reply":"can you suggest the veg menu that is famous in India"

    },
    {
        "question":'Sure! Popular Indian vegetarian dishes include Paneer Butter Masala, Chole Bhature, Aloo Gobi, Masoor Dal, Dosa with Sambar, Palak Paneer, and Rajma. \n\nHow would you like to showcase these dishes in your menu to attract more customers?',
        "reply":"i'll think over it."

    },
    {
        "question":"That's great to hear! Which specific aspects of your business are you considering reviewing or improving next? Understanding this can help us provide more targeted support.",
        "reply":"i'll let you know if i need anything else."

    },
    {
        "question":"Absolutely, feel free to reach out anytime. Meanwhile, what are your current priorities for your business growth?",
        "reply":None
    }
]

def get_action_plan(survey_data):
    action_plan_prompt = f"""The user has responded to a series of questions about the challenges they are facing in their business. Review the conversation below, analyze the issues mentioned, and suggest a customized action plan that addresses the specific problems raised by the user. Refer to the questions and responses to identify key pain points and areas for improvement. Use your intelligence to provide practical, solution-oriented advice that improves overall business experience. Only address the issues explicitly mentioned by the user, and give concise and actionable steps to help resolve them.\n

    Refer below data obtained from survey conducted for business owner:\n
    {survey_data}
    maximum token should be 150.
    """
    return action_plan_prompt

action_plan_prompt = get_action_plan(survey_data)
action_plan = get_response(client,action_plan_prompt)
print(action_plan)