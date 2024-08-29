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
global blood_test_results, liver_function_test_results, kidney_function_test_result, cholesterol_test_results
blood_test_results = {}
liver_function_test_results = {}
kidney_function_test_results = {}
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
    global blood_test_results, liver_function_test_results, kidney_function_test_result, cholesterol_test_results
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
            "haemoglobin": "Haemoglobin",
            "PCV": "Packed Cell Volume (PCV)",
            "RBC": " Red Blood Cell (RBC) count",
            "MCV": "Mean Corpuscular Volume (MCV)",
            "MCH": "Mean Corpuscular Hemoglobin (MCH)",
            "MCHC": "Mean Corpuscular Hemoglobin Concentration (MCHC)",
            "RDW": "Red Blood Cell Distribution Width (RDW)",
            "TLC": "Total Leukocyte Count (TLC)",
            "platelet": "Platelet Count",
            "neutrophils": "Neutrophils",
            "lymphocytes": "Lymphocytes",
            "eosinophils": "Eosinophils",
            "monocytes": "Monocytes",
            "basophils": "Basophils",
        },
        "liver": {
            "bilirubin_total": "Total Bilirubin",
            "bilirubin_direct": "Direct Bilirubin",
            "bilirubin_indirect": "Indirect Bilirubin",
            "ALT": "Alanine Aminotransferase (ALT)",
            "AST": "Aspartate Aminotransferase (AST)",
            "Alk": "Alkaline Phosphatase",
            "Protein": "Total Protein",
            "Albumin": "Albumin",
            "Globulin": "Globulin",
        },
        "kidney": {
            "creatinine": "Creatinine",
            "urea": "Urea",
            "blood_urea": "Blood Urea Nitrogen",
            "calcium": "Calcium",
            "phosphorus": "Phosphorus, Inorganic",
            "sodium": "Sodium",
            "potassium": "Potassium",
            "chloride": "Chloride",
        },
        "cholesterol": {
            "total_cholesterol": "Total Cholesterol",
            "hdl": "HDL Cholesterol",
            "ldl": "LDL Cholesterol",
            "triglycerides": "Triglycerides",
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
                kidney_function_test_results = extract_lab_results(
                    section_text, lab_tests["kidney"]
                )
            elif category == "cholesterol":
                cholesterol_test_results = extract_lab_results(
                    section_text, lab_tests["cholesterol"]
                )
    print(blood_test_results)
    print(liver_function_test_results)
    print(kidney_function_test_results)
    print(cholesterol_test_results)

    return jsonify({"summary": summary}), 200


@app.route('/charts-config')
def charts_config():
    charts_data = [
        # Blood Test Results (CBC)
        {
            'id': 'cbcChart',
            'type': 'bar',
            'label': 'CBC Results',
            'data': [11.2, 33.5, 3.85, 87.2, 29.2, 33.5, 15, 6810, 270000],
            'bgColor': 'rgba(54, 162, 235, 0.7)',
            'labels': ['Hemoglobin', 'PCV', 'RBC', 'MCV', 'MCH', 'MCHC', 'RDW', 'TLC', 'Platelets'],
            'yMin': 0,
            'yMax': 300000,
        },
        {
            'id': 'dlcChart',
            'type': 'bar',
            'label': 'DLC Percentages',
            'data': [58.6, 24.8, 6.6, 9.6, 0.4],
            'bgColor': ['rgba(255, 99, 132, 0.7)', 'rgba(54, 162, 235, 0.7)', 'rgba(75, 192, 192, 0.7)', 'rgba(255, 206, 86, 0.7)', 'rgba(153, 102, 255, 0.7)'],
            'labels': ['Neutrophils', 'Lymphocytes', 'Eosinophils', 'Monocytes', 'Basophils'],
            'yMin': 0,
            'yMax': 100,
        },
        {
            'id': 'nlrChart',
            'type': 'line',
            'label': 'NLR',
            'data': [2.36],
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
            'data': [0.55, 0.27, 0.28, 12.3, 21.5, 52.6, 5.96, 3.59, 2.37, 1.51],
            'bgColor': 'rgba(153, 102, 255, 0.7)',
            'labels': ['Total Bilirubin', 'Direct Bilirubin', 'Indirect Bilirubin', 'ALT', 'AST', 'Alkaline Phosphatase', 'Total Protein', 'Albumin', 'Globulin', 'A/G Ratio'],
            'yMin': 0,
            'yMax': 100,
        },
        {
            'id': 'lftRadarChart',
            'type': 'radar',
            'label': 'LFT Status',
            'data': [0.55, 0.27, 0.28, 12.3, 21.5, 52.6, 5.96, 3.59, 2.37, 1.51],
            'bgColor': 'rgba(255, 159, 64, 0.7)',
            'labels': ['Total Bilirubin', 'Direct Bilirubin', 'Indirect Bilirubin', 'ALT', 'AST', 'Alkaline Phosphatase', 'Total Protein', 'Albumin', 'Globulin', 'A/G Ratio'],
            'yMin': 0,
            'yMax': 100,
        },
        # Kidney Function Test (KFT) Results
        {
            'id': 'kftBarChart',
            'type': 'bar',
            'label': 'KFT Results',
            'data': [1.13, 44.1, 20.6, 0.74, 9.79, 3.76, 134, 4.7, 104],
            'bgColor': 'rgba(75, 192, 192, 0.7)',
            'labels': ['Creatinine', 'Urea', 'BUN', 'Uric Acid', 'Calcium', 'Phosphorus', 'Sodium', 'Potassium', 'Chloride'],
            'yMin': 0,
            'yMax': 150,
        },
        {
            'id': 'kftViolinChart',
            'type': 'line',  # Note: Actual Violin Plot is complex, use line chart for simplicity here.
            'label': 'KFT Distribution',
            'data': [1.13, 44.1, 20.6, 0.74, 9.79, 3.76, 134, 4.7, 104],
            'bgColor': 'rgba(54, 162, 235, 0.7)',
            'labels': ['Creatinine', 'Urea', 'BUN', 'Uric Acid', 'Calcium', 'Phosphorus', 'Sodium', 'Potassium', 'Chloride'],
            'yMin': 0,
            'yMax': 150,
        },
        # Cholesterol Test Results
        {
            'id': 'cholesterolPieChart',
            'type': 'pie',
            'label': 'Cholesterol Distribution',
            'data': [127, 48, 60.76, 18.74],
            'bgColor': ['rgba(255, 99, 132, 0.7)', 'rgba(54, 162, 235, 0.7)', 'rgba(255, 206, 86, 0.7)', 'rgba(153, 102, 255, 0.7)'],
            'labels': ['Total Cholesterol', 'HDL', 'LDL', 'VLDL'],
        },
        {
            'id': 'cholesterolBarChart',
            'type': 'bar',
            'label': 'Cholesterol Test Results',
            'data': [127, 94, 48, 80, 60.76, 18.74],
            'bgColor': 'rgba(153, 102, 255, 0.7)',
            'labels': ['Total Cholesterol', 'Triglycerides', 'HDL', 'Non-HDL', 'LDL', 'VLDL'],
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
    global blood_test_results, liver_function_test_results, kidney_function_test_result, cholesterol_test_results
    # Example data for each chart, typically you'd retrieve this from a database
    chart_data = {
        "cbcChart": {
            "labels": [
                "Hemoglobin",
                "PCV",
                "RBC",
                "MCV",
                "MCH",
                "MCHC",
                "RDW",
                "TLC",
                "Platelets",
            ],
            "data": [blood_test_results["haemoglobin"],blood_test_results["PCV"],blood_test_results["RBC"],blood_test_results["MCV"],blood_test_results["MCHC"],blood_test_results["RDW"],blood_test_results["TLC"],blood_test_results["platelet"]],
            "yMin": 0,
            "yMax": 300000,
        },
        "dlcChart": {
            "labels": [
                "Neutrophils",
                "Lymphocytes",
                "Eosinophils",
                "Monocytes",
                "Basophils",
            ],
            "data": [58.6, 24.8, 6.6, 9.6, 0.4],
            "yMin": 0,
            "yMax": 100,
        },
        "nlrChart": {"labels": ["NLR"], "data": [2.36], "yMin": 0, "yMax": 5},
        "lftBarChart": {
            "labels": [
                "Total Bilirubin",
                "Direct Bilirubin",
                "Indirect Bilirubin",
                "ALT",
                "AST",
                "Alkaline Phosphatase",
                "Total Protein",
                "Albumin",
                "Globulin",
                "A/G Ratio",
            ],
            "data": [0.55, 0.27, 0.28, 12.3, 21.5, 52.6, 5.96, 3.59, 2.37, 1.51],
            "yMin": 0,
            "yMax": 100,
        },
        "lftRadarChart": {
            "labels": [
                "Total Bilirubin",
                "Direct Bilirubin",
                "Indirect Bilirubin",
                "ALT",
                "AST",
                "Alkaline Phosphatase",
                "Total Protein",
                "Albumin",
                "Globulin",
                "A/G Ratio",
            ],
            "data": [0.55, 0.27, 0.28, 12.3, 21.5, 52.6, 5.96, 3.59, 2.37, 1.51],
            "yMin": 0,
            "yMax": 100,
        },
        "kftBarChart": {
            "labels": [
                "Creatinine",
                "Urea",
                "BUN",
                "Uric Acid",
                "Calcium",
                "Phosphorus",
                "Sodium",
                "Potassium",
                "Chloride",
            ],
            "data": [1.13, 44.1, 20.6, 0.74, 9.79, 3.76, 134, 4.7, 104],
            "yMin": 0,
            "yMax": 150,
        },
        "kftViolinChart": {
            "labels": [
                "Creatinine",
                "Urea",
                "BUN",
                "Uric Acid",
                "Calcium",
                "Phosphorus",
                "Sodium",
                "Potassium",
                "Chloride",
            ],
            "data": [1.13, 44.1, 20.6, 0.74, 9.79, 3.76, 134, 4.7, 104],
            "yMin": 0,
            "yMax": 150,
        },
        "cholesterolPieChart": {
            "labels": ["Total Cholesterol", "HDL", "LDL", "VLDL"],
            "data": [127, 48, 60.76, 18.74],
        },
        "cholesterolBarChart": {
            "labels": [
                "Total Cholesterol",
                "Triglycerides",
                "HDL",
                "Non-HDL",
                "LDL",
                "VLDL",
            ],
            "data": [127, 94, 48, 80, 60.76, 18.74],
            "yMin": 0,
            "yMax": 200,
        },
        "cholesterolLineChart": {
            "labels": ["Cholesterol/HDL Ratio", "Atherogenic Index"],
            "data": [2.67, 0.01],
            "yMin": 0,
            "yMax": 5,
        },
    }
    return jsonify(chart_data)


if __name__ == "__main__":
    app.run(debug=False)
