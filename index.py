# import stripe
# stripe.api_key = "sk_test_51O5w34DBYJ1xxvlEX89NGZXPtZTR7z2xyADaWhIB5I7Zcmq9HzkCNz2NHF2l0sSiDdV1cEJKmV4cUAAoNHSY1Gv000TEEvbR6c"

# a=stripe.Account.create(
#   type="custom",
#   country="US",
#   email="jenny.rosen@example.com",
#   capabilities={
#     "card_payments": {"requested": True},
#     "transfers": {"requested": True},
#   },
# ) 

# print(a['id'])


# import stripe

# # Set your Stripe API key
# stripe.api_key = 'sk_test_51O5w34DBYJ1xxvlEX89NGZXPtZTR7z2xyADaWhIB5I7Zcmq9HzkCNz2NHF2l0sSiDdV1cEJKmV4cUAAoNHSY1Gv000TEEvbR6c'

# # Redirect URI where the user will be redirected after completing the onboarding
# redirect_uri = 'https://yourwebsite.com/connect/callback'

# # Create an Express account link
# account_link = stripe.AccountLink.create(
#     account='acct_1OFZjfD3rf231k0r',  # Replace with your connected account ID
#     refresh_url=redirect_uri,
#     return_url=redirect_uri,
#     type='account_onboarding',
# )

# print(f"Express Account Link URL: {account_link.url}")

# Redirect URI where the user will be redirected after completing the onboarding
# redirect_uri = 'https://yourwebsite.com/connect/callback'

# # Create a Standard account link
# account_link = stripe.AccountLink.create(
#     account='acct_1OFZjfD3rf231k0r',  # Replace with your connected account ID
#     refresh_url=redirect_uri,
#     return_url=redirect_uri,
#     type='account_onboarding',
# )

# print(f"Standard Account Link URL: {account_link.url}")

import stripe
from stripe.error import StripeError

stripe.api_key = 'sk_test_51O5w34DBYJ1xxvlEX89NGZXPtZTR7z2xyADaWhIB5I7Zcmq9HzkCNz2NHF2l0sSiDdV1cEJKmV4cUAAoNHSY1Gv000TEEvbR6c'
account_id='acct_1OFvpvDA7bmXIfLx'


# external_account=stripe.Account.create_external_account(
# account_id,
#     external_account={
#         'object': 'bank_account',
#         'country': 'NG',
#         'currency': 'usd',
#         'account_number': '1111111112',
#         'account_holder_name': 'Testing',
#         'account_holder_type': 'individual', 
#         'swift': 'AAAANGLAXXX',
#     }
# )

# def create_payouts(bank_id, amount):
#     try:
#         value = stripe.Payout.create(
#             amount=int(amount * 100),
#             currency='ngn',
#             method='standard',
#             destination=bank_id,
#             stripe_account='acct_1OFvpvDA7bmXIfLx'
#         )
#         return value
#     except StripeError as e:
#         return e.error.message
#     except Exception as e:
#         return str(e)

# # Example usage:
# bank_id = 'ba_1OHL1VDA7bmXIfLxgzerr8jQ'  # Replace with the actual external account ID
# amount = 1000  # Replace with the desired payout amount

# result = create_payouts(bank_id, amount)
# print(result)




# def get_account_balance(account_id):
#     try:
#         balance = stripe.Balance.retrieve(stripe_account=account_id)
#         return balance

#     except stripe.error.StripeError as e:
#         # Handle the error as needed
#         print(f"Stripe Error: {e}")
#         return None
    
# account_id = 'acct_1OFvpvDA7bmXIfLx'  # Replace with the actual Connect account ID
# balance = get_account_balance(account_id)
# print(balance)
# print(balance.available[0].amount)
# print(balance.pending[0].amount)




# transfer = stripe.Transfer.create(
#         amount=1,  # Replace with the amount in cents that you want to transfer
#         currency='usd',  # Replace with the desired currency code
#         destination='acct_1OFvpvDA7bmXIfLx',
#     )


# try:
#     # Retrieve the balance of your main Stripe account
#     balance = stripe.Balance.retrieve()
#     print(balance)
#     # Access the available and pending amounts
#     available_amount = balance.available[0].amount
#     pending_amount = balance.pending[0].amount

#     # Convert amounts to a readable format (e.g., dollars and cents)
#     available_amount_formatted = available_amount / 100.0
#     pending_amount_formatted = pending_amount / 100.0

#     print(f"Available Balance: ${available_amount_formatted}")
#     print(f"Pending Balance: ${pending_amount_formatted}")

# except stripe.error.StripeError as e:
#     print(f"Error retrieving balance: {e}")





# def is_account_enabled(account_id):
#     try:
#         account = stripe.Account.retrieve(account_id)
#         charges_enabled = account.get('charges_enabled', False)
#         payouts_enabled = account.get('payouts_enabled', False)

#         if charges_enabled and payouts_enabled:
#             return True
#         else:
#             return False

#     except stripe.error.StripeError as e:
#         # Handle the error as needed
#         print(f"Stripe Error: {e}")
#         return False

# # Replace 'your_connect_account_id' with the actual ID of your Connect account
# connect_account_id = 'acct_1OIUjLD11zizYbXA'
# result = is_account_enabled(connect_account_id)

# if result:
#     print("Connect account is enabled.")
# else:
#     print("Connect account is not enabled.")




# Replace 'your_transfer_id' with the actual transfer ID
transfer_id = 'tr_1OJVTgDBYJ1xxvlEIwpetsR7'

try:
    # Retrieve transfer details
    transfer = stripe.Transfer.retrieve(transfer_id)
    print(transfer)
    # Get the transfer status
    transfer_status = transfer.get('status')
    print(transfer_status)
    # Check if the transfer is successful
    if transfer_status == 'succeeded':
        print('Transfer is successful!')
    else:
        print('Transfer has a different status:', transfer_status)

except stripe.error.StripeError as e:
    # Handle Stripe API errors
    print(f"Stripe API Error: {e}")
except Exception as e:
    # Handle other exceptions
    print(f"Error: {e}")