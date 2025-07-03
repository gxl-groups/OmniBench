from openai import OpenAI


API_KEY = "XXX"
BASE_URL = "https://XXX"

messages = [
    {
        "role": "system",
        "content": "You are a language specialist, help me build sentences(prompt) for T2I model.",
    },
    {
        "role": "user",
        "content": "Hello!"
    },
]


def generate_relpy(messages=messages, api_key=API_KEY, base_url=BASE_URL):
    client = OpenAI(api_key=api_key, base_url=base_url)

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages, temperature=0.8
    )
    print(f"LLM reply: {completion.choices[0].message.content}")
    return completion.choices[0].message.content


if __name__ == "__main__":
    generate_relpy()
