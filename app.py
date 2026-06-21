from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import google.generativeai as genai
import base64
import random
import string
import json
from datetime import datetime

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Configure Gemini
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None
    print("WARNING: GEMINI_API_KEY not set. Using fallback mode.")

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/style.css')
def serve_css():
    return send_from_directory('.', 'style.css')

@app.route('/script.js')
def serve_js():
    return send_from_directory('.', 'script.js')

@app.route('/generate', methods=['POST'])
def generate_image():
    data = request.json
    prompt = data.get('prompt', '').strip()
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    try:
        if model:
            # Try to generate with Gemini
            response = model.generate_content(
                f"Generate an image based on this description: {prompt}. Return as base64 encoded image.",
                generation_config=genai.types.GenerationConfig(
                    temperature=0.8,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=2048,
                )
            )
            
            # Try to extract image data
            image_data = None
            if hasattr(response, '_result') and response._result.candidates:
                parts = response._result.candidates[0].content.parts
                for part in parts:
                    if hasattr(part, 'data'):
                        image_data = part.data
                        break
                    elif hasattr(part, 'text') and part.text:
                        # Check if it's a base64 string
                        try:
                            base64.b64decode(part.text[:100])
                            image_data = base64.b64decode(part.text)
                            break
                        except:
                            pass
            
            if image_data and isinstance(image_data, bytes):
                img_base64 = base64.b64encode(image_data).decode('utf-8')
                data_url = f"data:image/png;base64,{img_base64}"
            else:
                # Fallback: generate SVG or use placeholder
                data_url = generate_svg_placeholder(prompt)
        else:
            data_url = generate_svg_placeholder(prompt)
        
        return jsonify({
            'image': data_url,
            'prompt': prompt
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            'image': generate_svg_placeholder(prompt),
            'prompt': prompt
        })

def generate_svg_placeholder(prompt):
    """Generate a simple SVG placeholder without requiring Pillow"""
    # Create a deterministic color based on prompt
    hash_val = sum(ord(c) for c in prompt) % 360
    color1 = f"hsl({hash_val}, 70%, 55%)"
    color2 = f"hsl({(hash_val + 60) % 360}, 70%, 45%)"
    
    # Generate random shapes as SVG
    shapes = []
    for i in range(10):
        x = random.randint(10, 90)
        y = random.randint(10, 90)
        r = random.randint(5, 30)
        colors = [color1, color2, "white", "#ff6b6b", "#4ecdc4", "#45b7d1"]
        shapes.append(f'<circle cx="{x}%" cy="{y}%" r="{r}" fill="{random.choice(colors)}" opacity="0.3"/>')
    
    # Get first few words of prompt
    words = prompt.split()[:3]
    text = ' '.join(words) if words else 'CHITRA'
    
    svg = f'''<svg width="512" height="512" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:{color1};stop-opacity:1" />
                <stop offset="100%" style="stop-color:{color2};stop-opacity:1" />
            </linearGradient>
        </defs>
        <rect width="100%" height="100%" fill="url(#grad)"/>
        {''.join(shapes)}
        <text x="50%" y="50%" font-family="Arial" font-size="32" fill="white" text-anchor="middle" dominant-baseline="central" font-weight="bold" stroke="rgba(0,0,0,0.2)" stroke-width="2">
            ✨ {text}
        </text>
        <text x="50%" y="70%" font-family="Arial" font-size="16" fill="rgba(255,255,255,0.6)" text-anchor="middle" dominant-baseline="central">
            CHITRA AI
        </text>
    </svg>'''
    
    svg_base64 = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{svg_base64}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
