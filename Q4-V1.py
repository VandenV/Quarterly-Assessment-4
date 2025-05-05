import openai
# Set the API key
openai.api_key = "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"
# Create the completion request
completion = openai.ChatCompletion.create(
model="gpt-4",
messages=[
{"role": "system", "content": "You are a helpful assistant."},
{"role": "user", "content": "Write a haiku about recursion in programming."}
]
)
# Print the response
print(completion.choices[0].message['content'])