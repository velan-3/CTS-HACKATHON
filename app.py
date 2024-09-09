from flask import Flask, redirect, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename
from model import Model
import os, re, shutil
from flask_cors import CORS
import pickle
import pandas as pd
import numpy as np
from pymongo import MongoClient


app = Flask(__name__)
CORS(app)
app.config["UPLOAD_FOLDER"] = "./upload"
global summaries_cache
summaries_cache = {}
global uploaded_filename
uploaded_filename = None
global blood_test_results, liver_function_test_results
global cholesterol_test_results, kidney_test_results
blood_test_results = {}
kidney_test_results = {}
liver_function_test_results = {}
cholesterol_test_results = {}
global gender,age
uri = "mongodb+srv://anupriyaravi2020:anu1803@cluster0.cl1fywz.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client['doctorDB']
doctor_collection = db['doctors']
admin_collection = db['admins']
try:
    client.admin.command('ping')
    print("MongoDB connected successfully.")
except Exception as e:
    print("Error connecting to MongoDB:", e)


    
@app.route("/")
def index():
    return render_template("login.html", title="Login Page")

@app.route("/home")
def home():
    return render_template("index.html",title = "Home Page")

@app.route('/logout')
def logout():
    # Redirect to login page
    return redirect(url_for('index'))

@app.route('/verify_id', methods=['POST'])
def verify_id():
    data = request.get_json()
    user_id = data.get('userId')
    user_type = data.get('userType')

    try:
        if user_type == 'doctor':
            # Check if doctor exists
            doctor = doctor_collection.find_one({"doctorId": user_id})

            if not doctor:
                return jsonify({"success": False, "message": "Doctor ID not found."}), 404
            return jsonify({"success": True, "name": doctor.get('doctorName')}), 200

        else:
            return jsonify({"success": False, "message": "Invalid user type."}), 400

    except Exception as e:
        print("Error during ID verification:", str(e))
        return jsonify({"success": False, "message": "Server error. Please try again later."}), 500

@app.route('/verify_password', methods=['POST'])
def verify_password():
    data = request.get_json()
    user_id = data.get('userId')
    password = data.get('password')
    user_type = data.get('userType')

    try:
        if user_type == 'doctor':
            # Verify doctor's password
            doctor = doctor_collection.find_one({"doctorId": user_id})

            if not doctor:
                return jsonify({"success": False, "message": "Doctor ID not found."}), 404

            if doctor.get('password') == password:
                print("Doctor password verified successfully")
                return jsonify({"success": True, "redirect_url": url_for('home')}), 200
            else:
                return jsonify({"success": False, "message": "Incorrect password."}), 401

        else:
            return jsonify({"success": False, "message": "Invalid user type."}), 400

    except Exception as e:
        print("Error during password verification:", str(e))
        return jsonify({"success": False, "message": "Server error. Please try again later."}), 500


