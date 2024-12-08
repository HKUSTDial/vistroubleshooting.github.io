import pandas as pd
import json
import os
import vl_convert as vlc

# Ensure the folder for saving images exists
output_dir = 'ans_code_image_40'
os.makedirs(output_dir, exist_ok=True)

# Load the Excel file
input_file = 'dataset/4_DocEx_cases/47_Vega_refine.xlsx'
df = pd.read_excel(input_file)

def save_vega_chart(row):
    try:
        # Get the code and Question ID
        code = row['Answer Code']
        q_id = str(row['Question ID'])
        # Parse the Vega-Lite specification
        spec = json.loads(code)
        
        # Save as PNG
        save_path = os.path.join(output_dir, f'{q_id}.png')
        
        # Convert to PNG
        png_data = vlc.vegalite_to_png(spec)
        
        # Write the PNG file
        with open(save_path, 'wb') as f:
            f.write(png_data)
        
        print(f"Successfully saved image: {q_id}.png")
        
    except Exception as e:
        print(f"Error processing Question ID {q_id}: {str(e)}")

# Apply the save function to each row
df.apply(save_vega_chart, axis=1)
