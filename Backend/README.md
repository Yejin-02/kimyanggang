##install

python3 -m venv venv # 파이썬 가상환경 만들기
source ./venv/bin/activate # 가상환경 활성화
pip install fastapi==0.74.1 # fastapi 설치
pip install "uvicorn[standard]" # uvicorn 설치

##run

Backend 디렉토리에서
uvicorn main:app --reload

##포트문제

sudo lsof -i:8000
kill -9 <PID>
