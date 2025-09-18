import scrubadub

text = "My cat can be contacted on example@example.com, or 1800 555-5555"

# Replaces the phone number and email addresse with anonymous IDs.

print(scrubadub.clean(text))
'My cat can be contacted on {{EMAIL}}, or {{PHONE}}'