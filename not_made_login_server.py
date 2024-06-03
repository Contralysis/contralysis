from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from etherscan_check import check_address
from chatgpt_check import analyze_contract
from firebase_config import init_firebase, get_user_reports, save_report
import stripe
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Stripe API 설정
stripe.api_key = 'your_stripe_api_key'

# Firebase 초기화
firebase_app = init_firebase()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Firebase Authentication 로그인 처리
        try:
            user = firebase_app.auth().sign_in_with_email_and_password(email, password)
            session['user'] = user
            return redirect(url_for('dashboard'))
        except:
            return "로그인 실패"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session['user']
    reports = get_user_reports(user['localId'])
    return render_template('dashboard.html', reports=reports)

@app.route('/check', methods=['POST'])
def check():
    address = request.form['address']
    address_type, source_code = check_address(address)
    
    if address_type == 'wallet':
        result = "지갑 주소 입니다"
        return jsonify({'message': result})
    elif address_type == 'contract':
        report = analyze_contract(source_code)
        user_id = session['user']['localId']
        save_report(user_id, address, report)
        result = "악의적인 코드입니다" if "악의적인 코드입니다" in report else "악의적이지 않은 코드입니다"
        return jsonify({'message': result})
    else:
        return jsonify({'message': '잘못된 주소입니다'})

@app.route('/pay', methods=['POST'])
def pay():
    amount = 500  # 결제 금액 설정 (단위: 센트)
    address = request.form['address']
    
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'Smart Contract Report',
                },
                'unit_amount': amount,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('success', address=address, _external=True),
        cancel_url=url_for('dashboard', _external=True),
    )
    
    return redirect(session.url, code=303)

@app.route('/success')
def success():
    address = request.args.get('address')
    user = session['user']
    report = get_user_reports(user['localId'], address)
    return render_template('report.html', report=report)

if __name__ == '__main__':
    app.run(debug=True)
