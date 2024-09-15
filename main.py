import random
import google.generativeai as genai
api_key = ""
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

def generate_bot_response(prompt):
    response = model.generate_content(prompt)
    return response.text.strip()

def calculate_counteroffer(initial_price, user_offer, counteroffer_count):
    if user_offer <= initial_price * 0.5:
        # Offer is less than 50%, reject
        return "Reject", initial_price
    elif 0.5 < user_offer < 0.75:
        # Counteroffer between 50% and 75%
        discounts = [0.75, 0.73, 0.70]  # Discounts for 1st, 2nd, 3rd counteroffer
        if counteroffer_count < len(discounts):
            discount_percentage = discounts[counteroffer_count]
        else:
            discount_percentage = 0.70  # Minimum offer discount
        new_price = max(initial_price * (1 - discount_percentage), initial_price * 0.70)
    elif 0.75 <= user_offer <= 1.0:
        # Counteroffer between 75% and 100%
        discounts = [0.95, 0.90, 0.85, 0.82, 0.80]  # Discounts for 1st to 5th counteroffer
        if counteroffer_count < len(discounts):
            discount_percentage = discounts[counteroffer_count]
        else:
            discount_percentage = 0.80  # Minimum offer discount
        new_price = max(initial_price * (1 - discount_percentage), initial_price * 0.80)
    else:
        return "Reject", initial_price  # If user offer is above 100%, no valid action
    
    return "Counteroffer", new_price

def interpret_user_response(user_response, counteroffer=False, initial_price=None, counteroffer_value=None):
    if not counteroffer:
        # Prompt 1 for non-counteroffer scenarios
        prompt = f"You are a negotiator and the initial price was ${initial_price}. The user response is '{user_response}'. Analyze if the response is to 'accept' or 'reject' the offer."
    else:
        # Prompt 2 for counteroffer scenarios
        prompt = f"The initial price was ${initial_price}. The user counteroffer was ${counteroffer_value}. The next counteroffer calculated is ${initial_price - (initial_price * (0.70 if counteroffer_count < 3 else 0.80))}. Write a convincing response to the user's counteroffer."
    
    response = generate_bot_response(prompt)
    return response

def handle_user_response(initial_price):
    max_attempts = 5
    counteroffer_count = 0

    while counteroffer_count < max_attempts:
        user_response = input(f"Bot: Do you want to accept, counteroffer, or reject the price of ${initial_price}? \nUser: ")

        # Determine if the response is an accept, reject, or counteroffer
        response_type = interpret_user_response(user_response, counteroffer=False, initial_price=initial_price)
        
        if 'accept' in response_type.lower():
            print(f"Bot: Thank you for purchasing at ${initial_price}!")
            break
        elif 'reject' in response_type.lower():
            print(f"Bot: Sorry to hear that. Could you provide a counteroffer or desired price?")
            user_response = input(f"User: ")
            response_type = interpret_user_response(user_response, counteroffer=True, initial_price=initial_price, counteroffer_value=int(''.join(filter(str.isdigit, user_response))))
        elif 'counteroffer' in response_type.lower():
            user_offer = int(''.join(filter(str.isdigit, user_response)))
            response_type, new_price = calculate_counteroffer(initial_price, user_offer, counteroffer_count)
            
            if response_type == "Reject":
                print(f"Bot: Sorry, your offer of ${user_offer} is too low. We cannot accept it.")
                break

            # Generate a response using Gemini based on the counteroffer
            prompt = f"Initial price was ${initial_price}. The user offered ${user_offer}. The counteroffer process has reached its {counteroffer_count+1} stage. The new counteroffer is ${new_price}. "
            prompt += "Generate a response that acknowledges the counteroffer and clearly communicates the next step."

            response = generate_bot_response(prompt)
            print(f"Bot: {response}")
            
            initial_price = new_price
            counteroffer_count += 1

        else:
            print("Bot: Sorry, I didn't understand that. Please respond with 'accept', 'reject', or a counteroffer price.")
    
    if counteroffer_count == max_attempts:
        print(f"Bot: We couldn't reach an agreement. The best I can offer is ${initial_price}.")

def start_chatbot():
    initial_price = 48501
    print(f"Bot: Hello! I am offering this product at ${initial_price}.")
    handle_user_response(initial_price)

if _name_ == "_main_":
    start_chatbot()
