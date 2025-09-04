ver_03 모듈화 했습니다.

requirements.txt 파일에 필요한 패키지들을 명시했습니다.
가상환경을 설정하고, `pip install -r requirements.txt` 명령어로 필요한 패키지들을 설치할 수 있습니다.
hotel_mod에서 main.py를 실행하면 됩니다.

XGBoost 훈련 성능  
  정확도 (Accuracy): 0.8787  
  정밀도 (Precision): 0.8585  
  재현율 (Recall): 0.8051  
  F1-점수 (F1-Score): 0.8310  
  AUC: 0.9531  

XGBoost 테스트 성능  
  정확도 (Accuracy): 0.8664  
  정밀도 (Precision): 0.8457  
  재현율 (Recall): 0.7819  
  F1-점수 (F1-Score): 0.8125  
  AUC: 0.9417  