from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import google.generativeai as genai
from PIL import Image
import io
import base64

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Configure Gemini
# IMPORTANT: Set your API key as environment variable GEMINI_API_KEY
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')  # or gemini-2.0-flash-exp
else:
    model = None
    print("WARNING: GEMINI_API_KEY not set. Using fallback mode.")

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/style.css')
def serve_css():
    return send_from_directory('.', 'style.css')

@app.route('/script.js')
def serve_js():
    return send_from_directory('.', 'script.js')

@app.route('/generate', methods=['POST'])
def generate_image():
    """Generate image from prompt using Gemini"""
    data = request.json
    prompt = data.get('prompt', '').strip()
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    if not model:
        # Fallback: return a placeholder image
        return jsonify({
            'image': generate_fallback_image(prompt),
            'prompt': prompt
        })
    
    try:
        # Generate image using Gemini
        response = model.generate_content(
            f"Generate an image based on this description: {prompt}",
            generation_config=genai.types.GenerationConfig(
                temperature=0.8,
                top_p=0.95,
                top_k=40,
                max_output_tokens=2048,
            )
        )
        
        # Extract image from response
        if hasattr(response, '_result') and response._result.candidates:
            # Handle response format
            image_data = response._result.candidates[0].content.parts[0].data
        elif hasattr(response, 'candidates') and response.candidates:
            image_data = response.candidates[0].content.parts[0].data
        else:
            # Try alternative extraction
            image_data = response.text
        
        # Convert to base64
        if isinstance(image_data, bytes):
            img_base64 = base64.b64encode(image_data).decode('utf-8')
            data_url = f"data:image/png;base64,{img_base64}"
        else:
            # If text response, generate fallback
            data_url = generate_fallback_image(prompt)
        
        return jsonify({
            'image': data_url,
            'prompt': prompt
        })
        
    except Exception as e:
        print(f"Error generating image: {e}")
        # Fallback to placeholder
        return jsonify({
            'image': generate_fallback_image(prompt),
            'prompt': prompt
        })

def generate_fallback_image(prompt):
    """Generate a fallback image using PIL (for demo without API key)"""
    from PIL import Image, ImageDraw, ImageFont
    import random
    
    # Create a colorful image
    img = Image.new('RGB', (512, 512), color=(240, 240, 255))
    draw = ImageDraw.Draw(img)
    
    # Random colors based on prompt
    random.seed(hash(prompt) % 100000)
    colors = [
        (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
        for _ in range(5)
    ]
    
    # Draw random shapes
    for _ in range(20):
        x = random.randint(0, 512)
        y = random.randint(0, 512)
        r = random.randint(20, 100)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=colors[random.randint(0, len(colors)-1)], outline=None)
    
    # Add text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 30)
    except:
        font = ImageFont.load_default()
    
    words = prompt.split()[:3]
    text = '✨ ' + ' '.join(words) if words else '✨ CHITRA'
    draw.text((256, 256), text, fill=(255, 255, 255), anchor="mm", font=font, stroke_width=2, stroke_fill=(0,0,0))
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_base64}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
