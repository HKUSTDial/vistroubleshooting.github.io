import pandas as pd
from openai import OpenAI
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import API_CONFIG

def create_classification_prompt(title, description):
    """Create a classification prompt."""
    # Define the example JSON structure as a separate variable
    json_example = '''{
    "category": "Troubleshooting Issues",
    "subcategories": [
        {
            "name": "Visual Style",
            "confidence": "high/medium/low",
            "analysis": {
                "reasoning": "explanation of why this classification applies",
                "key_points": ["key point 1", "key point 2"]
            }
        },
        {
            "name": "Data Transformation",
            "confidence": "high/medium/low",
            "analysis": {
                "reasoning": "explanation of why this classification applies",
                "key_points": ["key point 1", "key point 2"]
            }
        }
        // More subcategories can be added here
    ]
}'''

    prompt = f"""Analyze the following Vega-Lite visualization question and classify it into exactly ONE category with potentially multiple subcategories that best describe the main issues.

Title: {title}
Description: {description}

Classification Framework:

Troubleshooting Issues:
Questions involving defective visualizations, typically accompanied by code snippets. Focus is on improving or fixing existing visualizations rather than creating new ones. Divided into four subcategories:
- Visual Style: Focus on improving aesthetics and design of visualizations. Example: "How to get a dashed line in the legend?"
- Data Transformation: Challenges in processing and restructuring data for visualization. Example: "How to encode table-based data?"
- Interaction Design: Adding or refining interactive features in visualizations. Example: "Is there a way to have a dynamic tooltip in Deneb?"
- Syntax Error: Coding mistakes preventing proper rendering. Example: "VL editor table is empty."

Authoring Issues:
Questions without defective visualizations, containing code snippets related to functionality. Users typically provide data and requirements. Divided into two subcategories:
- Simple Design: Straightforward visualization tasks and basic feature implementations. Example: "How do I create a progress bar in VL?"
- Complex Design: Sophisticated visualization requirements or advanced features. Example: "How can I have multiple levels in an axis in VL?"

System Issues:
Challenges external to the VegaLite compiler, involving environment configuration, dependencies, or tool integration. Divided into two subcategories:
- Code Integration: Challenges in embedding Vega-Lite into other platforms. Example: "Vega-Lite API misbehaving."
- Tool Compatibility: Issues with Vega-Lite derivatives like Altair or Vega. Example: "How to zoom markgeoshape to a specific region in Altair?"

Important:
1. Choose ONLY ONE category and potentially multiple subcategories that best represent the main issues.
2. Provide detailed analysis explaining why these specific classifications were chosen.
3. Include a confidence level (high/medium/low) for each classification.

Please analyze and return the classification in JSON format.
Add the surrounding ```json\n \n```Use the following JSON format:
```json
{json_example}
```
"""
    return prompt

def clean_json_response(response_text):
    
    json_text = ""
 
    if '```json' in response_text:
        parts = response_text.split('```json')
        json_text = parts[1].split('```')[0] if len(parts) > 1 else ""

    elif '```' in response_text:
        parts = response_text.split('```')
        json_text = parts[1].split('```')[0] if len(parts) > 1 else ""

    else:
        if '{' in response_text and '}' in response_text:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            json_text = response_text[start:end]
        else:
            json_text = response_text 

    return json_text.strip()

def classify_questions(client, df, output_file):
    """Classify questions using GPT API and save results."""
    results = []

    for index, row in df.iterrows():
        title = row['Title']
        description = row['Description']
        questionId = row['Question ID']

        prompt = create_classification_prompt(title, description)

        try:
            response = client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                model="gpt-4",
            )

            response_content = response.choices[0].message.content
            cleaned_response = clean_json_response(response_content)
            classification = json.loads(cleaned_response)
            classification['questionId'] = questionId
            results.append(classification)

            # 保存结果
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
            print(f"Saved result to {output_file}")

        except Exception as e:
            print(f"Error occurred: {e}")
            classification = {
                'questionId': questionId,
                'result': response_content
            }
            results.append(classification)

    return results

def main():
    client = OpenAI(
        api_key=API_CONFIG["api_key"],
        base_url=API_CONFIG["base_url"]
    )

    input_file = "dataset/1_All_cases/889_Vega.xlsx"
    output_file = "Q1/Output/question_classification_results_1.json"

    df = pd.read_excel(input_file)

    results = classify_questions(client, df, output_file)

if __name__ == "__main__":
    main()