@app.route("/upload", methods=["POST"])
def upload_file():
    global uploaded_filename
    global blood_test_results, liver_function_test_results
    global cholesterol_test_results, kidney_test_results
    global summaries_cache
    delete_all_files_in_folder("./upload")
    blood_test_results.clear
    kidney_test_results.clear
    liver_function_test_results.clear
    cholesterol_test_results.clear
    summaries_cache[uploaded_filename] = None
    uploaded_filename = None
    if "pdf" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["pdf"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith(".pdf"):

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
        uploaded_filename = filename
        return (
            jsonify({"message": "File uploaded successfully", "file_path": file_path}),
            200,
        )

    return jsonify({"error": "Invalid file type. Only PDFs are allowed."}), 400
def delete_all_files_in_folder(folder_path):
    # Use glob to get all files in the folder
    if os.path.exists(folder_path):
        # Remove all contents of the folder, including subdirectories
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Remove the directory and all its contents
            elif os.path.isfile(item_path):
                os.remove(item_path)  # Remove the file


@app.route("/summarize", methods=["POST"])
def summarize_pdf():
    global uploaded_filename
    global blood_test_results, liver_function_test_results
    global cholesterol_test_results, kidney_test_results
    global summaries_cache
    global gender,age
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
        "blood": re.compile(
            r"Blood Test Results:.*?(?=(?:Liver Function Test Results|Kidney Function Test Results|Cholesterol Test Results))",
            re.DOTALL,
        ),
        "liver": re.compile(
            r"Liver Function Test Results:.*?(?=(?:Kidney Function Test Results|Cholesterol Test Results))",
            re.DOTALL,
        ),
        "kidney": re.compile(
            r"Kidney Function Test Results:.*?(?=(?:Cholesterol Test Results))",
            re.DOTALL,
        ),
        "cholesterol": re.compile(r"Cholesterol Test Results:.*", re.DOTALL),
        "gender": re.compile(r"Gender[:\s]*(Male|Female|Other|M|F)", re.IGNORECASE),
        "age": re.compile(r"Age[:\s]*(\d+)", re.IGNORECASE),
    }

    lab_tests = {
        "blood": {
        "haemoglobin": [r"Hemoglobin", r"Haemoglobin"],
        "PCV": [r"Packed Cell Volume \(PCV\)", r"PCV",r"Hematocrit Value, Hct"r"Red Blood Cell \(RBC\) count"],
        "RBC": [r"RBC Count",r"Total RBC Count"],
        "MCV": [r"MCV",r"Mean Corpuscular Volume, MCV",r"Mean Corpuscular Volume \(MCV\)"],
        "MCH": [r"MCH",r"Mean Cell Haemoglobin, MCH",r"Mean Corpuscular Hemoglobin \(MCH\)"],
        "MCHC": [r"MCHC",r"Mean Cell Haemoglobin CON, MCHC",r"Mean Corpuscular Hemoglobin Concentration \(MCHC\)"],
        "RDW": [r"RDW",r"R.D.W. - CV",r"Red Cell Distribution Width \(RDW\)"],
        "platelet": [r"Platelet count"],
        "neutrophils": [r"Neutrophils"],
        "lymphocytes": [r"Lymphocytes"],
        "eosinophils": [r"Eosinophils"],
        "monocytes": [r"Monocytes"],
        "basophils": [r"Basophils"],
        "nlr": [r"Neutrophil lymphocyte ratio \(NLR\)"]
    },
    "liver": {
        "bilirubin_total": [r"Total Bilirubin",r"Serum Bilirubin \(Total\)"],
        "bilirubin_direct": [r"Bilirubin Conjugated \(Direct\)",r"Serum Bilirubin \(Direct\)",r"Bilirubin Direct"],
        "bilirubin_indirect": [r"Bilirubin Indirect",r"Serum Bilirubin \(Indirect\)"],
        "ALT": [r"ALT", r"Alanine Aminotransferase \(ALT\)",r"SGPT \(ALT\)"],
        "AST": [r"AST", r"Aspartate Aminotransferase \(AST\)",r"SGOT \(AST\)"],
        "Alk": [r"Alkaline Phosphatase",r"Serum Alkaline Phosphatase"],
        "Protein": [r"Total Protein",r"Serum Protein",r"Protein, Total"],
        "Albumin": [r"Albumin",r"Serum Albumin"],
        "Globulin": [r"Globulin"],
        "ag": [r"A/G Ratio"]
        },
        "kidney": {
        "creatinine": [r"Creatinine",r"Serum Creatinine"],
        "urea": [r"Urea",r"Serum Urea"],
        "blood_urea": [r"Blood Urea Nitrogen",r"BUN"],
        "calcium": [r"Calcium",r"Serum Calcium"],
        "phosphorus": [r"Phosphorus, Inorganic"],
        "sodium": [r"Sodium",r"Serum Sodium"],
        "potassium": [r"Potassium",r"Serum Potassium"],
        "chloride": [r"Chloride"],
    },
    "cholesterol": {
        "total_cholesterol": [r"Total Cholesterol"],
        "hdl": [r"HDL Cholesterol"],
        "ldl": [r"LDL Cholesterol"],
        "triglycerides": [r"Triglycerides"],
    },
        
    }

    def extract_lab_results(section_text, lab_tests):
        results = {}
        number_pattern = re.compile(r"[\d\.]+")

        for key, test_patterns in lab_tests.items():
            found = False
            for pattern in test_patterns:
                compiled_pattern = re.compile(
                    rf"{pattern}[:\s]*({number_pattern.pattern})", re.IGNORECASE
            )
                match = compiled_pattern.search(section_text)
                if match:
                    value = match.group(1)
                    try:
                    # Convert to float, if possible
                        results[key] = float(value.strip())
                    except ValueError:
                    # If conversion fails, store 0
                        results[key] = 0
                    found = True
                    break  # Stop checking other patterns for this key
        
            if not found:
            # If no pattern matched for this key
                results[key] = 0
        
        return results
    def extract_gender_age(text):
        gender = None
        age = None

        gender_match = patterns["gender"].search(text)
        if gender_match:
            gender = gender_match.group(1).strip()

        age_match = patterns["age"].search(text)
        if age_match:
            age = age_match.group(1).strip()

        return gender, age
    gender,age = extract_gender_age(text)
    for category, pattern in patterns.items():
        match = pattern.search(text)
        if match:
            section_text = match.group(0)
            if category == "blood":
                blood_test_results = extract_lab_results(
                    section_text, lab_tests["blood"]
                )
            elif category == "liver":
                liver_function_test_results = extract_lab_results(
                    section_text, lab_tests["liver"]
                )
            elif category == "kidney":
                kidney_test_results = extract_lab_results(
                    section_text, lab_tests["kidney"]
                )
            elif category == "cholesterol":
                cholesterol_test_results = extract_lab_results(
                    section_text, lab_tests["cholesterol"]
                )
    print(blood_test_results)
    print(liver_function_test_results)
    print(kidney_test_results)
    print(cholesterol_test_results)
    print(gender)
    print(age)

    return jsonify({"summary": summary}), 200


