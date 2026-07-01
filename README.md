# 🧫 Diagnostic Lab Assistant

An interactive **Streamlit web app** for interpreting **antibiotic susceptibility tests (AST)** and analyzing microbiology plate data.  
The app automates **EUCAST breakpoint interpretation**, supports **OCR** for lab result sheets, and reduces human error during reading and reporting.

🌐 **Live app:** [https://bact-app.streamlit.app](https://bact-app.streamlit.app)  
💾 **Repository:** [github.com/MartinGalea17/bact_app](https://github.com/MartinGalea17/bact_app)

---

## 🚀 Features
- Interpret **MIC** and **disc diffusion** results using EUCAST 2024 breakpoints  
- Automatic **fuzzy name matching** to handle typos or partial bacterial names  
- Built-in antibiotic panels for **Gram-positive** and **Gram-negative** organisms  
- **Plotly** charts for visualization  
- Secure **bcrypt-based** admin and user authentication  


---

## 🧩 Tech Stack
- **Frontend:** Streamlit  
- **Data:** Pandas, OpenPyXL, JSON  
- **OCR:** EasyOCR, PyTesseract, OpenCV, Torch  
- **Auth:** Bcrypt  
- **Visualization:** Plotly  

---

## ⚙️ Run Locally
Clone the repository and install dependencies:

```bash
git clone https://github.com/MartinGalea17/bact_app.git
cd bact_app
pip install -r requirements.txt

📜 License

MIT License © 2025 Martin Galea
