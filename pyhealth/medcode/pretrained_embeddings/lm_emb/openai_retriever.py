import requests
import json
import os


def embedding_retrieve(term):
    # The API key is read lazily so that importing this module does not
    # require OPENAI_API_KEY to be set.
    key = os.environ['OPENAI_API_KEY']

    # Set up the API endpoint URL and request headers
    url = "https://api.openai.com/v1/embeddings"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}"
    }

    # Set up the request payload with the text string to embed and the model to use
    payload = {
        "input": term,
        "model": "text-embedding-ada-002"
    }

    # Send the request and retrieve the response
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Extract the text embeddings from the response JSON
    embedding = response.json()["data"][0]['embedding']

    return embedding