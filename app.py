from flask import Flask, render_template, request, jsonify, send_file,session
from werkzeug.utils import secure_filename
from model import Model
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = './upload' 
summaries_cache = {}
global uploaded_filename
uploaded_filename = None


@app.route('/')
def index():
    return render_template('index.html', title="My Flask Website with Images")


@app.route('/upload', methods=['POST'])
def upload_file():
    global uploaded_filename 
    if 'pdf' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['pdf']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and file.filename.endswith('.pdf'):
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        uploaded_filename = filename
        #fname.append(filename)
        # Here you can process the file if needed and then return a response
        return jsonify({'message': 'File uploaded successfully', 'file_path': file_path}), 200
    
    return jsonify({'error': 'Invalid file type. Only PDFs are allowed.'}), 400

@app.route('/summarize', methods=['POST'])
def summarize_pdf():
    global uploaded_filename
    if uploaded_filename in summaries_cache:
        print("Returning cached summary")
        summary = summaries_cache[uploaded_filename]
        print(summary)
    else:
        print(uploaded_filename)
        model = Model()
        print("model executed")
        model.pdfprocessing(uploaded_filename)
        print("pdfprocessing done")
        model.summarization()
        print("summarization done")
        summary = model.run_retrieval() 
        summaries_cache[uploaded_filename] = summary  # Cache the summary
        print(summary)  # This will run the retrieval chain and summarize the PDF
    return jsonify({'summary': summary}), 200

if __name__ == '__main__':
    app.run(debug=False)
