# 🛠️ Git 협업 규칙
- 코드 충돌을 최소화하고 효율적인 협업을 위해 아래 규칙을 반드시 지켜주세요.

# 작업 시작 전

반드시 main 브랜치를 최신 상태로 맞춘다.

git checkout main
git pull origin main


그다음 자신의 브랜치로 이동해서 main을 merge (또는 rebase).

git checkout TAEHO   # 예시
git merge main   # 또는 git rebase main

# 📌 브랜치 전략

main: 항상 배포 가능한 안정된 코드만 존재해야 합니다.

개인 브랜치: 각 팀원은 자신에게 할당된 브랜치에서만 작업합니다.

# 📌 작업 시작 전

작업을 시작하기 전 반드시 최신 main 브랜치를 가져와야 합니다.

git checkout main
git pull origin main
git checkout feature/내브랜치
git merge main   # 또는 git rebase main


👉 이렇게 해야 충돌(conflict)을 줄일 수 있습니다.

# 📌 커밋 규칙

작은 단위로 커밋하기 (나중에 리뷰하기 편하도록).

커밋 메시지 규칙:

feat: 새로운 기능 추가

fix: 버그 수정

docs: 문서 작업

refactor: 코드 리팩토링

style: 코드 스타일 (세미콜론, 들여쓰기 등) 수정

test: 테스트 관련 추가/수정

예시:

feat: 로그인 페이지 UI 추가
fix: 회원가입 시 비밀번호 검증 오류 수정

# 📌 충돌(Conflict) 처리

충돌 발생 시 PR 작성자가 직접 해결합니다.

해결 후 다시 push → 리뷰어에게 알리기.

# 📌 브랜치 네이밍 규칙

feature/기능명 : 새로운 기능 개발

fix/버그명 : 버그 수정

hotfix/긴급패치 : 급한 수정

docs/문서 : 문서 작업

예시:

feature/login
fix/signup-error
docs/readme-update


작업 전에는 항상 git pull origin main → 내 브랜치에 merge/rebase 해주세요.
PR은 반드시 코드리뷰를 거쳐 main에 반영합니다.

# 풀 리퀘스트 규칙
- main 브랜치는 직접 커밋&푸시 불가능
- 각자 자신의 이름으로 만들어진 브랜치에 작업
- 자신의 브랜치에서 작업한 내용을 main 브랜치에 업로드 하고 싶을 때 github 웹사이트 메뉴에 Pull Request 요청
- Pull Request는 5명 중 2명 이상의 동의가 있을 시에 merge성공
- 다른사람이 요청한 PR을 확인할 때 꼭 오류가 없는지 제대로 수정되었는지 검토 후에 승인하기.

# SKN18-2nd-5Team
https://www.kaggle.com/datasets/blastchar/telco-customer-churn
https://www.kaggle.com/datasets/radheshyamkollipara/bank-customer-churn
https://www.kaggle.com/datasets?search=Churn
관련 웹페이지 만들어서
ex) 통신라라면 관련 분석 웹페이지 만들어서 머신러닝or딥러닝
예측 서비스 제공
[공공데이터 사용 가능]
