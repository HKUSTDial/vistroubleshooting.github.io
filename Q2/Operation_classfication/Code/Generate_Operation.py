import pandas as pd
from openai import OpenAI
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from config import API_CONFIG

def load_data(file_path):
    return pd.read_excel(file_path)

def create_classification_prompt(incomplete_code, complete_code):
    """Create classification prompt"""
    return f"""Analyze the differences between these two Vega-Lite visualization codes and identify the specific categories, subcategories, and operations involved based on the given classification criteria.

Original Code:
{incomplete_code}

Completed Code:
{complete_code}

Please analyze according to the following classification criteria:

1. Data Transformation and Processing:
   Data:
   - Types of Data Sources
   - Data Format
   - Data Generators
   - Datasets

   Aggregate:
   - Aggregate in Encoding Field Definition
   - Aggregate Transform
   - Supported Aggregation Operations
   - Argmin/Argmax

   Bin:
   - Binning in Encoding Field Definition
   - Bin Transform
   - Bin Parameters
   - Ordinal Bin

   Join Aggregate:
   - Join Aggregate Field Definition
   - Join Aggregate Transform Definition

   Stack:
   - Stack in Encoding Field Definition
   - Stack Transform

   Window:
   - Window Field Definition
   - Window Transform Definition
   - Window Only Operation Reference

   Other Transform:
   - Calculate
   - Density
   - Extent
   - Filter
   - Flatten
   - Fold
   - Impute
   - Loess
   - Lookup
   - Pivot
   - Quantile
   - Regression
   - Sample

2. View:
   Schema:
   - $schema

   Title:
   - Alignment
   - Color
   - Font size

   Width/Height:
   - Specifying Fixed Width and Height
   - Specifying Responsive Width and Height
   - Specifying Width and Height per Discrete Step
   - Step for Offset Channel
   - Autosize
   - Width and Height of Multi-View Displays

   Mark Type:
   - Arc Properties/Config
   - Area Properties/Config
   - Bar Properties/Config
   - Boxplot Properties/Config
   - Circle Properties/Config
   - Errorband Properties/Config
   - Errorbar Properties/Config
   - Geoshape Properties/Config
   - Image Properties/Config
   - Line Properties/Config
   - Point Properties/Config
   - Rect Properties/Config
   - Rule Properties/Config
   - Square Properties/Config
   - Text Properties/Config
   - Tick Properties/Config
   - Trail Properties/Config

   Encoding Channels:
   - Position Channels
   - Position Offset Channels
   - Polar Position Channels
   - Geographic Position Channels
   - Mark Property Channels
   - Text and Tooltip Channels
   - Hyperlink Channel
   - Description Channel
   - Level of Detail Channel
   - Key Channel
   - Order Channel
   - Facet Channels

   Time Unit:
   - Time Unit in Encoding Field Definition
   - Time Unit Transform
   - UTC time
   - Time Unit Parameters

   Sort:
   - Sorting Continuous Fields
   - Sorting Discrete Fields

   Scale:
   - Scale Types
   - Scale Domains
   - Scale Ranges
   - Continuous Scales
   - Discrete Scales
   - Discretizing Scales
   - Disabling Scale

   Legends:
   - Legend Types
   - Combined Legend
   - Legend Properties
   - Gradient
   - Labels
   - Symbols
   - Symbol Layout
   - Title

   Axis:
   - Using Axis minExtent
   - Using Axis labelExpr
   - Using Axis tickBand
   - Customize Title
   - Grid
   - Conditional Axis Properties

   Other Encoding Functions:
   - Band Position
   - Condition
   - Datum
   - Field
   - Format
   - Header
   - Impute
   - Type
   - Value

3. Selection and Interaction:
   Bind:
   - Input Element Binding
   - Legend Binding
   - Scale Binding

   Selection:
   - Selection Projection with encodings and fields
   - Point Selection Properties
   - Interval Selection Properties

   Interaction:
   - Parameters In Expression Strings
   - Parameters As Predicates
   - Parameters Data Extents

   Tooltip:
   - Tooltip Based on Encoding
   - Tooltip Based on Data Point
   - Tooltip Channel
   - Tooltip Image
   - Disable Tooltips

4. View Composition and Layout:
   Facet:
   - Row-Facet
   - Wrapped Facet
   - Grid Facet

   Concatenate:
   - Horizontal Concatenation
   - Vertical Concatenation
   - Wrappable Concatenation

   Repeat:
   - Repeated Line Charts
   - Multi-series Line Chart
   - Repeated Histogram
   - Scatterplot Matrix

   Resolve:
   - Scale Resolution
   - Axis Resolution
   - Legend Resolution

   Layer:
   - Layer

Please analyze the differences and return the results in the following JSON format:
```json"""+"""
{
    "analysis": {
        "description": "Detailed description of the main differences between the two codes",
        "key_changes": [
            "Change 1",
            "Change 2"
        ]
    },
    "classifications": {
        "data_transformation": {
            "changes": [
                {
                    "category": "category name",
                    "subcategory": "subcategory name",
                    "operation": "specific operation",
                    "code_before": "relevant code segment from original code",
                    "code_after": "relevant code segment from modified code"
                }
            ]
        },
        "view": {
            "changes": [
                {
                    "category": "category name",
                    "subcategory": "subcategory name",
                    "operation": "specific operation",
                    "code_before": "relevant code segment from original code",
                    "code_after": "relevant code segment from modified code"
                }
            ]
        },
        "selection_interaction": {
            "changes": [
                {
                    "category": "category name",
                    "subcategory": "subcategory name",
                    "operation": "specific operation",
                    "code_before": "relevant code segment from original code",
                    "code_after": "relevant code segment from modified code"
                }
            ]
        },
        "view_composition": {
            "changes": [
                {
                    "category": "category name",
                    "subcategory": "subcategory name",
                    "operation": "specific operation",
                    "code_before": "relevant code segment from original code",
                    "code_after": "relevant code segment from modified code"
                }
            ]
        }
    }
}
```
"""

