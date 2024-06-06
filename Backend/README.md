## install

python3 -m venv venv # 파이썬 가상환경 만들기

source ./venv/bin/activate # 가상환경 활성화

pip install fastapi==0.74.1 # fastapi 설치

pip install "uvicorn[standard]" # uvicorn 설치

## run

Backend 디렉토리에서

uvicorn main:app --reload

## 포트문제

sudo lsof -i:8000

kill -9 <PID>

## Dockerize

cd Backend

docker build -t yangyj21/mobile-exp-backend:y0.1 .

docker push yangyj21/mobile-exp-backend:y0.1

backend.yaml에서 image : "여기를 수정"

cd ../k8s

kubectl apply -f backend.yaml

kubectl get pods -l app=backend

kubectl describe pod backend-pod-name

=> image 잘 설정 되어 있나 확인
Containers:
  server:
    Container ID:   containerd://69a947b4bd80e73d66b8d4b73f4519e80264fa62d988971c80a6f12fab6142f0
    Image:          <여기를 확인>