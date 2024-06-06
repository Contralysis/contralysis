import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
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
        
        time.sleep(2)  # 페이지 로드 대기
        
        # 로그인 후 페이지 제목 확인
        assert "Ethereum Address Checker" in self.driver.title

if __name__ == "__main__":
    pytest.main()