
## Everyone can make own classification model!
공부없이 그냥 분류 모델을 만들고 싶은 사람을 위한 프로그램
<br/><br />

## 0. 설치 방법 ( how to setting )

```
git clone https://github.com/dnfwlxo11/flask_classification_sampleServer.git  

cd {clone directory}
cd docker-env

docker-compose build

docker-compose up (if you want background mod, add -d option)

start train your classification model
```  

<br/>

 ## 1. 서비스 프로세스 ( Service Process)
![detection](https://user-images.githubusercontent.com/32836490/144176518-ff0d9fcf-500f-4ba1-ac8d-b9d781c02c68.jpg)  


<br />

## 2. 간단한 실행 모습 (showing, example) 
![easy_1 b162eaab](https://user-images.githubusercontent.com/32836490/155907410-b839fd5d-9f04-483f-9064-0daa5ad9c157.jpg)
2-1)  메인 페이지의 모습, 좌측은 추론, 가운데는 학습, 우측은 모델 확인 및 다운로드 페이지   
(left side inference page, center side train custom model page, right side trained model check and download page)
<br />
![easy_3 54c11ba0](https://user-images.githubusercontent.com/32836490/155907457-11c536d0-2013-4a28-b430-e2d2b9af470f.jpg)
2-2) 김밥 사진을 수집하여 학습하는 모습 (collect sample images and train example, gimbab is a kind of food)
<br />
![easy_2 e5593d69](https://user-images.githubusercontent.com/32836490/155907565-7c763e80-1145-4b1b-937d-c94df2b7d2c2.jpg)
2-3) 2-2에서 학습한 모델로 추론을 해본 결과   
(2-2 train model inference test, "1638489510412" is just trained classification model name)
<br />
![easy_4 5681912b](https://user-images.githubusercontent.com/32836490/155907715-218d032e-b546-40d7-bb35-b6e44d812f0f.jpg)
2-4) 학습한 모델들을 확인하고 다운로드 받을 수 있는 페이지   
(check trained models and model download or remove page)
