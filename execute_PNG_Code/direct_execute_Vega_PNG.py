import vl_convert as vlc
import json

# Vega-Lite specification
vega_spec = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "transform": [
        {"calculate": "1", "as": "one"}
    ],
    "layer": [
        {
            "mark": {"type": "bar"},
            "encoding": {
                "x": {
                    "field": "diff",
                    "type": "quantitative",
                    "title": "Difference"
                },
                "y": {
                    "field": "diff",
                    "type": "quantitative",
                    "title": "Value"
                }
            }
        },
        {
            "mark": {"type": "rule", "color": "red"},
            "encoding": {
                "y": {"datum": 2}
            }
        }
    ],
    "data": {
        "values": [
            {"diff": 1},
            {"diff": 2},
            {"diff": 3}
        ]
    }
}

def save_vega_chart(spec, output_path):
    try:
        if not output_path.endswith('.png'):
            output_path += '.png'
            
        if isinstance(spec, dict):
            spec = json.dumps(spec)

        png_data = vlc.vegalite_to_png(spec)

        with open(output_path, 'wb') as f:
            f.write(png_data)
            
        print(f"Chart successfully saved to: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error processing chart: {str(e)}")
        return False

save_vega_chart(vega_spec, 'output_chart.png')