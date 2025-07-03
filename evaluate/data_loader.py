import json
import os
import glob
import re


def read_score(llm_eva_output_path):
    """
    Read the score from the llm_eva_output_path
    - Args:
        llm_eva_output_path: the path of the llm evaluation output file
    """
    with open(llm_eva_output_path, "r", encoding="utf-8") as file:
        llm_result = file.read()
    rating_match = re.search(r"Rating[\s\S]*?(\d+(\.\d+)?)/10", llm_result)
    if rating_match:
        llm_rating = int(rating_match.group(1))
        # print(f"Rating extracted: {llm_rating}")

    else:
        # print(f"Rating not found in: {SKILL}-{LEVEL}-{p_id}")
        print(f"Rating not found in: {llm_eva_output_path}")
        llm_rating = None
    return llm_rating


def read_skill(skill_dir):
    """
    Read the skill data from the skill_dir
    - Args:
        skill_dir: the directory of the skill data

    - Returns:
        results: a dictionary of the skill data
        results = {
            '1': { # level
                {
                    "0": { # prompt_id
                        "objects": ["apple", "banana"],
                        "tags": ["..."],
                        "prompt": "A red apple and a yellow banana."
                    },
                        "objects": ["apple", "banana"],
                        "tags": ["..."],
                        "prompt": "A yellow apple and a green banana."
                    }
                    ...
                }
            },
            ...
        }
    """
    results = {}
    txt_file_paths = glob.glob(os.path.join(skill_dir, "*.json"))
    for txt_file_path in sorted(txt_file_paths):
        # 检查文件名里有没有包含数字，将该数字记录成一个变量：level
        level = "".join(
            filter(str.isdigit, os.path.basename(txt_file_path))
        )  # like: "3"
        # results.setdefault(level, )
        with open(txt_file_path, "r") as f:
            data = json.load(f)
        results[level] = data
    return results


if __name__ == "__main__":
    skill_dir = "data/composite/OC_AB_SR"
    skill_data = read_skill(skill_dir)
    for level, datas in skill_data.items():
        print(f"Level: {level}")
        print(datas)
        for p_id in datas:
            data = datas[p_id]
            objects = data["objects"]
            tags = data["tags"]
            prompt_text = data["prompt"]
            print(
                f"Prompt_id: {p_id}",
                f"Objects: {objects}",
                f"Tags: {tags}",
                f"Prompt: {prompt_text}",
            )