def truncate_data(vega_code):
    """Truncate long data arrays in Vega-Lite specifications"""
    try:
        # Parse the Vega-Lite code
        spec = json.loads(vega_code)
        
        # Check if there's inline data
        if "data" in spec and "values" in spec["data"]:
            values = spec["data"]["values"]
            if isinstance(values, list) and len(values) > 10:
                # Keep only first 10 items
                spec["data"]["values"] = values[:10]
                # Add a comment to indicate truncation
                spec["data"]["_comment"] = f"Data truncated from {len(values)} to 10 items"
            
        # Convert back to string with proper formatting
        return json.dumps(spec, indent=2)
    except:
        # If parsing fails, return original code
        return vega_code

def clean_json_response(response_text):
    """Clean API response text to extract pure JSON content"""
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

def classify_operations(client, df):
    results = []
    
    # Process all rows
    for index, row in df.iterrows():
        print(f"Processing row {index + 1} of {len(df)}")
        
        # Truncate data in both incomplete and complete code
        complete_code = truncate_data(row['Question Code'])
        incomplete_code = truncate_data(row['Answer Code'])
        
        prompt = create_classification_prompt(incomplete_code, complete_code)
        
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
            classification['Question ID'] = row["Question ID"]
            results.append(classification)
            
        except Exception as e:
            print(f"Error processing row {index + 1}: {str(e)}")
            # Continue with next row instead of breaking the entire process
            continue
    
    return results

def clean_code_string(code_str):

    if isinstance(code_str, str):
        code_str = code_str.replace('\n', ' ')
        code_str = ' '.join(code_str.split())
        code_str = code_str.replace('"', '""')
    return code_str

def save_results(results, output_path):

    for result in results:
        if 'Question ID' in result:
            result['Question ID'] = int(result['Question ID'])
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

def main():
    input_file = "dataset/3_validCode_cases/288_Vega_refine.xlsx"
    output_file = "Q2/Operation_classfication/Output/operation_classification_results_1.json" 

    df = pd.read_excel(input_file)
    client = OpenAI(
        api_key=API_CONFIG["api_key"],
        base_url=API_CONFIG["base_url"]
    )
    
    results = classify_operations(client, df)
    save_results(results, output_file)


if __name__ == "__main__":
    main()