@app.route('/charts-config')
def charts_config():
    global blood_test_results, liver_function_test_results
    global cholesterol_test_results, kidney_test_results
    if not (blood_test_results and liver_function_test_results and cholesterol_test_results and kidney_test_results):
        return jsonify({'error': 'Test results are not available'}), 200
    print(blood_test_results)
    print(liver_function_test_results)
    print(kidney_test_results)
    print(cholesterol_test_results)
    charts_data = [
        # Blood Test Results (CBC)
        {
            'id': 'cbcChart',
            'type': 'bar',
            'label': 'CBC Results',
            'data': [blood_test_results["haemoglobin"], blood_test_results["MCV"], blood_test_results["MCH"], blood_test_results["MCHC"]],
            'bgColor': 'rgba(54, 162, 235, 0.7)',
            'labels': ["Haemoglobin", "MCV", "MCH", "MCHC"],
            'yMin': 0,
            'yMax': 100,
        },
        {
            'id': 'dlcChart',
            'type': 'bar',
            'label': 'DLC Percentages',
            'data': [blood_test_results["neutrophils"], blood_test_results["lymphocytes"], blood_test_results["eosinophils"], blood_test_results["monocytes"], blood_test_results["basophils"]],
            'bgColor': ['rgba(255, 99, 132, 0.7)', 'rgba(54, 162, 235, 0.7)', 'rgba(75, 192, 192, 0.7)', 'rgba(255, 206, 86, 0.7)', 'rgba(153, 102, 255, 0.7)'],
            'labels': ['Neutrophils', 'Lymphocytes', 'Eosinophils', 'Monocytes', 'Basophils'],
            'yMin': 0,
            'yMax': 100,
        },
        {
            'id': 'nlrChart',
            'type': 'line',
            'label': 'NLR',
            'data': [blood_test_results["nlr"]],
            'bgColor': 'rgba(255, 206, 86, 0.7)',
            'labels': ['NLR'],
            'yMin': 0,
            'yMax': 5,
        },
        # Liver Function Test (LFT) Results
        {
            'id': 'lftBarChart',
            'type': 'bar',
            'label': 'LFT Results',
            'data': [liver_function_test_results["bilirubin_total"], liver_function_test_results["bilirubin_direct"], liver_function_test_results["bilirubin_indirect"], liver_function_test_results["ALT"], liver_function_test_results["AST"], liver_function_test_results["Alk"],liver_function_test_results["Albumin"],liver_function_test_results["Globulin"] ],
            'bgColor': 'rgba(153, 102, 255, 0.7)',
            'labels': ['Total Bilirubin', 'Direct Bilirubin', 'Indirect Bilirubin', 'ALT', 'AST', 'Alkaline Phosphatase', 'Albumin', 'Globulin'],
            'yMin': 0,
            'yMax': 60,
        },
        {
            'id': 'lftRadarChart',
            'type': 'radar',
            'label': 'LFT Status',
            'data': [liver_function_test_results["bilirubin_total"], liver_function_test_results["bilirubin_direct"], liver_function_test_results["bilirubin_indirect"], liver_function_test_results["ALT"], liver_function_test_results["AST"], liver_function_test_results["Alk"],liver_function_test_results["Albumin"],liver_function_test_results["Globulin"] ],
            'bgColor': 'rgba(255, 159, 64, 0.7)',
            'labels': ['Total Bilirubin', 'Direct Bilirubin', 'Indirect Bilirubin', 'ALT', 'AST', 'Alkaline Phosphatase', 'Albumin', 'Globulin'],
            'yMin': 0,
            'yMax': 100,
        },
        # Kidney Function Test (KFT) Results
        {
            'id': 'kftBarChart',
            'type': 'bar',
            'label': 'KFT Results',
            'data': [kidney_test_results['creatinine'], kidney_test_results['urea'], kidney_test_results['blood_urea'], kidney_test_results['calcium'], kidney_test_results['phosphorus'], kidney_test_results['sodium'], kidney_test_results['potassium'], kidney_test_results['chloride'] ],
            'bgColor': 'rgba(75, 192, 192, 0.7)',
            'labels': ['Creatinine', 'Urea', 'BUN', 'Calcium', 'Phosphorus', 'Sodium', 'Potassium', 'Chloride'],
            'yMin': 0,
            'yMax': 150,
        },
        {
            'id': 'kftViolinChart',
            'type': 'line',  # Note: Actual Violin Plot is complex, use line chart for simplicity here.
            'label': 'KFT Distribution',
            'data': [kidney_test_results['creatinine'], kidney_test_results['urea'], kidney_test_results['blood_urea'], kidney_test_results['calcium'], kidney_test_results['phosphorus'], kidney_test_results['sodium'], kidney_test_results['potassium'], kidney_test_results['chloride']],
            'bgColor': 'rgba(54, 162, 235, 0.7)',
            'labels': ['Creatinine', 'Urea', 'BUN', 'Calcium', 'Phosphorus', 'Sodium', 'Potassium', 'Chloride'],
            'yMin': 0,
            'yMax': 150,
        },
        # Cholesterol Test Results
        {
            'id': 'cholesterolPieChart',
            'type': 'pie',
            'label': 'Cholesterol Distribution',
            'data': [cholesterol_test_results['total_cholesterol'], cholesterol_test_results['hdl'], cholesterol_test_results['ldl'], cholesterol_test_results['triglycerides'] ],
            'bgColor': ['rgba(255, 99, 132, 0.7)', 'rgba(54, 162, 235, 0.7)', 'rgba(255, 206, 86, 0.7)', 'rgba(153, 102, 255, 0.7)'],
            'labels': ['Total Cholesterol', 'HDL', 'LDL', 'Triglycerides'],
        },
        {
            'id': 'cholesterolBarChart',
            'type': 'bar',
            'label': 'Cholesterol Test Results',
            'data': [cholesterol_test_results['total_cholesterol'], cholesterol_test_results['hdl'], cholesterol_test_results['ldl'], cholesterol_test_results['triglycerides']],
            'bgColor': 'rgba(153, 102, 255, 0.7)',
            'labels': ['Total Cholesterol', 'HDL', 'LDL','Triglycerides'],
            'yMin': 0,
            'yMax': 200,
        },
        {
            'id': 'cholesterolLineChart',
            'type': 'line',
            'label': 'Cholesterol/HDL Ratio & Atherogenic Index',
            'data': [2.67, 0.01],
            'bgColor': 'rgba(255, 159, 64, 0.7)',
            'labels': ['Cholesterol/HDL Ratio', 'Atherogenic Index'],
            'yMin': 0,
            'yMax': 5,
        }
    ]
    return jsonify(charts_data)

