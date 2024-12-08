import os
import base64
from openai import OpenAI
import json
import pandas as pd
import re
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import API_CONFIG
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_question_images(question_id, image_folder):
    image_paths = []
    pattern = f"^{question_id}_\\d+\\.png$"
    
    for filename in os.listdir(image_folder):
        if re.match(pattern, filename):
            image_paths.append(os.path.join(image_folder, filename))
    
    return sorted(image_paths)

def create_answer_prompt(title, description, example=None, image_paths=None, external_link=None):
    """Create answer prompt with precise examples and images"""
    example_content = f"\nRelevant Examples:\n{example}" if example else ""
    external_link_content = f"\nExternal Link in Description:\n{external_link}" if external_link else ""

    content = [{
        "type": "text",
        "text": f"""Based on the following Vega-Lite visualization question{' and provided images' if image_paths else ''}, generate a comprehensive answer.

Title: {title}
Description: {description}{external_link_content}{example_content}

Please provide a detailed response in the following format:

1. First understand the user's visualization needs
2. Analyze the provided examples
3. Explain the solution step by step
4. Provide complete Vega-Lite code with explanations

Please return the response in JSON format:
```json
{{
    "problem_analysis": {{
        "user_needs": "description of what the user is trying to achieve",
        "visualization_requirements": [
            "requirement 1",
            "requirement 2"
        ]
    }},
    "solution": {{
        "examples_analysis": {{
            "relevant_sections": [
                {{
                    "section": "section from examples",
                    "relevance": "why this example is relevant",
                    "key_information": "important information from this example"
                }}
            ]
        }},
        "implementation_steps": [
            {{
                "step_number": 1,
                "action": "specific action to take",
                "code_snippet": "relevant Vega-Lite code for this step"
            }}
        ],
        "complete_code": {{
            "vega_lite_spec": "complete Vega-Lite specification"
        }}
    }}
}}
```
"""
    }]
    
    # 如果有图片，添加到content中
    if image_paths:
        for image_path in image_paths:
            base64_image = encode_image(image_path)
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                }
            })
    
    return content

def clean_json_response(response_text):
    if '```json' in response_text:
        parts = response_text.split('```json')
        if len(parts) > 1:
            json_text = parts[1]
    elif '```' in response_text:
        parts = response_text.split('```')
        if len(parts) > 1:
            json_text = parts[1]
    else:
        json_text = response_text
    
    if '```' in json_text:
        json_text = json_text.split('```')[0]
    
    return json_text.strip()

def generate_answers(client, df, image_folder):
    results = []
    
    for index, row in df.iterrows():
        if pd.isna(row.get('Precise Examples')):
            continue
        question_id = str(row['Question ID'])
        title = row['Title']
        description = row['Description']

        image_paths = get_question_images(question_id, image_folder)
        
        content = create_answer_prompt(
            title=title, 
            description=description,
            example=row.get('Precise Examples'),
            external_link=row.get('External_Link') if pd.notna(row.get('External_Link')) else None,
            image_paths=image_paths
        )
        cleaned_response=''
        try:
            model = "gpt-4-vision-preview"
            
            response = client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": content
                }],
                model=model,
                max_tokens=20000
            )
            
            response_content = response.choices[0].message.content
            cleaned_response = clean_json_response(response_content)
            answer = json.loads(cleaned_response)
            answer['question_id'] = question_id
            results.append(answer)
            
        except Exception as e:
            results.append({
                'question_id': question_id,
                'error': cleaned_response
            })

    return results

def main():

    client = OpenAI(
        api_key=API_CONFIG["api_key"],
        base_url=API_CONFIG["base_url"]
    )
    
    input_file = "dataset/4_DocEx_cases/47_Vega_refine.xlsx"
    image_folder = "dataset/4_DocEx_cases/que_image_47"
    output_file = "Q4/results/generated_answers_level_2_prec_example_test.json"
    df = pd.read_excel(input_file)


    results = generate_answers(client, df, image_folder)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
