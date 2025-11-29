import os
import requests

BASE = os.environ.get('BASE_URL', 'http://127.0.0.1:5000')
S = requests.Session()
# Use environment variables for test credentials. If not provided, skip login checks.
TEST_USER = os.environ.get('TEST_STUDENT_USER')
TEST_PASSWORD = os.environ.get('TEST_PASSWORD')
if TEST_USER and TEST_PASSWORD:
    creds = {'username': TEST_USER, 'password': TEST_PASSWORD}
    print(f'Logging in as {TEST_USER}...')
    r = S.post(BASE + '/login', json=creds, timeout=10)
    print('Login:', r.status_code, r.text[:200])
else:
    print('No TEST_STUDENT_USER/TEST_PASSWORD set; skipping login and using anonymous requests for pages.')

paths = ['/student/dashboard','/student/analytics','/student/assignments','/student/doubts']
for p in paths:
    r = S.get(BASE + p, timeout=10)
    print('\nGET', p, 'status', r.status_code)
    txt = r.text.lower()
    print('Contains LearnMatrixAPI:', 'learnmatrixapi' in txt)
    print('Contains skeleton placeholders:', 'skeleton' in txt)
    # look for client-side error placeholders
    print('Contains "error loading" string:', 'error loading' in txt)

# Also directly check JSON API endpoints
api_paths = ['/api/student/analytics','/api/student/assignments','/api/student/weakness-topics']
for p in api_paths:
    r = S.get(BASE + p, timeout=10)
    print('\nAPI', p, '->', r.status_code)
    try:
        print('JSON keys:', list(r.json().keys()))
    except Exception as e:
        print('JSON parse error:', e, 'response len', len(r.text))
