import pytest
from fastapi.testclient import TestClient
from backend import store
from backend.main import app, SESSIONS

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setattr(store,'DB_PATH',tmp_path/'test.sqlite3')
    SESSIONS.clear()
    with TestClient(app) as c:
        yield c


def parent(client,email='parent@example.test',password='a-different-long-password'):
    response=client.post('/auth/parent/register',json={'name':'Mama','email':email,'password':password})
    assert response.status_code==201,response.text
    return {'Authorization':'Bearer '+response.json()['access_token']}


def child(client,headers,username='amina_123',pin='8392'):
    response=client.post('/children',headers=headers,json={'name':'Amina','username':username,
        'pin':pin,'grade':'Grade 1','avatar':'🦋','language':'Urdu'})
    assert response.status_code==201,response.text
    return response.json()['id']


def login_child(client,username='amina_123',pin='8392'):
    response=client.post('/auth/child/login',json={'username':username,'pin':pin})
    assert response.status_code==200,response.text
    return {'Authorization':'Bearer '+response.json()['access_token']}


def test_seed_bank_all_grades_subjects(client):
    catalog=client.get('/catalog').json()
    assert len(catalog['grades'])==7
    assert len(catalog['subjects'])==7
    headers=parent(client)
    lessons=client.get('/lessons',headers=headers).json()
    assert len(lessons)>=49
    assert len({(r['grade'],r['subject']) for r in lessons})==49
    assert all(len(r['questions'])>=6 for r in lessons)
    assert sum(len(r['questions']) for r in lessons)>=294


def test_register_login_and_role_enforcement(client):
    assert client.get('/children').status_code==401
    headers=parent(client)
    assert client.post('/auth/parent/register',json={'name':'M','email':'parent@example.test','password':'password-abcde'}).status_code==422
    duplicate=client.post('/auth/parent/register',json={'name':'Mother','email':'PARENT@example.test','password':'password-abcde'})
    assert duplicate.status_code==409
    assert client.post('/auth/parent/login',json={'email':'parent@example.test','password':'wrong'}).status_code==401
    logged=client.post('/auth/parent/login',json={'email':'parent@example.test','password':'a-different-long-password'})
    assert logged.status_code==200
    sid=child(client,headers)
    assert client.post('/auth/child/login',json={'username':'amina_123','pin':'0000'}).status_code==401
    student_headers=login_child(client)
    assert client.get('/children',headers=student_headers).status_code==403
    assert client.post('/children',headers=student_headers,json={}).status_code==403
    assert client.post('/lessons',headers=student_headers,json={}).status_code==403
    assert client.get('/auth/me',headers=student_headers).json()['account']['id']==sid
    assert 'pin_hash' not in str(client.get('/auth/me',headers=student_headers).json())
    assert client.post('/auth/logout',headers=student_headers).status_code==200
    assert client.get('/auth/me',headers=student_headers).status_code==401


def test_student_quiz_progress_private(client):
    headers=parent(client)
    sid=child(client,headers)
    student_headers=login_child(client)
    lessons=client.get('/lessons?grade=Grade%201&subject=Mathematics',headers=student_headers).json()
    assert lessons
    lesson=lessons[0]
    answers=[q['answer'] for q in lesson['questions']]
    assert client.post('/attempts',headers=headers,json={'lesson_id':lesson['id'],'answers':answers}).status_code==403
    bad=client.post('/attempts',headers=student_headers,json={'lesson_id':lesson['id'],'answers':[]})
    assert bad.status_code==422
    attempt=client.post('/attempts',headers=student_headers,json={'lesson_id':lesson['id'],'answers':answers})
    assert attempt.status_code==201
    assert attempt.json()['correct']==len(answers)
    progress=client.get(f'/progress/{sid}',headers=headers).json()
    assert progress['completed_lessons']==1
    assert progress['total_stars']==3
    assert client.get('/progress/999999',headers=student_headers).status_code==404
    other=parent(client,email='other@example.test')
    assert client.get(f'/progress/{sid}',headers=other).status_code==403


def test_child_edit_and_legacy_account_migration(client):
    # Existing v0.1 database rows remain intact and migrate to first parent.
    with store.connection() as con:
        con.execute('INSERT INTO students(name,grade,avatar,language) VALUES (?,?,?,?)',
                    ('Legacy Kid','Preschool','🌟','English'))
    h=parent(client)
    children=client.get('/children',headers=h).json()
    legacy=next(x for x in children if x['name']=='Legacy Kid')
    assert legacy['username'] is None
    data={'name':'Legacy Kid','username':'legacy_kid','pin':'7829',
          'grade':'Preschool','avatar':'🌟','language':'English'}
    assert client.put(f"/children/{legacy['id']}",headers=h,json=data).status_code==200
    assert client.post('/auth/child/login',json={'username':'legacy_kid','pin':'7829'}).status_code==200
    other=parent(client,email='other@example.test')
    assert client.put(f"/children/{legacy['id']}",headers=other,json=data).status_code==403


def test_parent_lesson_editor(client):
    h=parent(client)
    lesson={'grade':'Grade 5','subject':'Science','title':'New Discovery',
            'explanation':'A new lesson','emoji':'🪐',
            'questions':[{'prompt':'A question?','choices':['Yes','No','Maybe'],'answer':0}]}
    assert client.post('/lessons',json=lesson).status_code==401
    created=client.post('/lessons',headers=h,json=lesson)
    assert created.status_code==201,created.text
    lid=created.json()['id']
    lesson['title']='Updated Discovery'
    assert client.put(f'/lessons/{lid}',headers=h,json=lesson).status_code==200
    assert client.get(f'/lessons/{lid}',headers=h).json()['title']=='Updated Discovery'
    assert client.delete(f'/lessons/{lid}',headers=h).status_code==200
    assert client.get(f'/lessons/{lid}',headers=h).status_code==404
