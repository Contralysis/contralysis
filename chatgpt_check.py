from openai import OpenAI

openai = OpenAI()

def analyze_contract(source_code):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a security expert specializing in analyzing Ethereum smart contract code for malicious behavior. you must evince malicious or not. if code is not malicious, must tell not malicious. do not insert another word between not and malicious. and then make report that analyze it."},
                {"role": "user", "content": f"Analyze the following Ethereum smart contract source code for any malicious behavior:\n\n{source_code}"}
            ]
        )

        print(source_code)

        analysis = response.choices[0].message.content 

        print(analysis)     

        if "not malicious" in analysis.lower():
            result = "악의적인 않은 코드입니다"
        else:
            result = "악의적인 코드입니다"
        
        return f"{result}\n\n{analysis}"
    except Exception as e:
        print(f"GPT API 오류: {e}")
        return f"GPT API 호출 중 오류가 발생했습니다: {str(e)}"