@app.route('/process-query', methods=['POST'])
def process_query():
    global summaries_cache,uploaded_filename
    context = summaries_cache[uploaded_filename]
    data = request.json
    search_query = data.get('query', '')
    model = Model()
    response = model.Extraction(search_query,context)  
    # Placeholder response
    return jsonify({'result': response})

@app.route('/prediction')
def prediction():
    
    global blood_test_results, liver_function_test_results
    global cholesterol_test_results, kidney_test_results
    global gender,age
    if not (blood_test_results and liver_function_test_results and cholesterol_test_results and kidney_test_results):
        return jsonify({'error': 'Test results are not available'}), 200
    model_paths = {
    "anemia": "savedmodels/anemia_stacking_model.pkl",
    "cirrhosis": "savedmodels/cirrhosis_pipeline_model.pkl",
    "hepatitis": "savedmodels/hepatitis_stacking_model.pkl",
    "liver": "savedmodels/liver_stacking_model.pkl",
    "kidney": "savedmodels/kidney_disease_model.pkl",
}
    label_encoder_kidney = "savedmodels/label_encoders.pkl"
    with open(model_paths["anemia"], 'rb') as file:
        anemia_model = pickle.load(file)
    with open(model_paths["cirrhosis"], 'rb') as file:
        cirhossis_model = pickle.load(file)
    with open(model_paths["hepatitis"], 'rb') as file:
        hepatitis_model = pickle.load(file)
    with open(model_paths["liver"], 'rb') as file:
        liver_model = pickle.load(file)
    with open(model_paths["kidney"], 'rb') as file:
        kidney_model = pickle.load(file)
    with open(label_encoder_kidney, 'rb') as file:
        kidney_label_encoder = pickle.load(file)
    with open("savedmodels/stack.pkl", 'rb') as model_file:
        scaler = pickle.load(model_file)
        
    if gender=="Male" or gender=="M":
        gender_value = 1
    else:
        gender_value = 0    
        
    ##Predicting Anemia    
    def predict_anemia(input_data):
        input_data = np.array(input_data).reshape(1, -1)
        prediction = anemia_model.predict(input_data)
        return 'Anemia' if prediction[0] == 1 else 'No Anemia'
    anemia_data = [gender_value,blood_test_results['haemoglobin'],blood_test_results['MCH'],blood_test_results['MCHC'],blood_test_results['MCV']]
    anemia_disease = predict_anemia(anemia_data)
    print('anemia done')
    ##Predicting Kidney disease using anemia disease
    categorical_cols = ['anemia']  # List of categorical columns
    numerical_cols = ['age', 'albumin', 'blood urea', 'Creatinine', 'sodium', 'potassium', 'hemoglobin', 'wbc count', 'rbc count']
    def predict_kidney_disease(new_data):
    # Convert the input data to a DataFrame if it's not already one
        if isinstance(new_data, dict):
            new_data = pd.DataFrame([new_data])
    # Handle missing values
        new_data[numerical_cols] = new_data[numerical_cols].fillna(new_data[numerical_cols].median())
    # Fill and encode categorical variables
        for col in categorical_cols:
            if col in new_data:
                new_data[col] = new_data[col].fillna(new_data[col].mode().iloc[0])
                if col in kidney_label_encoder:
                    new_data[col] = new_data[col].apply(lambda x: kidney_label_encoder[col].transform([x])[0]
                                                    if x in kidney_label_encoder[col].classes_ else -1)
    # Ensure the order of columns matches the training data
    # Here you should match the columns with the training feature columns
        required_columns = numerical_cols + categorical_cols
        new_data = new_data[required_columns]
    # Make a prediction using the trained model
        prediction = kidney_model.predict(new_data)
    # If 'classification' is a categorical feature and encoded, you may need to decode
        if 'classification' in kidney_label_encoder:
            predicted_class = kidney_label_encoder['classification'].inverse_transform(prediction)
            return predicted_class[0]
        else:
            return prediction[0]
    anemia_value = 'no' if anemia_disease == "No Anemia" else 'yes'
    kidney_data = {
    'age': int(age),
    'albumin': liver_function_test_results['Albumin'],
    'blood urea': kidney_test_results['blood_urea'],
    'Creatinine': kidney_test_results['creatinine'],
    'sodium': kidney_test_results['sodium'],
    'potassium': kidney_test_results['potassium'],
    'hemoglobin': blood_test_results['haemoglobin'],
    'wbc count': blood_test_results['neutrophils']+blood_test_results['lymphocytes']+blood_test_results['eosinophils']+blood_test_results['basophils']+blood_test_results['monocytes'],
    'rbc count': blood_test_results['RBC'],
    'anemia': anemia_value
}
    kidney_disease = predict_kidney_disease(kidney_data)
    print('kidney done')
    ##Predicting hepatitis
    def predict_hepatitis_disease(input_data):
    # Convert input data to a numpy array and reshape for prediction
        input_data = np.array(input_data).reshape(1, -1)
    
    # Predict using the trained stacking model
        prediction = hepatitis_model.predict(input_data)
    
    # Map the prediction to the corresponding disease status
        disease_map = {
        0: 'No Disease',
        1: 'Hepatitis',
        2: 'Fibrosis',
        3: 'Cirrhosis',
        4: 'Blood Donor'
    }
    
    # Return the predicted disease status
        return disease_map.get(prediction[0], 'Unknown')
    hepatitis_data = [int(age), gender_value, liver_function_test_results['Alk'], liver_function_test_results['ALT'], liver_function_test_results['AST'],kidney_test_results['creatinine']]
    hepatitis_disease = predict_hepatitis_disease(hepatitis_data)
    print('Hepatitis done')
    ##Predicting cirrhosis
    hepatitis_value = 1 if anemia_disease == "Hepatitis" else 0
    new_data = pd.DataFrame({
    'Age': [int(age)],
    'Gender': [gender_value],  # 0 for male, 1 for female
    'Hepatitis_C_infection': [hepatitis_value],  # 0 for negative, 1 for positive
    'Total Bilirubin(mg/dl)': [liver_function_test_results['bilirubin_total']],
    'Direct(mg/dl)': [liver_function_test_results['bilirubin_direct']],
    'Indirect(mg/dl)': [liver_function_test_results['bilirubin_indirect']],
    'Albumin(g/dl)': [liver_function_test_results['Albumin']],
    'Globulin(g/dl)': [liver_function_test_results['Globulin']],
    'A/G Ratio': [liver_function_test_results['ag']],
    'AL.Phosphatase(U/L)': [liver_function_test_results['Alk']],
    'SGOT/AST(U/L)': [liver_function_test_results['AST']],
    'SGPT/ALT(U/L)': [liver_function_test_results['ALT']]
})
    def predict_cirrhosis(input_data):
        input_data = np.array(input_data).reshape(1, -1)
        prediction = cirhossis_model.predict(input_data)
        return 'YES' if prediction[0] == 1 else 'NO'
    cirhossis_disease = predict_cirrhosis(new_data)
    print('cirrhosis done')
    ##Predicting LiverDisease
    def predict_liver_disease(input_data):
    # Convert input data to a numpy array
        input_data = np.array(input_data).reshape(1, -1)
    # Standardize the input data
        input_data = scaler.transform(input_data)
    # Predict using the stacking model
        prediction = liver_model.predict(input_data)
    # Return the prediction
        return 'Liver Disease' if prediction[0] == 1 else 'No Liver Disease'
    
    liver_data = [int(age), gender_value, liver_function_test_results['bilirubin_total'], liver_function_test_results['bilirubin_direct'], liver_function_test_results['Alk'], liver_function_test_results['ALT'], liver_function_test_results['AST'], liver_function_test_results['Protein'], liver_function_test_results['Albumin'], liver_function_test_results['ag']]  # Example values; should be set dynamically
    liver_disease = predict_liver_disease(liver_data)
    print('liver done')
    print(liver_disease)
    print(anemia_disease)
    print(hepatitis_disease)
    print(cirhossis_disease)
    print(kidney_disease)
    prediction_details = []
    if anemia_disease=="Anemia":
        if gender_value ==1:
            prediction_details.append({
            "organ": "Blood",
            "disease": "Anemia",
            "image": "static/images/male-liver.png",
            "description": "Anemia is a condition in which you lack enough healthy red blood cells to carry adequate oxygen to your body's tissues."
        })
        else:
            prediction_details.append({
            "organ": "Blood",
            "disease": "Anemia",
            "image": "static/images/female-liver.png",
            "description": "Anemia is a condition in which you lack enough healthy red blood cells to carry adequate oxygen to your body's tissues."
        })
    if hepatitis_disease == "Hepatitis":
        if gender_value==1:
            prediction_details.append({
            "organ": "Liver",
            "disease": "Hepatitis",
            "image": "static/images/male-citrhosis.png",
            "description": "Hepatitis is an inflammation of the liver, commonly caused by a viral infection."
        })
        else:
            prediction_details.append({
            "organ": "Liver",
            "disease": "Hepatitis",
            "image": "static/images/female-citrhosis.png",
            "description": "Hepatitis is an inflammation of the liver, commonly caused by a viral infection."
        })
    if cirhossis_disease=="YES":
        if gender_value==1:
            prediction_details.append({
            "organ": "Liver",
            "disease": "Cirrhosis",
            "image": "static/images/male-citrhosis.png",
            "description": "Cirrhosis is a late stage of scarring (fibrosis) of the liver caused by many forms of liver diseases and conditions."
        })
        else:
            prediction_details.append({
            "organ": "Liver",
            "disease": "Cirrhosis",
            "image": "static/images/female-citrhosis.png",
            "description": "Cirrhosis is a late stage of scarring (fibrosis) of the liver caused by many forms of liver diseases and conditions."
        })
    if kidney_disease=="ckd":
        if gender_value==1:
            prediction_details.append({
            "organ": "Kidney",
            "disease": "Chronic Kidney Disease",
            "image": "static/images/male-kidney.png",
            "description": "Chronic kidney disease (CKD) is a long-term condition where the kidneys don't work as well as they should."
        })
        else:
            prediction_details.append({
            "organ": "Kidney",
            "disease": "Chronic Kidney Disease",
            "image": "static/images/female-kidney.png",
            "description": "Chronic kidney disease (CKD) is a long-term condition where the kidneys don't work as well as they should."
        })
    if liver_disease=="Liver Disease":
        if gender_value==1:
            prediction_details.append({
            "organ": "Liver",
            "disease": "Liver Disease",
            "image": "static/images/male-liver.png",
            "description": "Liver disease refers to any condition that impairs the liver's ability to function properly."
        })
        else:
            prediction_details.append({
            "organ": "Liver",
            "disease": "Liver Disease",
            "image": "static/images/female-liver.png",
            "description": "Liver disease refers to any condition that impairs the liver's ability to function properly."
        })
    return jsonify(prediction_details), 200

@app.route('/consultation')
def consultation():
    global blood_test_results, liver_function_test_results
    global cholesterol_test_results, kidney_test_results
    global summaries_cache,uploaded_filename
    if not (blood_test_results and liver_function_test_results and cholesterol_test_results and kidney_test_results):
        return jsonify({'error': 'Test results are not available'}), 200
    model = Model()
    data = model.Consultation(summaries_cache[uploaded_filename])
    return jsonify(data),200

if __name__ == "__main__":
    app.run(debug=False)
