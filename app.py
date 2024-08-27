from flask import Flask, render_template, request, jsonify, send_file,session
from werkzeug.utils import secure_filename
from model import Model
import os,re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = './upload' 
summaries_cache = {}
global uploaded_filename
uploaded_filename = None
blood_test_results = {}
liver_function_test_results = {}
kidney_function_test_results = {}
cholesterol_test_results = {}


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
        summaries_cache[uploaded_filename] = summary  
        print(summary) 
        
    text = summary   
    patterns = {
    'blood': re.compile(r'Blood Test Results:.*?(?=(?:Liver Function Test Results|Kidney Function Test Results|Cholesterol Test Results))', re.DOTALL),
    'liver': re.compile(r'Liver Function Test Results:.*?(?=(?:Kidney Function Test Results|Cholesterol Test Results))', re.DOTALL),
    'kidney': re.compile(r'Kidney Function Test Results:.*?(?=(?:Cholesterol Test Results))', re.DOTALL),
    'cholesterol': re.compile(r'Cholesterol Test Results:.*', re.DOTALL)
    }
    
    lab_tests = {
    'blood': {
        'haemoglobin': 'Haemoglobin',
        'PCV': 'Packed Cell Volume (PCV)',
        'RBC': ' Red Blood Cell (RBC) count',
        'MCV': 'Mean Corpuscular Volume (MCV)',
        'MCH': 'Mean Corpuscular Hemoglobin (MCH)',
        'MCHC': 'Mean Corpuscular Hemoglobin Concentration (MCHC)',
        'RDW': 'Red Blood Cell Distribution Width (RDW)',
        'TLC': 'Total Leukocyte Count (TLC)',
        'platelet': 'Platelet Count',
        'neutrophils': 'Neutrophils',
        'lymphocytes': 'Lymphocytes',
        'eosinophils': 'Eosinophils',
        'monocytes': 'Monocytes',
        'basophils': 'Basophils',
    },
    'liver': {
        'bilirubin_total': 'Total Bilirubin',
        'bilirubin_direct': 'Direct Bilirubin',
        'bilirubin_indirect': 'Indirect Bilirubin',
        'ALT': 'Alanine Aminotransferase (ALT)',
        'AST': 'Aspartate Aminotransferase (AST)',
        'Alk': 'Alkaline Phosphatase',
        'Protein': 'Total Protein',
        'Albumin': 'Albumin',
        'Globulin': 'Globulin',
    },'kidney': {
        'creatinine': 'Creatinine',
        'urea': 'Urea',
        'blood_urea': 'Blood Urea Nitrogen',
        'calcium': 'Calcium',
        'phosphorus': 'Phosphorus, Inorganic',
        'sodium': 'Sodium',
        'potassium': 'Potassium',
        'chloride': 'Chloride'
    },
    'cholesterol': {
        'total_cholesterol': 'Total Cholesterol',
        'hdl': 'HDL Cholesterol',
        'ldl': 'LDL Cholesterol',
        'triglycerides': 'Triglycerides',
    }
    }
    def extract_lab_results(section_text, lab_tests):
        results = {}
        number_pattern = re.compile(r'[\d\.]+')  
    
        for key, test_name in lab_tests.items():
            pattern = re.compile(rf'{test_name}[:\s]*({number_pattern.pattern})', re.IGNORECASE)
            match = pattern.search(section_text)
            if match:
                value = match.group(1)
                results[key] = value.strip()
        return results
    for category, pattern in patterns.items():
        match = pattern.search(text)
        if match:
            section_text = match.group(0)
            if category == 'blood':
                blood_test_results = extract_lab_results(section_text, lab_tests['blood'])
            elif category == 'liver':
                liver_function_test_results = extract_lab_results(section_text, lab_tests['liver'])
            elif category == 'kidney':
                kidney_function_test_results = extract_lab_results(section_text, lab_tests['kidney'])
            elif category == 'cholesterol':
                cholesterol_test_results = extract_lab_results(section_text, lab_tests['cholesterol'])
    print(blood_test_results)
    print(liver_function_test_results)
    print(kidney_function_test_results)
    print(cholesterol_test_results)

    return jsonify({'summary': summary}), 200

if __name__ == '__main__':
    app.run(debug=False)
