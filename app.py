from flask import Flask, request, jsonify, send_file
import periodictable
import re
from pydub import AudioSegment
from pydub.generators import Sine
import io

app = Flask(__name__)

# Generate element sound based on atomic number
def generate_element_sound(element_name, duration=1000):
    element = getattr(periodictable, element_name.capitalize(), None)
    if element is not None:
        frequency = element.number * 50  # Less shrill sound
        sound = Sine(frequency).to_audio_segment(duration=duration)
        sound = sound + 10  # Increase volume
        sound = sound.fade_in(300).fade_out(300)
        return sound
    return None

# Parse molecular formula
def parse_molecule(molecule):
    element_pattern = r'([A-Z][a-z]*)(\d*)'
    elements = re.findall(element_pattern, molecule)
    molecule_dict = {}
    for (element, quantity) in elements:
        if quantity == "":
            quantity = 1
        else:
            quantity = int(quantity)
        molecule_dict[element] = molecule_dict.get(element, 0) + quantity
    return molecule_dict

# Generate sound for molecule
def generate_molecule_sound(molecule):
    element_sounds = []
    molecule_dict = parse_molecule(molecule)
    
    for element, quantity in molecule_dict.items():
        sound = generate_element_sound(element)
        if sound:
            for _ in range(quantity):
                element_sounds.append(sound)
    
    if element_sounds:
        combined_sound = sum(element_sounds)
        return combined_sound
    return None

# API endpoint to generate sound
@app.route('/generate-sound', methods=['POST'])
def generate_sound():
    data = request.json
    molecule = data.get('molecule', 'H2O')  # Default to H2O if no molecule is provided
    sound = generate_molecule_sound(molecule)
    
    if sound:
        # Save sound to bytes and send it back
        buffer = io.BytesIO()
        sound.export(buffer, format="wav")
        buffer.seek(0)
        return send_file(buffer, mimetype="audio/wav")
    
    return jsonify({'error': 'Unable to generate sound for the molecule'}), 400

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template

app = Flask(__name__)

# Define a route for the home page
@app.route('/')
def home():
    return render_template('index.html')  # This will serve the index.html file

# Other routes and functions go here...

if __name__ == "__main__":
    app.run(debug=True)


