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
    """Encode image to base64 format"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_question_images(question_id, image_folder):
    """Get all image paths for a specific question ID"""
    image_paths = []
    pattern = f"^{question_id}_\\d+\\.png$"
    
    for filename in os.listdir(image_folder):
        if re.match(pattern, filename):
            image_paths.append(os.path.join(image_folder, filename))
    
    return sorted(image_paths)  # Sort by filename to ensure order

def create_answer_prompt(title, description, external_link, image_paths=None):
    """Create answer prompt"""
    # Build documentation content string
    external_link_content = f"\nExternal Link in Description:\n{external_link}" if external_link else ""
    content = [{
        "type": "text",
        "text": f"""Based on the following Vega-Lite visualization question{' and provided images' if image_paths else ''}, generate a comprehensive answer.

Title: {title}
Description: {description}{external_link}

Please provide a detailed response in the following format:

1. First understand the user's visualization needs
2. Explain the solution step by step
3. Provide complete Vega-Lite code with explanations

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
        "approach": "explanation of the chosen approach",
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
    
    # If there are images, add them to the content
    if image_paths:
        for index,image_path in enumerate(image_paths):
            base64_image = encode_image(image_path)
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                }
            })
    
    return content
def clean_json_response(response_text):
    """Clean API response text and extract JSON content"""
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
    """Generate answers for questions"""
    results = []
    
    for index, row in df.iterrows():
        question_id = str(row['Question ID'])
        title = row['Title']
        description = row['Description']
        
        # Get all images for this question
        image_paths = get_question_images(question_id, image_folder)
        
        # Create prompt content
        content = create_answer_prompt(
            title, 
            description,
            external_link=row.get('External_Link') if pd.notna(row.get('External_Link')) else None,
            image_paths=image_paths
        )
        cleaned_response=''
        try:
            # Select model based on image presence
            model = "gpt-4-vision-preview"
            
            response = client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": content
                }],
                model=model,
                max_tokens=70000
            )
            
            response_content = response.choices[0].message.content
            
            # Print processing information
            print(f"\nProcessing row {index} (Question ID: {question_id}):")
            print(f"Number of images: {len(image_paths)}")
            print(f"Using model: {model}")
            
            # Parse response
            cleaned_response = clean_json_response(response_content)
            answer = json.loads(cleaned_response)
            
            answer['question_id'] = question_id
            results.append(answer)
            
        except Exception as e:
            print(f"Error processing row {index}: {str(e)}")
            results.append({
                'question_id': question_id,
                'error': cleaned_response
            })
    
    return results

def main():
    # API settings
    client = OpenAI(
        api_key=API_CONFIG["api_key"],
        base_url=API_CONFIG["base_url"]
    )
    
    # File paths
    input_file = "dataset/3_validCode_cases/288_Vega.xlsx"
    image_folder = "dataset/3_validCode_cases/que_image"
    output_file = "Q3/output/L0_solutions_test.json"
    
    # Load data
    df = pd.read_excel(input_file)
    # Generate answers
    results = generate_answers(client, df, image_folder)
    
    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("Generation complete, results saved to", output_file)

if __name__ == "__main__":
    main()
