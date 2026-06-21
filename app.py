from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import google.generativeai as genai
import base64
import random
import json
from datetime import datetime

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Configure Gemini with error handling
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
model = None

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Use a simpler model name that's guaranteed to work
        model = genai.GenerativeModel('gemini-3.1-flash')
        print("Gemini configured successfully!")
    except Exception as e:
        print(f"Error configuring Gemini: {e}")
        model = None
else:
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
            try:
                response = model.generate_content(
                    f"Generate a creative and artistic image based on this description: {prompt}. " +
                    "Make it visually stunning with vibrant colors and interesting composition.",
                    generation_config={
                        "temperature": 0.9,
                        "top_p": 0.95,
                        "top_k": 40,
                        "max_output_tokens": 2048,
                    }
                )
                
                # Extract image data
                image_data = None
                if hasattr(response, '_result') and response._result.candidates:
                    parts = response._result.candidates[0].content.parts
                    for part in parts:
                        if hasattr(part, 'data'):
                            image_data = part.data
                            break
                        elif hasattr(part, 'text') and part.text:
                            # Try to parse as base64
                            text = part.text.strip()
                            try:
                                # Check if it looks like base64
                                base64.b64decode(text[:100])
                                image_data = base64.b64decode(text)
                                break
                            except:
                                pass
                
                if image_data and isinstance(image_data, bytes):
                    img_base64 = base64.b64encode(image_data).decode('utf-8')
                    data_url = f"data:image/png;base64,{img_base64}"
                else:
                    data_url = generate_svg_placeholder(prompt)
            except Exception as e:
                print(f"Gemini generation error: {e}")
                data_url = generate_svg_placeholder(prompt)
        else:
            data_url = generate_svg_placeholder(prompt)
        
        return jsonify({
            'image': data_url,
            'prompt': prompt,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            'image': generate_svg_placeholder(prompt),
            'prompt': prompt,
            'error': str(e)
        })

def generate_svg_placeholder(prompt):
    """Generate a simple SVG placeholder without requiring external libraries"""
    # Create a deterministic color based on prompt
    hash_val = sum(ord(c) for c in prompt) % 360
    color1 = f"hsl({hash_val}, 70%, 55%)"
    color2 = f"hsl({(hash_val + 60) % 360}, 70%, 45%)"
    
    # Generate random shapes
    shapes = []
    for i in range(15):
        x = random.randint(10, 90)
        y = random.randint(10, 90)
        r = random.randint(5, 35)
        colors = [color1, color2, "#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4", "#ffd93d"]
        shapes.append(f'<circle cx="{x}%" cy="{y}%" r="{r}" fill="{random.choice(colors)}" opacity="0.4"/>')
    
    # Add some rectangles
    for i in range(5):
        x = random.randint(10, 80)
        y = random.randint(10, 80)
        w = random.randint(10, 40)
        h = random.randint(10, 40)
        colors = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4"]
        shapes.append(f'<rect x="{x}%" y="{y}%" width="{w}%" height="{h}%" fill="{random.choice(colors)}" opacity="0.3" rx="5"/>')
    
    # Get first few words of prompt
    words = prompt.split()[:3]
    text = ' '.join(words) if words else 'CHITRA'
    
    svg = f'''<svg width="512" height="512" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:{color1};stop-opacity:1" />
                <stop offset="100%" style="stop-color:{color2};stop-opacity:1" />
            </linearGradient>
            <radialGradient id="glow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" style="stop-color:rgba(255,255,255,0.3)" />
                <stop offset="100%" style="stop-color:rgba(255,255,255,0)" />
            </radialGradient>
        </defs>
        <rect width="100%" height="100%" fill="url(#grad)"/>
        <rect width="100%" height="100%" fill="url(#glow)"/>
        {''.join(shapes)}
        <text x="50%" y="42%" font-family="Arial, sans-serif" font-size="36" fill="white" text-anchor="middle" dominant-baseline="central" font-weight="bold" stroke="rgba(0,0,0,0.3)" stroke-width="3">
            ✨ {text}
        </text>
        <text x="50%" y="55%" font-family="Arial, sans-serif" font-size="18" fill="rgba(255,255,255,0.8)" text-anchor="middle" dominant-baseline="central">
            CHITRA AI
        </text>
        <text x="50%" y="65%" font-family="Arial, sans-serif" font-size="12" fill="rgba(255,255,255,0.5)" text-anchor="middle" dominant-baseline="central">
            Generated by AI
        </text>
    </svg>'''
    
    svg_base64 = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{svg_base64}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
