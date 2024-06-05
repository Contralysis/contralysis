import os
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from etherscan_check import check_address
from chatgpt_check import analyze_contract
from firebase_config import init_firebase, save_report, get_report, get_user_reports, get_analysis, verify_id_token
import firebase_admin
from firebase_admin import auth
from config import Config

import os
from dotenv import load_dotenv


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config.from_object(Config)

# Initialize Firebase
init_firebase()


@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('index.html', firebase_config=app.config['FIREBASE_CONFIG'])

@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html', firebase_config=app.config['FIREBASE_CONFIG'])

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html', firebase_config=app.config['FIREBASE_CONFIG'])

@app.route('/authenticate', methods=['POST'])
def authenticate():
    id_token = request.form['idToken']
    user_id = verify_id_token(id_token)

    if user_id:
        session['user_id'] = user_id

        return redirect(url_for('index'))
    
    else:
        return jsonify({'message': '로그인 실패'}), 400

@app.route('/logout')
def logout():
    session.pop('user_id', None)

    return redirect(url_for('login'))

@app.route('/check', methods=['POST'])
def check():
    if 'user_id' not in session:

        return redirect(url_for('login'))

    address = request.form['address']
    user_id = session['user_id']

    if not address or not user_id:
        return jsonify({'message': '주소와 사용자 ID를 입력해 주세요'}), 400

    address_type, source_code = check_address(address)
    
    if address_type == 'wallet':
        result = "지갑 주소 입니다"
        return jsonify({'message': result})
    
    elif address_type == 'contract':
        report = analyze_contract(source_code)

        if "GPT API 호출 중 오류가 발생했습니다" in report:
            return jsonify({'message': report}), 500
        
        result_gpt, analysis = report.split('\n\n', 1)

        # 보고서 저장
        try:
            save_report(user_id, address, result_gpt, analysis)
        except Exception as e:
            print(f"보고서 저장 중 오류 발생: {e}")
            return jsonify({'message': '보고서를 저장하는 중 오류가 발생했습니다.'}), 500
        
        result = "악의적인 코드입니다" if "악의적인 코드입니다" in report.split("\n")[0] else "악의적이지 않은 코드입니다"
        return jsonify({'message': result})
    
    else:   
        return jsonify({'message': '잘못된 주소입니다'}), 400

@app.route('/report')
def report():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    address = request.args.get('address')
    user_id = session['user_id']

    if not address or not user_id:
        return "주소와 사용자 ID를 제공해 주세요.", 400

    report = get_report(user_id, address)

    analysis = get_analysis(user_id, address)
    
    if report:
        return render_template('report.html', report=report, address=address, analysis=analysis)
    else:
        return "보고서를 찾을 수 없습니다.", 404
    
@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    reports = get_user_reports(user_id)
    
    return render_template('history.html', reports=reports)

if __name__ == '__main__':
    app.run(debug=True)