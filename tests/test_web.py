import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.expected_conditions import alert_is_present, text_to_be_present_in_element
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time
import chromedriver_autoinstaller
import subprocess
import os
import signal
import requests

@pytest.fixture(scope="class")
def server():
    # server.py 파일의 경로
    server_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../server.py')
    
    # 서버 실행
    process = subprocess.Popen(['python', server_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(5)  # 서버가 실행될 시간을 줌
    
    # 서버가 시작될 때까지 대기
    for _ in range(30):
        try:
            response = requests.get("http://127.0.0.1:5000")
            if response.status_code == 200:
                break
        except requests.ConnectionError:
            time.sleep(1)
    
    yield process
    
    # 서버 종료
    os.kill(process.pid, signal.SIGTERM)

@pytest.fixture(scope="class")
def driver_init(request, server):
    # ChromeDriver 자동 설치
    chromedriver_autoinstaller.install()

    # ChromeOptions 객체 생성
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # UI 없이 실행 (옵션)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Chrome WebDriver 초기화
    driver = webdriver.Chrome(options=options)
    request.cls.driver = driver
    yield
    driver.quit()

@pytest.mark.usefixtures("driver_init")
class TestWebApp:

    def test_home_page(self):
        # 로컬 서버에 접속
        self.driver.get("http://127.0.0.1:5000")
        
        # 페이지 제목 확인
        assert "Login" in self.driver.title
        
    def test_login(self):
        # 로컬 서버에 접속
        self.driver.get("http://127.0.0.1:5000/login")
        
        # 로그인 테스트
        email_field = self.driver.find_element("name", "email")
        password_field = self.driver.find_element("name", "password")
        login_button = self.driver.find_element("tag name", "button")
        
        email_field.send_keys("21900421@handong.edu")
        password_field.send_keys("12345678")
        login_button.click()
        
        # 페이지 로드 대기
        wait = WebDriverWait(self.driver, 10)
        wait.until(lambda driver: "Ethereum Address Checker" in driver.title)
        
        assert "Ethereum Address Checker" in self.driver.title

    def test_check_scam(self):
        self.test_login()
        self.driver.get("http://127.0.0.1:5000")
        address_field = self.driver.find_element("name", "address")
        check_button = self.driver.find_element("tag name", "button")
    
        address_field.send_keys("0xA0cfba0825ac28441f3b718fD2e40Ad7605F93c7")
        check_button.click()
    
        # 결과 텍스트가 나타날 때까지 대기
        wait = WebDriverWait(self.driver, 10)
        wait.until(text_to_be_present_in_element(("id", "result"), "This is malicious."))
        
        # 체크 후 결과 확인
        result_text = self.driver.find_element("id", "result").text
        print(f"Scam Result Text: {result_text}")  
        assert "This is malicious." in result_text

    def test_check_normal(self):
        self.test_login()
        self.driver.get("http://127.0.0.1:5000")
        address_field = self.driver.find_element("name", "address")
        check_button = self.driver.find_element("tag name", "button")
    
        address_field.send_keys("0x9bcCB0Dd17c1B2A62B70Ac4Bfad033a90CbA6F50")
        check_button.click()
    
        # 결과 텍스트가 나타날 때까지 대기
        wait = WebDriverWait(self.driver, 10)
        wait.until(text_to_be_present_in_element(("id", "result"), "This is not malicious."))
        
        # 체크 후 결과 확인
        result_text = self.driver.find_element("id", "result").text
        print(f"Normal Result Text: {result_text}") 
        assert "This is not malicious." in result_text

    def test_check_invalid(self):
        self.test_login()
        self.driver.get("http://127.0.0.1:5000")
        address_field = self.driver.find_element("name", "address")
        check_button = self.driver.find_element("tag name", "button")
    
        address_field.send_keys("0x24745f2B750f8cAC17F")
        check_button.click()
    
        # 결과 텍스트가 나타날 때까지 대기
        wait = WebDriverWait(self.driver, 10)
        wait.until(text_to_be_present_in_element(("id", "result"), "Invalid address"))
        
        # 체크 후 결과 확인
        result_text = self.driver.find_element("id", "result").text
        print(f"Invalid Result Text: {result_text}") 
        assert "Invalid address" in result_text

    def test_check_wallet(self):
        self.test_login()
        self.driver.get("http://127.0.0.1:5000")
        address_field = self.driver.find_element("name", "address")
        check_button = self.driver.find_element("tag name", "button")
    
        address_field.send_keys("0xF6a0Bdc3F28f293DF75cbC174dad31CDAB53500A")
        check_button.click()
    
        # 결과 텍스트가 나타날 때까지 대기
        wait = WebDriverWait(self.driver, 10)
        wait.until(text_to_be_present_in_element(("id", "result"), "This is the wallet address"))
        
        # 체크 후 결과 확인
        result_text = self.driver.find_element("id", "result").text
        print(f"Wallet Result Text: {result_text}") 
        assert "This is the wallet address" in result_text

    def test_check_register_page(self):
        # 로컬 서버에 접속
        self.driver.get("http://127.0.0.1:5000/login")
        
        # Register 링크 클릭
        register_link = self.driver.find_element("link text", "Register")
        register_link.click()
        
        # 페이지 로드 대기
        wait = WebDriverWait(self.driver, 10)
        wait.until(lambda driver: "Register" in driver.title)
        
        # Register 페이지 제목 확인
        assert "Register" in self.driver.title
    

    def test_logout_redirect(self):
        self.test_login()
        self.driver.get("http://127.0.0.1:5000")
        
        logout_link = self.driver.find_element("link text", "Logout")
        logout_link.click()
        
        time.sleep(2)  # 페이지 로드 대기
        
        # 로그아웃 후 페이지 제목 확인
        assert "Login" in self.driver.title

    def test_report_who_subscribe(self):
        self.test_login()  # 로그인이 성공해야 함
        self.driver.get("http://127.0.0.1:5000")
        
        # 정상적인 주소 입력
        address_field = self.driver.find_element("name", "address")
        check_button = self.driver.find_element("tag name", "button")
        
        address_field.send_keys("0x9bcCB0Dd17c1B2A62B70Ac4Bfad033a90CbA6F50")
        check_button.click()
        
        # View Report 버튼 클릭
        wait = WebDriverWait(self.driver, 10)
        view_report_link = wait.until(lambda driver: driver.find_element("link text", "View Report"))
        view_report_link.click()
        
        # Report 페이지로 이동했는지 확인
        wait.until(lambda driver: "Report" in driver.title)
        assert "Report" in self.driver.title

    def test_report_who_not_subscribe(self):
        # 다른 사용자로 로그인
        self.driver.get("http://127.0.0.1:5000/login")
    
        email_field = self.driver.find_element("name", "email")
        password_field = self.driver.find_element("name", "password")
        login_button = self.driver.find_element("tag name", "button")
    
        email_field.send_keys("qwer1234@naver.com")
        password_field.send_keys("12345678")
        login_button.click()
    
        # 로그인 성공 확인
        wait = WebDriverWait(self.driver, 10) 
        wait.until(lambda driver: "Ethereum Address Checker" in driver.title)
        assert "Ethereum Address Checker" in self.driver.title
    
        # 정상적인 주소 입력
        address_field = self.driver.find_element("name", "address")
        check_button = self.driver.find_element("tag name", "button")
    
        address_field.send_keys("0x9bcCB0Dd17c1B2A62B70Ac4Bfad033a90CbA6F50")
        check_button.click()
    
        # View Report 버튼 클릭
        view_report_link = wait.until(lambda driver: driver.find_element("link text", "View Report"))
        view_report_link.click()
    
        # Subscription Required 페이지로 이동했는지 확인
        wait.until(lambda driver: driver.find_element(By.TAG_NAME, "h1").text == "Subscription Required")
        assert "Subscribe" in self.driver.title



    def test_login_fail(self):
        # 로컬 서버에 접속
        self.driver.get("http://127.0.0.1:5000/login")
        
        # 로그인 테스트
        email_field = self.driver.find_element("name", "email")
        password_field = self.driver.find_element("name", "password")
        login_button = self.driver.find_element("tag name", "button")
        
        email_field.send_keys("21900421@handong.edu")
        password_field.send_keys("wrong password")
        login_button.click()
        
        wait = WebDriverWait(self.driver, 5)
        alert = wait.until(alert_is_present())
        
        assert alert

if __name__ == "__main__":
    pytest.main()
