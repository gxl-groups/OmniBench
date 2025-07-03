from tqdm import tqdm
import time
import concurrent.futures
from chat_completions import generate_relpy
import os


ICL_QA_1 = """
> Q: Is there any bottle in image?
> A: 
1. Description: There is a green bottle with a white cap and a green toothbrush beside it.
2. Answer: Yes.

> Q: How many bottles in the image?
> A: 
Answer: 1.

> Q: Describe the color of bottle in image in detail. And according the description, answer my question: <Is there any green bottle?
> A: 
1. Description: The bottle in the image is green in color. It has a green tint and is made of a translucent material, allowing the green liquid inside to be visible.
2. Answer: Yes, there is a green bottle in the image.

> Q: Is there any toothbrush in image?
> A: 
1. Description: There is a toothbrush in the image.
2. Answer: Yes.

> Q: How many toothbrushs in the image?
> A: 
Answer: 1.

> Q: Describe the color of toothbrush in image in detail. And according the description, answer my question: <Is there any white toothbrush?
> A: 
1. Description: The toothbrush in the image has a green handle and white bristles.
2. Answer: No, there is no white toothbrush in the image.
"""

ICL_RESPONSE_1 = """
- **Detailed Comparison**:
1. **Green Bottle**:
   - The answer to the question "Is there any green bottle?" confirms the presence of a green bottle in the image.
   - The image contains a green bottle with a white cap, as described in the prompt text.
2. **White Toothbrush**:
   - The answer to the question "Is there any toothbrush in the image?" confirms the presence of a toothbrush.
   - However, the color of the toothbrush in the image does not match the description of a white toothbrush. It has a green handle and white bristles.
   - The image includes a toothbrush but does not have a white handle as specified in the prompt text.

- **Summary of Evaluation**:
The image aligns quite well with the prompt text but does fall short in accurately matching the color of the toothbrush.

- **Rating**: 8/10
The image fulfills the criteria of having a green bottle and a toothbrush but loses points due to the color discrepancy of the toothbrush.
"""


def create_message(prompt_text, VQA_evaluation):
    messages = [
        {
            "role": "system",
            "content": "You are an expert in evaluating image content based on descriptive prompts. "
            "Your task is to analyze and compare two inputs: a 'prompt text' that describes an image and a 'questions and answers' section that details the actual content of the image. "
            "You need to evaluate how well the image meets the requirements of the prompt text based on the comparison of these two inputs. "
            "Provide a detailed analysis and rate the alignment between the image and the prompt on a scale of 1 to 10, "
            "where 1 is a poor match and 10 is a perfect match. Identify any significant differences or strong alignments."
            "Format your response in the following structure for readability:\n\n"
            "- **Detailed Comparison**: Break down every part of the 'prompt text' and compare it to the image description which is from the 'questions and answers'. Please rigorously check that the requirements in the 'prompt text' is met or not.\n"
            "- **Summary of Evaluation**: According to detailed comparison. Provide a brief overview of how well the image meets the prompt.\n"
            "- **Rating**: Provide a final rating from 1 to 10.\n\n"
            "Use bullet points, subheadings, and lists where appropriate to make your response clear and easy to read.",
        },
        {
            "role": "user",
            "content": f"Prompt text: 'A green bottle and a white toothbrush.'"
            f"Questions and answers:\n{ICL_QA_1}",
        },
        {"role": "assistant", "content": f"{ICL_RESPONSE_1}"},
        {
            "role": "user",
            "content": f"Prompt text: '{prompt_text}'"
            f"Questions and answers:\n{VQA_evaluation}",
        },
    ]
    return messages


API_KEYS = [
    "xxx",
    "xxx",
]
api_key_index = 0


def get_next_api_key():
    global api_key_index
    api_key = API_KEYS[api_key_index]
    api_key_index = (api_key_index + 1) % len(API_KEYS)
    return api_key


def llm_evaluate_and_save(args):
    QA_result_path, prompt, llm_evaluation_file_path = args
    with open(QA_result_path, "r", encoding="utf-8") as file:  # 打开文件
        QA_result = file.read()

    if os.path.exists(llm_evaluation_file_path):
        with open(llm_evaluation_file_path, "w") as f:
            f.write("")  # 清空文件内容

    MAX_TRY = 4  # Maximum number of attempts, you can modify it as needed
    for _ in range(MAX_TRY):
        try:
            API_KEY = get_next_api_key()
            print("QA_result_path:", QA_result_path)

            messages = create_message(prompt_text=prompt, VQA_evaluation=QA_result)
            reply = generate_relpy(
                messages=messages,
                api_key=API_KEY,
            )
            with open(llm_evaluation_file_path, "a") as f:  # Append mode
                f.write(reply)  # Write the reply to the file
            break
        except Exception as e:
            print(f"Error processing data: {e}")
            time.sleep(1)


if __name__ == "__main__":
    # === Single File Processing ===
    # Modify the following parameters according to the actual situation
    QA_result_path = ""
    prompt = ""
    output_llm_evaluation_path = ""
    # Call the function to evaluate with LLM and save the result
    llm_evaluate_and_save((QA_result_path, prompt, output_llm_evaluation_path))

    """
    # === Batch Processing ===
    Batch = 64  # as an example

    # according to the actual situation, modify the following code
    QA_result_path_list = []  # list of QA result paths
    prompt_list = []  # list of prompts
    output_llm_evaluation_path_list = []  # list of output paths

    with concurrent.futures.ThreadPoolExecutor(max_workers=Batch) as executor:
        results = list(
            tqdm(
                executor.map(
                    llm_evaluate_and_save,
                    zip(
                        QA_result_path_list, prompt_list, output_llm_evaluation_path_list
                    ),
                ),
                total=len(QA_result_path_list),
            )
        )
    """
