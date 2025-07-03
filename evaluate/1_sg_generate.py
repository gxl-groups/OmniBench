
import json
from tqdm import tqdm
import time
import concurrent.futures
from chat_completions import generate_relpy
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)


format_example = """

    "object name1":{
        "counting": the number of object name1
        "color": color value (if it has color description), or "" (if has not)
        "material": material value (if it has matiral description), or "" (if has not)
        "pattern": ...
        "shape": ...
        "sentiment": ... 
    }.
    "object name2": {...},
    ...,
    "connection":{
        "(object name A, object name B)": connection,
        ...
    }
    ...
}

"""
ICL_general = {
    "role": "assistant",
    "content": """
            {
                "woman": {
                    "counting": 1,
                    "color": "",
                    "material": "",
                    "pattern": "",
                    "shape": "",
                    "sentiment": "happy"
                },
                "microwave": {
                    "counting": 1,
                    "color": "white",
                    "material": "",
                    "pattern": "",
                    "shape": ""
                },
                "connection": {
                    "(woman, microwave)": "on the left of",
                    "(woman, microwave)": "taller than"
                }
            }""",
}

ICL_negation = {
    "role": "assistant",
    "content": """
            {
                "car": {
                    "counting": 1,
                    "color": "not red",
                    "material": "",
                    "pattern": "",
                    "shape": "",
                    "sentiment": ""
                },
                "boat": {
                    "counting": 0,
                    "color": "",
                    "material": "",
                    "pattern": "",
                    "shape": ""
                },

            }""",
}

# not necessary to use this, but just in case, we can have more detail examples
ICL_differentiation = {
    "role": "assistant",
    "content": """
            {
                "woman": {
                    "counting": 1,
                    "color": "",
                    "material": "",
                    "pattern": "",
                    "shape": "",
                    "sentiment": ""
                }
                "vase": {
                    "counting": 1,
                    "color": ["red", "white"],
                    "material": "",
                    "pattern": "",
                    "shape": ""
                }
                "connection": {
                    "(vase, woman)": ["on the left of", "on the right of"]
                }
            }""",
}
ICL_interaction = {
    "role": "assistant",
    "content": """
            {
                "dog": {
                    "counting": 1,
                    "color": "black",
                    "material": "",
                    "pattern": "",
                    "shape": "",
                    "sentiment": ""
                },
                "woman": {
                    "counting": 1,
                    "color": "",
                    "material": "",
                    "pattern": "",
                    "shape": "",
                    "sentiment": "happy"
                }
                "microwave": {
                    "counting": 1,
                    "color": "white",
                    "material": "",
                    "pattern": "",
                    "shape": ""
                },
                "cat": {
                    "counting": 1,
                    "color": "blue",
                    "material": "",
                    "pattern": "",
                    "shape": "",
                    "sentiment": ""
                },
                "connection": {
                    "(dog, microwave)": "sleeping on"
                    "(woman, microwave)": "using",
                    "(cat, woman)": "runing around",
                }
            }""",
}

ICL_part = {
    "role": "assistant",
    "content": """
            {
                "woman": {
                    "counting": 1,
                    "color": "",
                    "material": "",
                    "pattern": "",
                    "shape": "",
                    "sentiment": "happy"
                },
                "handbag": {
                    "counting": 1,
                    "color": "",
                    "material": "leather",
                    "pattern": "",
                    "shape": "",
                    "sentiment": ""
                },
                "man": {
                    "counting": 1,
                    "color": "",
                    "material": "",
                    "pattern": "",
                    "shape": "",
                    "sentiment": ""
                },
                "umbrella": {
                    "counting": 1,
                    "color": "",
                    "material": "leather",
                    "pattern": "",
                    "shape": "",
                    "sentiment": ""
                },
                "microwave": {
                    "counting": 1,
                    "color": "white",
                    "material": "",
                    "pattern": "",
                    "shape": ""
                },
                "banana": {
                    "counting": 1,
                    "color": "green",
                    "material": "",
                    "pattern": "",
                    "shape": "",
                    "sentiment": ""
                },
                "connection": {
                    "(woman, handbag)": "with",
                    "(man, umbrella)": "with",
                    "(microwave, banana)": "containing"
                }
            }""",
}


