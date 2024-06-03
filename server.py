from flask import Flask, request, jsonify, render_template
from etherscan_check import check_address
from chatgpt_check import analyze_contract
from database import init_db, save_report, get_report
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# 데이터베이스 초기화
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check():
    address = request.form['address']
    if not address:
        return jsonify({'message': '주소를 입력해 주세요'}), 400

    address_type, source_code = check_address(address)
    
    if address_type == 'wallet':
        result = "지갑 주소 입니다"
        return jsonify({'message': result})
    elif address_type == 'contract':
        report = analyze_contract(source_code)
        if "GPT API 호출 중 오류가 발생했습니다" in report:
            return jsonify({'message': report}), 500
        # 보고서 저장
        try:
            save_report(address, report)
        except Exception as e:
            print(f"보고서 저장 중 오류 발생: {e}")
            return jsonify({'message': '보고서를 저장하는 중 오류가 발생했습니다.'}), 500
        result = "악의적인 코드입니다" if "악의적인 코드입니다" in report.split("\n")[0] else "악의적이지 않은 코드입니다"
        return jsonify({'message': result})
    else:
        return jsonify({'message': '잘못된 주소입니다'}), 400

@app.route('/report')
def report():
    address = request.args.get('address')
    report = get_report(address)
    if report:
        return render_template('report.html', report=report)
    else:
        return "보고서를 찾을 수 없습니다.", 404

if __name__ == '__main__':
    app.run(debug=True)
