from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

openai = OpenAI()

def analyze_contract(source_code):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a security expert specializing in analyzing Ethereum smart contract code for malicious or vulnerability behavior."},
                {"role": "system", "content": "You must evince malicious or not on first sentence. 'This is malicious.' or 'This is not malicious.'. do not insert or change another word between not and malicious on first sentence. and then, change line. (enter)"},
                {"role": "system", "content": "And then, make report that analyze it. Tell me it's malicious even if it's judged to be vulnerable."},
                {"role": "system", "content": "In particular, see if there are no part of the recurrence vulnerability or specific results."},
                {"role": "user", "content": f"Analyze the following Ethereum smart contract source code for any malicious or vulneralbe behavior:\n\n{source_code}"}
            ]
        )

        print(source_code)

        analysis = response.choices[0].message.content 

        print(analysis)     

        if "not malicious" in analysis.lower():
            result = "This is not malicious."
        else:
            result = "This is malicious."
        
        return f"{result}\n\n{analysis}"
    
    except Exception as e:
        print(f"GPT API 오류: {e}")
        return f"GPT API 호출 중 오류가 발생했습니다: {str(e)}"
