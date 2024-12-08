import json
import os
import vl_convert as vlc

# Ensure the folder for saving images exists
output_dir = '4_experiment/execute_PNG_Code'
os.makedirs(output_dir, exist_ok=True)

# Load the JSON file
input_file = '4_experiment/ans_code_image/right_answer.json'
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

def save_vega_chart(item):
    try:
        # Get the question ID and Vega-Lite specification
        q_id = str(item['question_id'])
        vega_spec = item['solution']['complete_code']['vega_lite_spec']
        
        # Save as PNG
        save_path = os.path.join(output_dir, f'{q_id}.png')
        
        # Ensure that vega_spec is in string format before conversion
        if isinstance(vega_spec, dict):
            vega_spec = json.dumps(vega_spec)
            
        png_data = vlc.vegalite_to_png(vega_spec)
        
        # Write the PNG file
        with open(save_path, 'wb') as f:
            f.write(png_data)
        
        print(f"Successfully saved image: {q_id}.png")
        
    except Exception as e:
        print(f"Error processing Question ID {q_id}: {str(e)}")

# Process each answer
for item in data:
    save_vega_chart(item)
