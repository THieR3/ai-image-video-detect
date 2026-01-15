from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import torch
import cv2
import random
import os
from PIL import Image
from transformers import AutoImageProcessor, SiglipForImageClassification

# Création de l'application Flask et activation de CORS
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Chargement intelligent du modèle
MODEL_ID = "Ateeqq/ai-vs-human-image-detector"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("Chargement de l'IA...")
try:
    processor = AutoImageProcessor.from_pretrained(MODEL_ID)
    model = SiglipForImageClassification.from_pretrained(MODEL_ID).to(device)
    model.eval()
    print("✅ Prêt !")
except Exception as e:
    print(f"❌ Erreur : {e}")
@app.route('/')
def home():
    # Flask va chercher dans le dossier /templates/ automatiquement
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def handle_prediction():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    
    file = request.files['file']
    path = f"temp_{file.filename}"
    file.save(path)

    try:
        # Détection Vidéo ou Image
        if file.filename.lower().endswith(('.mp4', '.mov', '.avi')):
            cap = cv2.VideoCapture(path)
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            # On analyse 2% de la vidéo
            frames_to_check = random.sample(range(total), max(1, int(total*0.02)))
            scores = []
            for f in frames_to_check:
                cap.set(cv2.CAP_PROP_POS_FRAMES, f)
                ret, frame = cap.read()
                if not ret: continue
                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                inputs = processor(images=img, return_tensors="pt").to(device)
                with torch.no_grad():
                    out = model(**inputs)
                    scores.append(float(torch.softmax(out.logits, dim=-1)[0, 0]))
            cap.release()
            avg = sum(scores)/len(scores) if scores else 0
            res = {"verdict": "AI" if avg > 0.5 else "HUMAN", "confidence": avg if avg > 0.5 else 1-avg}
        else:
            # Image simple
            img = Image.open(path).convert("RGB")
            inputs = processor(images=img, return_tensors="pt").to(device)
            with torch.no_grad():
                out = model(**inputs)
                probs = torch.softmax(out.logits, dim=-1)
                idx = out.logits.argmax(-1).item()
                res = {"verdict": model.config.id2label[idx].upper(), "confidence": float(probs[0, idx])}
        
        os.remove(path)
        return jsonify(res)
    except Exception as e:
        if os.path.exists(path): os.remove(path)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)