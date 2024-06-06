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
        return jsonify({'message': 'Login Failed'}), 400

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
        return jsonify({'message': 'Please enter your address and user ID'}), 400

    address_type, source_code = check_address(address)
    
    if address_type == 'wallet':
        result = "This is the wallet address"
        return jsonify({'message': result})
    
    elif address_type == 'contract':
        report = analyze_contract(source_code)

        if "An error occurred while calling the GPT API" in report:
            return jsonify({'message': report}), 500
        
        result_gpt, analysis = report.split('\n\n', 1)

        # 보고서 저장
        try:
            save_report(user_id, address, result_gpt, analysis)
        except Exception as e:
            print(f"Error saving report: {e}")
            return jsonify({'message': 'An error occurred while saving the report.'}), 500
        
        result = "This is malicious." if "This is malicious." in report.split("\n")[0] else "This is not malicious."
        return jsonify({'message': result})
    
    else:   
        return jsonify({'message': 'Invalid address'}), 400

@app.route('/report')
def report():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    address = request.args.get('address')
    user_id = session['user_id']

    if not address or not user_id:
        return "Please provide me with your address and user ID.", 400

    report = get_report(user_id, address)

    analysis = get_analysis(user_id, address)
    
    if report:
        return render_template('report.html', report=report, address=address, analysis=analysis)
    else:
        return "Report not found.", 404
    
@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    reports = get_user_reports(user_id)
    
    return render_template('history.html', reports=reports)

@app.route('/payment')
def payment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('payment.html')

if __name__ == '__main__':
    app.run(debug=True)