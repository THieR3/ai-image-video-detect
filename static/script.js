let credits = localStorage.getItem('ai_credits') || 100;
let isSub = localStorage.getItem('is_sub') === 'true';
let fileToUpload = null;

const analyzeBtn = document.getElementById('analyze-btn');
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const creditDisplay = document.getElementById('credit-count');

creditDisplay.innerText = isSub ? "∞" : credits;

dropZone.onclick = () => fileInput.click();

fileInput.onchange = (e) => {
    if (e.target.files[0]) {
        fileToUpload = e.target.files[0];
        document.getElementById('selected-file-name').innerText = fileToUpload.name;
        analyzeBtn.disabled = false;
    }
};

function closeM() { document.getElementById('modal').classList.add('hidden'); }
function buy() { localStorage.setItem('is_sub', 'true'); location.reload(); }

analyzeBtn.onclick = async () => {
    if (credits <= 0 && !isSub) {
        document.getElementById('modal').classList.remove('hidden');
        return;
    }

    analyzeBtn.innerText = "Analyse en cours...";
    analyzeBtn.disabled = true;

    const fd = new FormData();
    fd.append('file', fileToUpload);

    try {
        const res = await fetch('/analyze', { method: 'POST', body: fd });        const data = await res.json();

        // Affichage résultats
        const box = document.getElementById('result-box');
        box.classList.remove('hidden');
        document.getElementById('res-verdict').innerText = data.verdict === 'AI' ? "⚠️ CONTENU GÉNÉRÉ PAR IA" : "✅ CONTENU HUMAIN";
        document.getElementById('res-verdict').style.color = data.verdict === 'AI' ? "#e11d48" : "#10b981";
        document.getElementById('res-conf').innerText = (data.confidence * 100).toFixed(2) + "%";

        if (!isSub) {
            credits--;
            localStorage.setItem('ai_credits', credits);
            creditDisplay.innerText = credits;
        }
    } catch (err) {
        alert("Erreur de connexion au serveur Python.");
    } finally {
        analyzeBtn.innerText = "Detect AI Content Now";
        analyzeBtn.disabled = false;
    }
};