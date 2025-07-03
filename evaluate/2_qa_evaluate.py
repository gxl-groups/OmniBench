from data_loader import read_skill
import json
from tqdm import tqdm
import os


def make_question_json(q_id, question, parent=[], skill=""):
    question_json = {
        "q_id": q_id,
        "question": question,
        "parent": parent,
        "skill": skill,
    }
    return question_json


def create_question(scene_graph_json, skill):
    question_list = []
    # question_pos_id[q_id] = True means the question with q_id is positive
    question_pos_id = dict()
    q_id = 0
    # object_id[object] = q_id means the object is in the image
    object_id = dict()

    # extend the question and append it to the question_list
    def extend_and_append_in_list(q_id, question, parent, skill):
        question_final = f"""{question}. Give out visual reasoning in brief before your final answer.
                Answer in the format like:
                1. Description: ...
                2. Answer: ...
                """
        question_json = make_question_json(
            q_id=q_id, question=question_final, parent=parent, skill=skill)
        question_list.append(question_json)
        question_pos_id[q_id] = True

    for object in scene_graph_json:
        if object != "connection":  # object = object name
            # (0) existence
            # remove the number in the object name
            object_pure = object.strip("0123456789 ")
            question = f"Is there any {object_pure} in image?"
            object_id[object_pure] = q_id
            extend_and_append_in_list(
                q_id, question=question, parent=[], skill="existence")
            q_id = q_id + 1

            attributes_list = scene_graph_json[object]

            if isinstance(attributes_list, dict):
                attributes_list = [attributes_list]
            for attributes_dict in attributes_list:
                for attribute in attributes_dict:
                    attribute_value = attributes_dict[attribute]
                    if attribute_value != "":
                        # (1) counting
                        if attribute in ["counting"]:  # object counting
                            question = f"How many {object_pure}s in the image?"
                            extend_and_append_in_list(
                                q_id=q_id,
                                question=question,
                                parent=[object_id[object_pure]],
                                skill="object_counting",
                            )
                            q_id = q_id + 1
                        # (2) attribute binding
                        if attribute in [
                            "color",
                            "material",
                            "shape",
                            "pattern",
                            "sentiment",
                        ]:  # attribute binding
                            # (2.1) attribute binding in differentiation
                            if isinstance(attribute_value, list):
                                for attribute_v in attribute_value:
                                    if "OU" in skill:
                                        question = f"Describe the {attribute} of {object} in image in detail. And according the description, answer my question: <Is there every {object} {attribute_v} in the image?>"
                                    else:
                                        question = f"Describe the {attribute} of {object} in image in detail. And according the description, answer my question: <Is there any {attribute_v} {object} in the image?>"
                                    extend_and_append_in_list(
                                        q_id=q_id,
                                        question=question,
                                        parent=[object_id[object_pure]],
                                        skill="attribute",
                                    )
                                    q_id = q_id + 1
                            # (2.2) normal attribute binding
                            else:
                                if "universality" in skill:
                                    question = f"Describe the {attribute} of {object} in image in detail. And according the description, answer my question: <Is there every {object} {attribute_value} in the image?>"
                                else:
                                    question = f"Describe the {attribute} of {object} in image in detail. And according the description, answer my question: <Is there any {attribute_value} {object} in the image?>"
                                extend_and_append_in_list(
                                    q_id=q_id,
                                    question=question,
                                    parent=[object_id[object_pure]],
                                    skill="attribute",
                                )
                                q_id = q_id + 1
        else:  # object = "connection"
            relationships = scene_graph_json[object]
            for objects in relationships:
                objects_list = objects[1:-1].split(",")[:2]
                if len(objects_list) != 2:
                    continue
                obj1, obj2 = objects_list
                obj1 = obj1.strip("0123456789 ")
                obj2 = obj2.strip("0123456789 ")
                if object_id.get(obj1) is None or object_id.get(obj2) is None:
                    continue
                relationship_value = relationships[objects]
                if relationship_value:
                    if isinstance(relationship_value, list):
                        for relationship_v in relationship_value:
                            if "OU" in skill:
                                question = f"Describe the position of {obj1} and {obj2} in image briefly. And according the description, answer my question: <Is every {obj1} {relationship_v} the {obj2} in the image?>"
                            else:
                                question = f"Describe the position of {obj1} and {obj2} in image briefly. And according the description, answer my question: <Is the {obj1} {relationship_v} the {obj2} in the image?>"
                            extend_and_append_in_list(
                                q_id=q_id,
                                question=question,
                                parent=[object_id[obj1], object_id[obj2]],
                                skill="relationship",
                            )
                            q_id = q_id + 1
                    else:
                        if "OU" in skill:
                            question = f"Describe the position of {obj1} and {obj2} in image briefly. And according the description, answer my question: <Is every {obj1} {relationship_value} the {obj2}?>"
                        else:
                            question = f"Describe the position of {obj1} and {obj2} in image briefly. And according the description, answer my question: <Is the {obj1} {relationship_value} the {obj2}?>"
                        extend_and_append_in_list(
                            q_id=q_id,
                            question=question,
                            parent=[object_id[obj1], object_id[obj2]],
                            skill="relationship",
                        )
                        q_id = q_id + 1

    return question_list, question_pos_id


def process_image_and_chat(
    img_path="",
    question=None,
):
    # TODO: process the image and chat with the VQA or MLLM model
    # according to the question, return the answer, use any visual model you like, for example: llava-onevision
    answer = "..."
    return answer


def run(scene_graph_path, image_path, skill, output_path):
    with open(scene_graph_path, 'r') as f:
        scene_graph_json = json.load(f)
    question_list, question_pos_id = create_question(scene_graph_json, skill)
    for question_json in tqdm(question_list):
        question = question_json["question"]
        q_id = question_json["q_id"]
        parents = question_json["parent"]
        # check if all the parents are positive
        is_need = all(question_pos_id.get(parent)
                      == True for parent in parents)
        if is_need:  # if all the parents are positive
            response = process_image_and_chat(image_path, question)

            # if the answer is negative, update the question_pos_id
            if response == "No" or "No," in response or " no " in response:
                question_pos_id[q_id] = False
            else:
                score = score + 1
            with open(output_path, "a") as f:
                f.write(f"> Q: {question}\n")
                f.write(f"> A: \n{response}\n\n")
        else:  # if not all the parents are positive, skip the question, and write the default answer
            with open(output_path, "a") as f:
                f.write(
                    f"> Q: {question}\n")
                if "how many" in question:
                    f.write(
                        f"> A: \nThe corresponding object does not exist. So the answer is of course 0.\n")
                else:
                    f.write(
                        f"> A: \nThe corresponding object does not exist. So the answer is of course No.\n")


if __name__ == "__main__":
    # for example, evaluate the skill "cross_counting_attribute_binding_spatial"
    skill_dir = 'data/OC_AB_SR'
    skill_data = read_skill(skill_dir)
    for level, datas in skill_data.items():
        print(f"Level: {level}")
        print(datas)
        for p_id in datas:
            data = datas[p_id]
            objects = data['objects']
            tags = data['tags']
            prompt_text = data['prompt']
            print(f"Prompt_id: {p_id}", f"Objects: {objects}", f"Tags: {tags}",
                  f"Prompt: {prompt_text}")
            image_path = "path/to/image.jpg"
            scene_graph_path = "path/to/scene_graph.json"
            run(scene_graph_path, image_path, os.path.basename(
                skill_dir), "path/to/output.txt")
