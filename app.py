from flask import Flask, request, render_template_string
import joblib
import pandas as pd
import csv
import os

app = Flask(__name__)

# Load trained model
model = joblib.load("models/flood_model.pkl")

# Rainfall data (sample values)
rainfall_data = {
    "Thiruvananthapuram":120,
    "Kollam":140,
    "Pathanamthitta":200,
    "Alappuzha":180,
    "Kottayam":220,
    "Idukki":250,
    "Ernakulam":210,
    "Thrissur":190,
    "Palakkad":150,
    "Malappuram":240,
    "Kozhikode":260,
    "Wayanad":300,
    "Kannur":230,
    "Kasaragod":170
}

html = """
<!DOCTYPE html>
<html>
<head>

<title>Flood Prediction System</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>

body{
    margin:0;
    padding:0;
    font-family:Arial,sans-serif;
    background:linear-gradient(to right,#2193b0,#6dd5ed);
}

.container{
    width:450px;
    margin:30px auto;
    background:white;
    padding:25px;
    border-radius:15px;
    box-shadow:0 0 20px gray;
}

h1{
    text-align:center;
    color:#0b5394;
}

label{
    font-weight:bold;
}

input,select{
    width:100%;
    padding:10px;
    margin-top:5px;
    margin-bottom:15px;
    border-radius:5px;
    border:1px solid #ccc;
    box-sizing:border-box;
}

button{
    width:100%;
    padding:12px;
    background:#007BFF;
    color:white;
    border:none;
    border-radius:5px;
    font-size:17px;
    cursor:pointer;
}

button:hover{
    background:#0056b3;
}

.result{
    margin-top:20px;
    background:#eef8ee;
    padding:15px;
    border-radius:10px;
    text-align:center;
}

canvas{
    margin-top:20px;
}

table{
    width:100%;
    border-collapse:collapse;
    margin-top:20px;
}

table,th,td{
    border:1px solid #ccc;
}

th,td{
    padding:8px;
    text-align:center;
}

</style>

</head>

<body>

<div class="container">

<h1>🌊 Flood Prediction System</h1>

<form method="POST">

<label>District</label>

<select name="District" required>

<option>Thiruvananthapuram</option>
<option>Kollam</option>
<option>Pathanamthitta</option>
<option>Alappuzha</option>
<option>Kottayam</option>
<option>Idukki</option>
<option>Ernakulam</option>
<option>Thrissur</option>
<option>Palakkad</option>
<option>Malappuram</option>
<option>Kozhikode</option>
<option>Wayanad</option>
<option>Kannur</option>
<option>Kasaragod</option>

</select>

<label>Monsoon Intensity</label>
<input type="number" name="MonsoonIntensity" required>

<label>Topography Drainage</label>
<input type="number" name="TopographyDrainage" required>

<label>River Management</label>
<input type="number" name="RiverManagement" required>

<label>Deforestation</label>
<input type="number" name="Deforestation" required>

<label>Urbanization</label>
<input type="number" name="Urbanization" required>

<label>Climate Change</label>
<input type="number" name="ClimateChange" required>

<button type="submit">Predict Flood</button>
</form>

{% if prediction is not none %}

<div class="result">

<h2>Prediction Result</h2>

<h3>📍 District: {{ district }}</h3>

<h3>🌧️ Estimated Rainfall: {{ rain }} mm</h3>

<h2>🌊 Flood Probability</h2>

<h1>{{ "%.2f"|format(prediction*100) }}%</h1>

<h2>{{ risk }}</h2>

</div>

<canvas id="floodChart"></canvas>

<script>

const ctx = document.getElementById('floodChart');

new Chart(ctx,{
    type:'bar',
    data:{
        labels:['Flood Probability'],
        datasets:[{
            label:'Probability (%)',
            data:[{{ prediction*100 }}]
        }]
    },
    options:{
        responsive:true,
        scales:{
            y:{
                beginAtZero:true,
                max:100
            }
        }
    }
});

</script>

{% if history %}

<h2 style="text-align:center;">Prediction History</h2>

<table>

<tr>
<th>District</th>
<th>Rainfall (mm)</th>
<th>Probability (%)</th>
<th>Risk</th>
</tr>

{% for row in history %}

<tr>

<td>{{ row[0] }}</td>
<td>{{ row[1] }}</td>
<td>{{ row[2] }}</td>
<td>{{ row[3] }}</td>

</tr>

{% endfor %}

</table>

{% endif %}

{% endif %}

</div>

</body>

</html>
"""
@app.route("/", methods=["GET", "POST"])
def home():

    prediction = None
    risk = ""
    district = ""
    rain = 0
    history = []

    # Create history file if it doesn't exist
    if not os.path.exists("history.csv"):
        with open("history.csv", "w", newline="") as f:
            pass

    if request.method == "POST":

        district = request.form["District"]
        rain = rainfall_data[district]

        values = [[
            float(request.form["MonsoonIntensity"]),
            float(request.form["TopographyDrainage"]),
            float(request.form["RiverManagement"]),
            float(request.form["Deforestation"]),
            float(request.form["Urbanization"]),
            float(request.form["ClimateChange"])
        ]]

        columns = [
            "MonsoonIntensity",
            "TopographyDrainage",
            "RiverManagement",
            "Deforestation",
            "Urbanization",
            "ClimateChange"
        ]

        data = pd.DataFrame(values, columns=columns)

        prediction = model.predict(data)[0]

        if prediction < 0.30:
            risk = " Low Risk"
        elif prediction < 0.60:
            risk = " Medium Risk"
        else:
            risk = " High Risk"

        with open("history.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                district,
                rain,
                f"{prediction*100:.2f}%",
                risk
            ])

    with open("history.csv", "r",encoding="utf-8") as f:
        reader = csv.reader(f)
        history = list(reader)

    return render_template_string(
        html,
        prediction=prediction,
        risk=risk,
        district=district,
        rain=rain,
        history=history
    )


if __name__ == "__main__":
    app.run(debug=True)