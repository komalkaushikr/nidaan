from flask import Flask, render_template, jsonify
import random, time
import numpy as np

app = Flask(__name__)

# Each bin now carries a short rolling history of recent hourly fill readings,
# used by the forecast endpoint below to project time-to-80% via linear regression.
bins_data = [
    {"id": 1, "name": "Miranda House College", "lat": 28.6878, "lng": 77.2150, "fill": 78, "type": "College", "history": [62, 66, 69, 72, 75, 78]},
    {"id": 2, "name": "Lady Shri Ram College", "lat": 28.6563, "lng": 77.2436, "fill": 45, "type": "College", "history": [38, 40, 41, 43, 44, 45]},
    {"id": 3, "name": "Gargi College", "lat": 28.5535, "lng": 77.1889, "fill": 92, "type": "College", "history": [74, 79, 83, 86, 89, 92]},
    {"id": 4, "name": "Jesus & Mary College", "lat": 28.5972, "lng": 77.1714, "fill": 31, "type": "College", "history": [26, 27, 28, 29, 30, 31]},
    {"id": 5, "name": "IP College for Women", "lat": 28.6741, "lng": 77.2291, "fill": 67, "type": "College", "history": [55, 58, 60, 63, 65, 67]},
    {"id": 6, "name": "Sarojini Nagar Hostel", "lat": 28.5770, "lng": 77.1955, "fill": 55, "type": "Hostel", "history": [47, 49, 51, 52, 54, 55]},
    {"id": 7, "name": "Lajpat Nagar Community Center", "lat": 28.5677, "lng": 77.2433, "fill": 83, "type": "Community", "history": [68, 72, 75, 78, 80, 83]},
    {"id": 8, "name": "Karol Bagh Hostel Block B", "lat": 28.6514, "lng": 77.1907, "fill": 20, "type": "Hostel", "history": [16, 17, 18, 19, 19, 20]},
    {"id": 9, "name": "Dwarka Sector 10 SHG Center", "lat": 28.5823, "lng": 77.0490, "fill": 61, "type": "SHG Center", "history": [51, 54, 56, 58, 59, 61]},
    {"id": 10, "name": "Rohini Women's Hostel", "lat": 28.7041, "lng": 77.1025, "fill": 44, "type": "Hostel", "history": [36, 38, 39, 41, 42, 44]},
]

LOOKAHEAD_HR = 1.5  # alert fires if forecast crosses 80% within this window


def forecast_bin(bin_info):
    """Fit a linear trend on recent fill history, project hours-to-80%."""
    history = bin_info["history"]
    x = np.arange(len(history))
    slope, intercept = np.polyfit(x, history, 1)
    slope = float(slope)
    if slope <= 0:
        return {"slope_per_hr": round(slope, 2), "hrs_to_80": None, "predictive_alert": False}
    hrs_to_80 = (80 - bin_info["fill"]) / slope
    predictive_alert = bool(0 <= hrs_to_80 <= LOOKAHEAD_HR)
    return {
        "slope_per_hr": round(slope, 2),
        "hrs_to_80": round(float(hrs_to_80), 2) if hrs_to_80 >= 0 else None,
        "predictive_alert": predictive_alert,
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/bins')
def get_bins():
    return jsonify(bins_data)

@app.route('/api/impact')
def get_impact():
    return jsonify({
        "pads_collected": 284710,
        "burns_prevented": 284710,
        "carbon_saved_kg": round(284710 * 0.0023, 1),
        "shg_earnings": 142355,
        "active_bins": len(bins_data),
        "partner_collections": 6
    })

@app.route('/api/alert/<int:bin_id>', methods=['POST'])
def trigger_alert(bin_id):
    bin_info = next((b for b in bins_data if b['id'] == bin_id), None)
    if bin_info:
        return jsonify({"status": "alert_sent", "message": f"SHG agent notified for {bin_info['name']}", "eta": "25 mins"})
    return jsonify({"status": "error"}), 404


@app.route('/api/forecast/<int:bin_id>')
def forecast(bin_id):
    """Predictive layer: forecasts whether a bin will cross 80% within
    the next LOOKAHEAD_HR hours, based on a linear fit of recent fill history.
    See forecast_analysis.py for the backtest comparing this against a
    naive reactive (alert-only-at-80%) baseline."""
    bin_info = next((b for b in bins_data if b['id'] == bin_id), None)
    if not bin_info:
        return jsonify({"status": "error"}), 404
    result = forecast_bin(bin_info)
    result.update({"bin_id": bin_id, "name": bin_info["name"], "current_fill": bin_info["fill"]})
    return jsonify(result)


@app.route('/api/forecast')
def forecast_all():
    return jsonify([
        {**forecast_bin(b), "bin_id": b["id"], "name": b["name"], "current_fill": b["fill"]}
        for b in bins_data
    ])

if __name__ == '__main__':
    app.run(debug=True)