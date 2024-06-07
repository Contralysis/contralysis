import os
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from etherscan_check import check_address
from chatgpt_check import analyze_contract
from firebase_config import init_firebase, save_report, get_report, get_user_reports, get_analysis, verify_id_token, save_user_profile, get_user_profile, update_user_subscription
import firebase_admin
from firebase_admin import auth
from functools import wraps
from config import Config
import time

import os
from dotenv import load_dotenv


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config.from_object(Config)

# Initialize Firebase
init_firebase()

def subscriber_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'is_subscriber' not in session or not session['is_subscriber']:
            return redirect(url_for('show_subscribe'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('index.html', firebase_config=app.config['FIREBASE_CONFIG'])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        id_token = data.get('idToken')

        try:
            decoded_token = verify_id_token(id_token)
            print(f"Decoded Token: {decoded_token}")

            if not decoded_token:
                raise ValueError("Invalid ID token")

            user_id = decoded_token['uid']
            email = decoded_token['email']

            if not email:
                raise ValueError("Email not found in decoded token")

            # Set initial subscription status to False
            auth.set_custom_user_claims(user_id, {'subscriber': False})

            # Save user profile data in Firestore
            user_profile = {
                'email': email,
                'subscriber': False
            }
            save_user_profile(user_id, user_profile)

            print(f"User profile saved for user ID: {user_id}")

            return jsonify({'message': 'User created successfully'}), 200
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return jsonify({'message': 'Error creating user', 'error': str(e)}), 400

    return render_template('register.html', firebase_config=app.config['FIREBASE_CONFIG'])

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html', firebase_config=app.config['FIREBASE_CONFIG'])

@app.route('/authenticate', methods=['POST'])
def authenticate():
    data = request.get_json()
    id_token = data.get('idToken')
    print(f"ID Token received: {id_token}")

    decoded_token = verify_id_token(id_token)

    time.sleep(1)  # need to wait a bit before verifying id token

    if decoded_token:
        user_id = decoded_token['uid']
        session['user_id'] = user_id

        # Fetch user profile from Firestore
        user_profile = get_user_profile(user_id)
        
        if user_profile:
            session['is_subscriber'] = user_profile.get('subscriber', False)
        else:
            session['is_subscriber'] = False
        
        print(f"Authenticated user ID: {user_id}, Subscriber: {session['is_subscriber']}")
        
        return jsonify({'message': 'Authentication successful'}), 200
    else:
        print("User ID not found or invalid token")
        return jsonify({'message': 'Login Failed'}), 400

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('is_subscriber', None)

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
@subscriber_required
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
@subscriber_required
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

@app.route('/subscribe', methods=['POST'])
def subscribe():
    if 'user_id' not in session:
        return jsonify({'message': '로그인 필요합니다'}), 400

    user_id = session['user_id']
    
    try:
        # Fetch user profile from Firestore
        user_profile = get_user_profile(user_id)
        if not user_profile:
            return jsonify({'message': 'User profile not found.'}), 404
        
        # Update the user's subscription status in Firestore
        update_user_subscription(user_id, True)
        
        # Update the session
        session['is_subscriber'] = True
        
        return jsonify({'message': '구독이 완료되었습니다'}), 200
    except Exception as e:
        return jsonify({'message': f'구독 중 오류가 발생했습니다: {str(e)}'}), 500
    
@app.route('/subscribe', methods=['GET'])
def show_subscribe():
    return render_template('subscribe.html')

if __name__ == '__main__':
    app.run(debug=True)