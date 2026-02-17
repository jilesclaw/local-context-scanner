# Payment Service
import json

# Task: Implement rate limiting here using the config
# and the utils.rate_limiter module.

def process_payment(user_id, amount, card_token):
    """
    Processes a payment for a user.
    """
    print(f"Processing ${amount} for {user_id}...")
    
    # Validation
    if amount <= 0:
        raise ValueError("Invalid amount")
        
    # TODO: Check rate limit!
    
    # Simulate API call
    result = {"success": True, "transaction_id": "txn_12345"}
    
    return result
