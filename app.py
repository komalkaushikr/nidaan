from flask import Flask, render_template, jsonify
import random, time

app = Flask(__name__)

bins_data = [
    {"id": 1, "name": "Miranda House College", "lat": 28.6878, "lng": 77.2150, "fill": 78, "type": "College"},
    {"id": 2, "name": "Lady Shri Ram College", "lat": 28.6563, "lng": 77.2436, "fill": 45, "type": "College"},
    {"id": 3, "name": "Gargi College", "lat": 28.5535, "lng": 77.1889, "fill": 92, "type": "College"},
    {"id": 4, "name": "Jesus & Mary College", "lat": 28.5972, "lng": 77.1714, "fill": 31, "type": "College"},
    {"id": 5, "name": "IP College for Women", "lat": 28.6741, "lng": 77.2291, "fill": 67, "type": "College"},
    {"id": 6, "name": "Sarojini Nagar Hostel", "lat": 28.5770, "lng": 77.1955, "fill": 55, "type": "Hostel"},
    {"id": 7, "name": "Lajpat Nagar Community Center", "lat": 28.5677, "lng": 77.2433, "fill": 83, "type": "Community"},
    {"id": 8, "name": "Karol Bagh Hostel Block B", "lat": 28.6514, "lng": 77.1907, "fill": 20, "type": "Hostel"},
    {"id": 9, "name": "Dwarka Sector 10 SHG Center", "lat": 28.5823, "lng": 77.0490, "fill": 61, "type": "SHG Center"},
    {"id": 10, "name": "Rohini Women's Hostel", "lat": 28.7041, "lng": 77.1025, "fill": 44, "type": "Hostel"},
]

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

if __name__ == '__main__':
    app.run(debug=True)
