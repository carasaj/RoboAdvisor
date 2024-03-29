### Required Libraries ###
from datetime import datetime
from dateutil.relativedelta import relativedelta

### Functionality Helper Functions ###
def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")


def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }


### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response


"""

Create an Amazon Lambda function that will validate the data provided by the user on the Robo Advisor.

1. Start by creating a new Lambda function from scratch and name it `recommendPortfolio`. Select Python 3.7 as runtime.

2. In the Lambda function code editor, continue by deleting the AWS generated default lines of code, then paste in the starter code provided in `lambda_function.py`.

3. Complete the `recommend_portfolio()` function by adding these validation rules:

    * The `age` should be greater than zero and less than 65.
    * The `investment_amount` should be equal to or greater than 5000.

4. Once the intent is fulfilled, the bot should respond with an investment recommendation based on the selected risk level as follows:

    * **none:** "100% bonds (AGG), 0% equities (SPY)"
    * **low:** "60% bonds (AGG), 40% equities (SPY)"
    * **medium:** "40% bonds (AGG), 60% equities (SPY)"
    * **high:** "20% bonds (AGG), 80% equities (SPY)"

5. Test it using the sample test events provided for this Challenge.

6. Open the Amazon Lex Console and navigate to the `recommendPortfolio` bot configuration, integrate the new Lambda function by selecting it in the “Lambda initialization and validation” and “Fulfillment” sections.

7. Test it with valid and invalid data for the slots.

"""


def validate_data(age, investment_amount, intent_request):
    """
    Validates the data provided by the user.
    """

    # Validate that the user is over 21 years old
    if age is not None:
        if int(age) < 21 or int(age) > 65:
            return build_validation_result(
                False,
                "age",
                "You should be between the ages of 21 and 65 to use this service  "
                "please provide an age.",
            )

    # Validate the investment amount, it should be > 0
    if investment_amount is not None:
        investment_amount = int(investment_amount)  # Since parameters are strings it's important to cast values
        if investment_amount <= 5000:
            return build_validation_result(
                False,
                "investment_amount",
                "The amount to invest should be greater than 5000, "
                "please provide a correct amount to invest.",
            )
#    if risk_level is not None:
 #       while risk_level not in ['None', 'Very Low', 'Low', 'Medium', 'High']:
  #          return build_validation_result(
   #             False,
    #            "risk_level",
     #           "The amount risk level should be None, Very Low, Low, Medium, or High; "
      #          "please provide a correct amount to invest."
       #     )
    # A True results is returned if age or amount are valid
    return build_validation_result(True, None, None)

### Intents Handlers ###
def recommend_portfolio(intent_request):
    """
    Performs dialog management and fulfillment for recommending a portfolio.
    """

    first_name = get_slots(intent_request)["firstName"]
    age = get_slots(intent_request)["age"]
    investment_amount = get_slots(intent_request)["investmentAmount"]
    risk_level = get_slots(intent_request)["riskLevel"]
    source = intent_request["invocationSource"]

    if source == "DialogCodeHook":
        # This code performs basic validation on the supplied input slots.

        # Gets all the slots
        slots = get_slots(intent_request)

        validation_result = validate_data(age, investment_amount, intent_request)

        if not validation_result["isValid"]:
            slots[validation_result["violatedSlot"]] = None  # Cleans invalid slot

            # Returns an elicitSlot dialog to request new data for the invalid slot
            return elicit_slot(
                intent_request["sessionAttributes"],
                intent_request["currentIntent"]["name"],
                slots,
                validation_result["violatedSlot"],
                validation_result["message"],
            )
            # Fetch current session attributes
        output_session_attributes = intent_request["sessionAttributes"]
         # Once all slots are valid, a delegate dialog is returned to Lex to choose the next course of action.
        return delegate(output_session_attributes, get_slots(intent_request))


    if risk_level == None:
        investment_suggestion = ""
    if risk_level == "none":
        investment_suggestion = "100% bonds (AGG), 0% equities (SPY)"
    elif risk_level == "low":
        investment_suggestion = "60% bonds (AGG), 40% equities (SPY)"
    elif risk_level == "medium":
        investment_suggestion = "40% bonds (AGG), 60% equities (SPY)"
    elif risk_level == "high":
        investment_suggestion = "20% bonds (AGG), 80% equities (SPY)"

    # Return a message with conversion's result.
    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": """Thanks for using this service, {}. In your circumstances, the recommendation would be this investment portfolio {}.
            """.format(
                first_name, investment_suggestion),
        },
    )


### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "recommendPortfolio":
        return recommend_portfolio(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")


### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)

