from flask import Flask, request, jsonify,Response
from core.main import create_trading_strategy_sell_only
from datetime import datetime
import pandas as pd
import io


app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return {"message": "API is working!"}

@app.route('/trading_stratergy/', methods=['POST'])
def calculate_risk_endpoint():
    try:
        data = request.get_json()
        app.logger.info("Request received")
        app.logger.info(f"Payload: {data}")

        training_period = data.get("training_period", None)
        testing_period = data.get("testing_period", None)

        stocks = data.get("stocks", None)
        lot_sizes = data.get("lot_sizes",None)

        if training_period is None:
            return jsonify({"error": "Missing field training_period"}), 400

        if testing_period is None:
            return jsonify({"error": "Missing field testing_period"}), 400

        try:
            training_start = datetime.strptime(training_period[0], '%Y-%m-%d')
            training_end = datetime.strptime(training_period[1], '%Y-%m-%d')
        except Exception as e:
            return jsonify({"error": str(e)})
        
        try:
            testing_start = datetime.strptime(testing_period[0], '%Y-%m-%d')
            testing_end = datetime.strptime(testing_period[1], '%Y-%m-%d')
        except Exception as e:
            return jsonify({"error": str(e)})

        if training_start > training_end:
            return jsonify({"error": "Training end date should be greater than start date"})

        if testing_start > testing_end:
            return jsonify({"error": "Testing end date should be greater than start date"})

        result_excel = create_trading_strategy_sell_only(training_period, testing_period, stocks, lot_sizes)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            result_excel.to_excel(writer, index=False, sheet_name="Periods")

        output.seek(0)
        return Response(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=trading_stratergy.xlsx"}
    )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)