def create_message(prompt_text, objects, skill):
    print(skill)
    if "ON" in skill:
        messages = [
            {
                "role": "system",
                "content": "You are a language specialist, help me convert a description to a json representation.",
            },
            {
                "role": "user",
                "content": f"Description: <The car is not red. Also, the boat is not in sight.> "
                f"please represent the objects ({objects}) with their counting, attribute and connection between them that appear in the description as a json data"
                f"(1)counting is the number of specific object, like 1, 2, ..., it must be a natural number. If description tell you that object is not in sight, which means the counting of this object is 0."
                f"(2)attribute is feature of the object, here are five attribute: color(like red, blue, ...), material(like wooden, metal...), pattern(like camouflage, plain, paisley...), shape(like round, square, crescentic...), sentiment(sentiment only has the following categories: 'happy', 'sad', 'angry', 'afraid', 'surprised', 'calm', 'excited', 'bored')."
                f"Answer me in the json format like {format_example}",
            },
            ICL_negation,
            {
                "role": "user",
                "content": f"Description: <{prompt_text}>. please represent the objects ({objects}) as a json data.",
            },
        ]
    elif (
        "OD" in skill
    ):
        messages = [
            {
                "role": "system",
                "content": "You are a language specialist, help me convert a description to a json representation.",
            },
            {
                "role": "user",
                "content": f"Description: <There are two vases positioned around the women; one on her left, and one on her right. One is red, one is white.> "
                f"please represent the objects ({objects}) with their counting, attribute and connection between them that appear in the description as a json data"
                f"(1)counting is the number of specific object, like 1, 2, ..., it must be a natural number."
                f"(2)attribute is feature of the object, here are five attribute: color(like red, blue, ...), material(like wooden, metal...), pattern(like camouflage, plain, paisley...), shape(like round, square, crescentic...), sentiment(sentiment only has the following categories: 'happy', 'sad', 'angry', 'afraid', 'surprised', 'calm', 'excited', 'bored')."
                f"(3)connection is the spatial relationship between two objects."
                f"Answer me in the json format like {format_example}",
            },
            ICL_differentiation,
            {
                "role": "user",
                "content": f"Description: <{prompt_text}>. please represent the objects ({objects}) as a json data.",
            },
        ]
    else:
        messages = [
            {
                "role": "system",
                "content": "You are a language specialist, help me convert a description to a json representation.",
            },
            {
                "role": "user",
                "content": f"Description: <A happy woman is on the left of a white microwave, and the woman is taller than the microwave. > "
                f"please represent the objects ({objects}) with their counting, attribute and connection between them that appear in the description as a json data"
                f"Answer me in the json format like {format_example}",
            },
            ICL_general,
            {
                "role": "user",
                "content": f"Description: <{prompt_text}>. please represent the objects ({objects}) as a json data.",
            },
        ]
    return messages


API_KEYS = [
    "XXX",
]
api_key_index = 0


def get_next_api_key():
    global api_key_index
    api_key = API_KEYS[api_key_index]
    api_key_index = (api_key_index + 1) % len(API_KEYS)
    return api_key


def graph_generate_and_save(messages, output_SG_path):
    # print(args)
    if (
        os.path.exists(output_SG_path)
        and os.path.getsize(output_SG_path) > 0
    ):
        return  # exiest and not empty, skip
    for _ in range(4):
        try:
            API_KEY = get_next_api_key()
            print(API_KEY)
            reply = generate_relpy(messages=messages, api_key=API_KEY)
            try:
                start_index = reply.find("{")
                end_index = reply.rfind("}")
                json_content = reply[start_index: end_index + 1]
                json_data = json.loads(json_content)
                reply = json_content
            except Exception as e:
                print(f"Error when check json: {e} \nError Reply: {reply}")
                continue

            # with open(output_SG_path, "a") as f:  # Append mode
            #     f.write(reply)  # Write the reply to the file
            with open(output_SG_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
            break
        except Exception as e:
            print(f"Error processing data: {e}")
            time.sleep(1)


if __name__ == "__main__":
    SG_output_dir = "examples/"

    messages = create_message("Two white clocks are on the side of two steel knives.", [
                              "clock", "knife"], "cross_counting_attribute_binding_spatial")
    graph_generate_and_save(messages, os.path.join(
        SG_output_dir, "SG_example.json"))
