import requests
import time
import sys

BASE = 'http://localhost:8000/api'

# 1. Login or dev auth
login_res = requests.post(f'{BASE}/auth/login', json={'email': 'alex@example.com', 'password': 'password123'})
if login_res.status_code == 200:
    token = login_res.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
else:
    headers = {}

print('Auth headers acquired:', bool(headers))

# 2. Upload template
with open('backend/tests/fixtures/sample_single_column.docx', 'rb') as f:
    files = {'file': ('sample.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
    res = requests.post(f'{BASE}/templates/upload', files=files, headers=headers)

if res.status_code not in (200, 201):
    print('Upload failed:', res.status_code, res.text)
    sys.exit(1)

template_data = res.json()
template_id = template_data['id']
print(f'Uploaded template ID: {template_id}')

# 3. Check analysis
res = requests.get(f'{BASE}/templates/{template_id}/analysis', headers=headers)
assert res.status_code == 200, f"Analysis failed: {res.text}"
analysis = res.json()
sections = analysis.get('content', {}).get('sections', [])
print(f'Analysis OK: {len(sections)} sections extracted.')

# 4. Trigger tailor
jd_text = """
Senior Full Stack Engineer
Required Skills: Python, FastAPI, React, PostgreSQL, Docker, Kubernetes, LangGraph, LLM
Preferred Skills: TypeScript, AWS, Next.js, Microservices
Responsibilities: Build generative AI resume tailoring agents and robust APIs.
"""
tailor_res = requests.post(f'{BASE}/tailor', json={'template_id': template_id, 'jd_text': jd_text}, headers=headers)
assert tailor_res.status_code in (200, 202), f"Tailor trigger failed: {tailor_res.text}"
job_id = tailor_res.json()['job_id']
print(f'Tailor job triggered: {job_id}')

# 5. Poll job status
status_data = {}
for i in range(20):
    poll_res = requests.get(f'{BASE}/tailor/{job_id}', headers=headers)
    status_data = poll_res.json()
    status = status_data.get('status')
    print(f'Poll {i+1}: status = {status}')
    if status in ('completed', 'failed'):
        break
    time.sleep(1)

assert status_data.get('status') == 'completed', f"Job did not complete: {status_data}"
print('Final job status: COMPLETED')
print(f'Match score before: {status_data.get("match_score_before")}%, after: {status_data.get("match_score_after")}%')
print(f'Changes proposed: {len(status_data.get("changes", []))}')
print(f'Skills missing: {status_data.get("skills_missing")}')

# 6. Check download endpoints
docx_res = requests.get(f'{BASE}/tailor/{job_id}/docx', headers=headers)
assert docx_res.status_code == 200, f"DOCX download failed: {docx_res.status_code}"
print(f'DOCX download OK: {len(docx_res.content)} bytes')

pdf_res = requests.get(f'{BASE}/tailor/{job_id}/pdf', headers=headers)
assert pdf_res.status_code == 200, f"PDF download failed: {pdf_res.status_code}"
print(f'PDF download OK: {len(pdf_res.content)} bytes')

orig_pdf_res = requests.get(f'{BASE}/tailor/{job_id}/original-pdf', headers=headers)
assert orig_pdf_res.status_code == 200, f"Original PDF download failed: {orig_pdf_res.status_code}"
print(f'Original PDF download OK: {len(orig_pdf_res.content)} bytes')

# 7. Check change toggle (accept/reject)
if status_data.get('changes'):
    first_ch = status_data['changes'][0]
    ch_id = first_ch['id']
    ch_res = requests.post(f'{BASE}/tailor/{job_id}/change/{ch_id}', json={'accepted': False}, headers=headers)
    assert ch_res.status_code == 200, f"Change toggle failed: {ch_res.text}"
    print(f'Toggle change {ch_id} to accepted=False OK: {ch_res.json().get("status")}')

# 8. Check creating a resume in the editor from tailored content
resume_create_res = requests.post(f'{BASE}/resumes', json={
    'title': 'Tailored Resume - Alex Johnson',
    'content': status_data.get('tailored_content'),
    'style': analysis.get('style')
}, headers=headers)
assert resume_create_res.status_code in (200, 201), f"Editor resume creation failed: {resume_create_res.text}"
new_resume_id = resume_create_res.json()['id']
print(f'Successfully loaded tailored resume into editor with Resume ID: {new_resume_id}')

print('\nALL END-TO-END VERIFICATION CHECKS PASSED SUCCESSFULLY!')
