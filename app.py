from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
from model import Model
import os, re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config["UPLOAD_FOLDER"] = "./upload"
summaries_cache = {}
global uploaded_filename
uploaded_filename = None
global blood_test_results, liver_function_test_results
global cholesterol_test_results, kidney_test_results
blood_test_results = {}
kidney_test_results = {}
liver_function_test_results = {}
cholesterol_test_results = {}


@app.route("/")
def index():
    return render_template("index.html", title="My Flask Website with Images")


@app.route("/upload", methods=["POST"])
def upload_file():
    global uploaded_filename
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


@app.route("/summarize", methods=["POST"])
def summarize_pdf():
    global uploaded_filename
    global blood_test_results, liver_function_test_results
    global cholesterol_test_results, kidney_test_results
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
    }

    lab_tests = {
        "blood": {
        "haemoglobin": r"Haemoglobin",
        "PCV": r"Packed Cell Volume \(PCV\)",
        "RBC": r"Red Blood Cell \(RBC\) count",
        "MCV": r"Mean Corpuscular Volume \(MCV\)",
        "MCH": r"Mean Corpuscular Hemoglobin \(MCH\)",
        "MCHC": r"Mean Corpuscular Hemoglobin Concentration \(MCHC\)",
        "RDW": r"Red Blood Cell Distribution Width \(RDW\)",
        "TLC": r"Total Leukocyte Count \(TLC\)",
        "platelet": r"Platelet count",
        "neutrophils": r"Neutrophils",
        "lymphocytes": r"Lymphocytes",
        "eosinophils": r"Eosinophils",
        "monocytes": r"Monocytes",
        "basophils": r"Basophils",
        "nlr": r"Neutrophil lymphocyte ratio \(NLR\)"
        },
        "liver": {
            "bilirubin_total": r"Total Bilirubin",
            "bilirubin_direct": r"Bilirubin Conjugated \(Direct\)",
            "bilirubin_indirect": r"Bilirubin Indirect",
            "ALT": r"Alanine Aminotransferase \(ALT\)",
            "AST": r"Aspartate Aminotransferase \(AST\)",
            "Alk": r"Alkaline Phosphatase",
            "Protein": r"Total Protein",
            "Albumin": r"Albumin",
            "Globulin": r"Globulin",
        },
        "kidney": {
            "creatinine": r"Creatinine",
            "urea": r"Urea",
            "blood_urea": r"Blood Urea Nitrogen",
            "calcium": r"Calcium",
            "phosphorus": r"Phosphorus, Inorganic",
            "sodium": r"Sodium",
            "potassium": r"Potassium",
            "chloride": r"Chloride",
        },
        "cholesterol": {
            "total_cholesterol": r"Total Cholesterol",
            "hdl": r"HDL Cholesterol",
            "ldl": r"LDL Cholesterol",
            "triglycerides": r"Triglycerides",
        },
    }

    def extract_lab_results(section_text, lab_tests):
        results = {}
        number_pattern = re.compile(r"[\d\.]+")

        for key, test_name in lab_tests.items():
            pattern = re.compile(
                rf"{test_name}[:\s]*({number_pattern.pattern})", re.IGNORECASE
            )
            match = pattern.search(section_text)
            if match:
                value = match.group(1)
                results[key] = value.strip()
        return results

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

    return jsonify({"summary": summary}), 200


@app.route('/charts-config')
def charts_config():
    global blood_test_results, liver_function_test_results
    global cholesterol_test_results, kidney_test_results
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
            'data': [11.2, 12.5, blood_test_results["RBC"], blood_test_results["MCV"], blood_test_results["MCH"], blood_test_results["MCHC"], blood_test_results["TLC"]
],
            'bgColor': 'rgba(54, 162, 235, 0.7)',
            'labels': ["Haemoglobin", "PCV", "RBC", "MCV", "MCH", "MCHC", "TLC"],
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


if __name__ == "__main__":
    app.run(debug=False)
