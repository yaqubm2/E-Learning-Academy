"""E-Learning Academy v0.2 — warm, touch-sized Flet learning experience."""
import flet as ft
from urllib.parse import quote

from .api import AcademyAPI, ApiError

BG='#F4F7FF'
INK='#26335A'
SOFT='#687897'
PURPLE='#6655D5'
PINK='#FF647C'
BLUE='#3F8DEA'
GREEN='#2B986F'
GOLD='#F3B93A'
SUBJECT_ICON={'English':'🔤','Mathematics':'🧮','Urdu':'🌙','Science':'🔬',
              'General Knowledge':'🌍','Islamiyat':'🤲','Computer':'💻'}
SUBJECT_COLOR=['#EDE9FF','#E5F2FF','#FFF0E0','#E9F8F1','#FFF6DC','#F3EAFF','#E7F5F8']
AVATARS=['🦊','🐻','🦁','🐼','🐰','🐯','🦋','🚀','🌟','🦄']


def main(page:ft.Page):
    page.title='E-Learning Academy • Learn, Play, Grow'
    page.bgcolor=BG
    page.theme_mode=ft.ThemeMode.LIGHT
    page.padding=0
    page.scroll=ft.ScrollMode.AUTO
    api=AcademyAPI()
    catalog={'grades':[],'subjects':[]}
    account=[None]
    selected_child=[None]
    current_subject=['English']
    current_lesson=[None]
    editing_lesson=[None]
    editing_child=[None]
    quiz_state={'index':0,'answers':[],'feedback':False,'selected':None}
    latest_result=[None]
    screen=['landing']
    root=ft.Column(spacing=16,scroll=ft.ScrollMode.AUTO,expand=True)
    page.add(ft.SafeArea(content=ft.Container(content=root,padding=18)))

    def txt(value,size=16,color=INK,bold=False):
        return ft.Text(str(value),size=size,color=color,
                       weight=ft.FontWeight.BOLD if bold else ft.FontWeight.NORMAL)

    def card(children,bg='#FFFFFF',pad=18):
        return ft.Container(content=ft.Column(controls=children,spacing=12),bgcolor=bg,
                            padding=pad,border_radius=22)

    def btn(label,callback,fill=PURPLE):
        return ft.Container(content=ft.Button(content=label,on_click=callback,bgcolor=fill,
                            color='#FFFFFF'),padding=4)

    def notice(msg,bg='#FFF0D4'):
        return ft.Container(content=txt(msg,14),padding=13,bgcolor=bg,border_radius=14)

    def title(head,sub='',back=None):
        controls=[]
        if back is not None: controls.append(ft.TextButton('← Back',on_click=lambda e:go(back)))
        controls.append(txt(head,29,INK,True))
        if sub: controls.append(txt(sub,15,SOFT))
        return ft.Column(controls=controls,spacing=5)

    def choice_list(options):
        return [ft.DropdownOption(key=str(x),text=str(x)) for x in options]

    def fail(exc):
        root.controls.insert(0,notice(str(exc),'#FFE3E4'))
        page.update()

    def go(name):
        screen[0]=name
        try: render()
        except ApiError as exc:
            root.controls.clear()
            root.controls.extend([title('Something went wrong'),notice(str(exc),'#FFE3E4'),
                                  btn('Try again',lambda e:go(name))])
            page.update()

    def signin(role,data):
        try:
            path={'parent_register':'/auth/parent/register','parent_login':'/auth/parent/login',
                  'child_login':'/auth/child/login'}[role]
            account[0]=api.authenticate(path,data)
            if api.role=='child':
                selected_child[0]=account[0]
                go('dashboard')
            else:
                go('parent_home')
        except ApiError as ex: fail(ex)

    def logout(e=None):
        api.logout()
        account[0]=None
        selected_child[0]=None
        go('landing')

    def child_form(existing=None):
        is_edit=existing is not None
        name=ft.TextField(label='Child display name',value=existing['name'] if is_edit else '',max_length=50)
        username=ft.TextField(label='Child login username (letters, numbers, _)',
                              value=(existing.get('username') or '') if is_edit else '',max_length=30)
        pin=ft.TextField(label='New 4–8 digit PIN' if is_edit else 'Choose a 4–8 digit PIN',
                         password=True,can_reveal_password=True,max_length=8)
        grade=ft.Dropdown(label='Learning level',options=choice_list(catalog['grades']),
                          value=existing['grade'] if is_edit else 'Preschool')
        lang=ft.Dropdown(label='Preferred language',options=choice_list(['English','Urdu']),
                         value=existing['language'] if is_edit else 'English')
        avatar=ft.Dropdown(label='Choose an avatar',options=choice_list(AVATARS),
                           value=existing['avatar'] if is_edit else '🦊')
        def save(e):
            data={'name':(name.value or '').strip(),'username':(username.value or '').strip(),
                  'grade':grade.value,'language':lang.value,'avatar':avatar.value}
            if pin.value: data['pin']=pin.value
            if not is_edit and not pin.value: return fail('Enter a child PIN.')
            try:
                if is_edit: api.call('PUT',f"/children/{existing['id']}",data)
                else: api.call('POST','/children',data)
                go('children')
            except ApiError as ex: fail(ex)
        root.controls.extend([title('Edit child account' if is_edit else 'Add a little learner',
                                    'Each child gets a separate profile and private PIN.',back='children'),
            card([txt('🧸 Student profile',20,INK,True),name,username,pin,grade,lang,avatar,
                  notice('Parent creates the child account. Children use their username and PIN to log in.'),
                  btn('Save child account ✓',save)])])

    def render():
        root.controls.clear()
        s=screen[0]
        if s=='landing':
            root.controls.extend([
                card([txt('🎒 E-LEARNING ACADEMY',15,PURPLE,True),
                      txt('Big adventures for little minds! ✨',31,INK,True),
                      txt('Explore • Learn • Play • Grow',17,SOFT),
                      ft.Row([txt('🔤',34),txt('🧮',34),txt('🌍',34),txt('🚀',34)],
                             alignment=ft.MainAxisAlignment.SPACE_AROUND)],bg='#EAE6FF',pad=22),
                card([txt('👧  I am a student',22,INK,True),
                      txt('Play games, answer quizzes and collect stars.',15,SOFT),
                      btn('Student login →',lambda e:go('child_login'),BLUE)]),
                card([txt('👨‍👩‍👧  I am a parent',22,INK,True),
                      txt('Register your family, create child accounts and manage lessons.',15,SOFT),
                      btn('Parent login',lambda e:go('parent_login')),
                      btn('Create parent account',lambda e:go('parent_register'),GREEN)]),
                txt('Made for Android and Windows • Family learning preview',12,SOFT)])

        elif s=='parent_register':
            name=ft.TextField(label='Parent name',max_length=70)
            email=ft.TextField(label='Email address',max_length=160)
            pwd=ft.TextField(label='Password (10+ characters)',password=True,can_reveal_password=True)
            again=ft.TextField(label='Confirm password',password=True,can_reveal_password=True)
            def register(e):
                if pwd.value!=again.value: return fail('Passwords do not match')
                signin('parent_register',{'name':name.value or '',
                         'email':email.value or '','password':pwd.value or ''})
            root.controls.extend([title('👨‍👩‍👧 Parent registration','Create a family learning account.',back='landing'),
                card([name,email,pwd,again,btn('Create my account',register,GREEN),
                      notice('Use a unique password. This is a local prototype, not an internet-ready account system.')])])

        elif s=='parent_login':
            email=ft.TextField(label='Email address')
            pwd=ft.TextField(label='Password',password=True,can_reveal_password=True)
            root.controls.extend([title('🔐 Parent login','Welcome back! Your learning studio awaits.',back='landing'),
                card([email,pwd,btn('Log in as parent',lambda e:signin('parent_login',
                       {'email':email.value or '','password':pwd.value or ''})),
                       ft.TextButton('New here? Create a parent account',on_click=lambda e:go('parent_register'))])])

        elif s=='child_login':
            username=ft.TextField(label='My username')
            pin=ft.TextField(label='My secret PIN',password=True,can_reveal_password=True,max_length=8)
            root.controls.extend([title('🌈 Student login','Ready to discover something new?',back='landing'),
                card([ft.Row([txt(x,35) for x in ['🦊','🐻','🦋','🚀']],alignment=ft.MainAxisAlignment.SPACE_AROUND),
                      username,pin,btn('🚀 Start my adventure',lambda e:signin('child_login',
                        {'username':username.value or '','pin':pin.value or ''}),BLUE),
                      notice('Ask your parent to create your account if you do not have one.')],bg='#F1EDFF')])

        elif s=='parent_home':
            root.controls.extend([title('👋 Hello, '+account[0]['name']+'!',
                'Welcome to your parent learning studio.'),
                card([txt('👧🧒 Manage children',22,INK,True),
                      txt('Create child accounts, set grades, languages and login PINs.',15,SOFT),
                      btn('Manage student accounts →',lambda e:go('children'),BLUE)],bg='#E7F1FF'),
                card([txt('📚 Lesson library',22,INK,True),
                      txt('Add, revise and preview lessons across all seven subjects.',15,SOFT),
                      btn('Manage lessons →',lambda e:go('parent_lessons'),PURPLE)]),
                card([txt('🏆 Family progress',22,INK,True),
                      btn('View learners →',lambda e:go('children'),GREEN)]),
                btn('Log out',logout,'#78829A')])

        elif s=='children':
            root.controls.extend([title('🧸 My children','Create or edit a learner account.',back='parent_home'),
                                  btn('＋ Register child',lambda e:go('child_edit'),GREEN)])
            for child in api.call('GET','/children'):
                root.controls.append(card([ft.Row([txt(child['avatar'],40),
                            ft.Column([txt(child['name'],19,INK,True),
                                      txt(f"{child['grade']} • {child['language']}",14,SOFT),
                                      txt('Login: '+(child['username'] or 'Setup needed'),13,SOFT)])]),
                        btn('Edit / Set login PIN',lambda e,c=child:edit_child(c),BLUE),
                        btn('View progress',lambda e,c=child:show_progress(c),GREEN)]))

        elif s=='child_edit':
            child_form(editing_child[0])

        elif s=='dashboard':
            child=selected_child[0]
            root.controls.extend([card([txt(f"{child['avatar']} Hi, {child['name']}! 🎉",29,INK,True),
                 txt('Ready to earn some stars today?',17,SOFT),
                 txt(f"🎓 {child['grade']}   •   🗣️ {child['language']}",15,PURPLE,True)],bg='#EAE6FF',pad=22),
                 title('Choose your next adventure','Tap a subject to explore its lessons.')])
            for i,subject in enumerate(catalog['subjects']):
                root.controls.append(ft.Container(content=ft.Column([
                    ft.Row([txt(SUBJECT_ICON.get(subject,'📗'),35),
                            ft.Column([txt(subject,20,INK,True),txt('Tap to explore',13,SOFT)])]),
                    btn('Let’s learn →',lambda e,sub=subject:pick_subject(sub),BLUE if i%2==0 else PURPLE)
                    ],spacing=8),bgcolor=SUBJECT_COLOR[i],border_radius=20,padding=16))
            root.controls.extend([btn('🏆 My stars and progress',lambda e:show_progress(child),GREEN),
                                  btn('Switch account',logout,'#78829A')])

        elif s=='lessons':
            subject=current_subject[0]
            child=selected_child[0]
            root.controls.append(title(SUBJECT_ICON.get(subject,'📚')+' '+subject,
                f"{child['grade']} • Pick a lesson",back='dashboard'))
            items=api.call('GET','/lessons?grade='+quote(child['grade'])+'&subject='+quote(subject))
            if not items: root.controls.append(notice('No lessons here yet. Ask a parent to add one.'))
            for lesson in items:
                root.controls.append(card([txt(lesson['emoji']+' '+lesson['title'],21,INK,True),
                    txt(lesson['explanation'][:150],15,SOFT),
                    txt(f"🧩 {len(lesson['questions'])} practice questions",13,PURPLE,True),
                    btn('Open lesson →',lambda e,l=lesson:pick_lesson(l),BLUE)]))

        elif s=='lesson':
            lesson=current_lesson[0]
            root.controls.extend([title(lesson['emoji']+' '+lesson['title'],
                  lesson['grade']+' • '+lesson['subject'],back='lessons'),
                card([txt('✨ Let’s learn together!',24,INK,True),
                      txt(lesson['explanation'],20,INK),
                      notice('Voice narration and animations are planned for a later update.'),
                      btn(f"🧩 Play the {len(lesson['questions'])}-question challenge!",start_quiz,GREEN)],
                     bg='#EDF8F1')])

        elif s=='quiz':
            lesson=current_lesson[0]
            questions=lesson['questions']
            ix=quiz_state['index']; question=questions[ix]
            root.controls.extend([title('🧩 Brain Challenge',lesson['title'],back='lesson'),
                 card([txt(f'Question {ix+1} of {len(questions)}',16,PURPLE,True),
                       ft.ProgressBar(value=ix/len(questions),color=PURPLE,bgcolor='#E8E5FD'),
                       txt(question['prompt'],24,INK,True)],bg='#ECEAFF')])
            for opt_index,answer in enumerate(question['choices']):
                if quiz_state['feedback']:
                    if opt_index==question['answer']: fill='#DFF5E5'
                    elif opt_index==quiz_state['selected']:fill='#FFE2E5'
                    else: fill='#FFFFFF'
                else:fill='#FFFFFF'
                def choose(e,j=opt_index):
                    if quiz_state['feedback']:return
                    quiz_state['selected']=j
                    quiz_state['feedback']=True
                    quiz_state['answers'].append(j)
                    go('quiz')
                root.controls.append(ft.Container(content=ft.Column([
                    btn(f"{chr(65+opt_index)}   {answer}",choose,PURPLE if not quiz_state['feedback'] else '#66748E')]),
                    bgcolor=fill,border_radius=15,padding=8))
            if quiz_state['feedback']:
                correct=quiz_state['selected']==question['answer']
                root.controls.append(notice('🎉 Amazing! Correct answer!' if correct else
                    '💪 Good try! The correct answer is: '+question['choices'][question['answer']],
                    '#DCF8E8' if correct else '#FFF1D8'))
                root.controls.append(btn('See my results ⭐' if ix==len(questions)-1 else 'Next question →',
                                         finish_or_next,GREEN))

        elif s=='results':
            result=latest_result[0]
            stars=result['stars']
            root.controls.extend([title('🎉 You did it!',back='dashboard'),
                card([txt('⭐'*stars+'☆'*(3-stars),47,GOLD),
                      txt(f"{result['correct']} / {result['total']} correct!",28,INK,True),
                      txt('Every challenge makes your brain stronger. Keep playing!',17,SOFT),
                      btn('🔄 Try these questions again',start_quiz,BLUE),
                      btn('📚 Choose another lesson',lambda e:go('lessons'),PURPLE),
                      btn('🏠 Home',lambda e:go('dashboard'),GREEN)],bg='#FFF6E1')])

        elif s=='progress':
            child=selected_child[0]
            progress=api.call('GET',f"/progress/{child['id']}")
            back='children' if api.role=='parent' else 'dashboard'
            root.controls.extend([title('🏆 '+child['name']+'’s achievements',back=back),
                card([txt(f"⭐ Total stars: {progress['total_stars']}",25,GOLD,True),
                      txt(f"📚 Lessons completed: {progress['completed_lessons']}",19,INK,True),
                      txt(f"🧩 Quiz attempts: {progress['total_attempts']}",19,INK,True)],bg='#FFF4DA')])
            for attempt in progress['attempts'][:40]:
                root.controls.append(card([txt(attempt['title'],17,INK,True),
                    txt(f"{attempt['subject']} • {attempt['correct']} / {attempt['total']} correct",14,SOFT)]))

        elif s=='parent_lessons':
            root.controls.extend([title('📚 Parent lesson editor','Build fun activities for every grade.',back='parent_home'),
                                  btn('＋ Create lesson',lambda e:edit_lesson(None),GREEN)])
            items=api.call('GET','/lessons')
            root.controls.append(txt(f'{len(items)} lessons available',14,SOFT))
            for lesson in items:
                root.controls.append(card([txt(lesson['emoji']+' '+lesson['title'],18,INK,True),
                    txt(f"{lesson['grade']} • {lesson['subject']} • {len(lesson['questions'])} questions",13,SOFT),
                    btn('Edit lesson',lambda e,l=lesson:edit_lesson(l),BLUE)]))

        elif s=='lesson_edit':
            existing=editing_lesson[0]
            head='Edit lesson' if existing else 'Create your lesson'
            title_input=ft.TextField(label='Lesson title',value=existing['title'] if existing else '')
            explanation=ft.TextField(label='Explanation / instructions',multiline=True,min_lines=3,max_lines=7,
                                     value=existing['explanation'] if existing else '')
            grade=ft.Dropdown(label='Grade',options=choice_list(catalog['grades']),
                              value=existing['grade'] if existing else 'Preschool')
            subject=ft.Dropdown(label='Subject',options=choice_list(catalog['subjects']),
                                value=existing['subject'] if existing else 'English')
            emoji=ft.TextField(label='Emoji',value=existing['emoji'] if existing else '📚')
            questions_controls=ft.Column(spacing=12)
            entries=[]
            def append_question(q=None):
                if len(entries)>=30:return fail('A lesson can have up to 30 questions.')
                q=q or {'prompt':'','choices':['','',''],'answer':0}
                question=ft.TextField(label=f'Question {len(entries)+1}',value=q['prompt'])
                option_fields=[ft.TextField(label=f'Answer option {i+1}',
                     value=q['choices'][i] if i<len(q['choices']) else '') for i in range(max(3,len(q['choices'])))]
                correct=ft.Dropdown(label='Correct answer number',
                                    options=choice_list([str(i+1) for i in range(len(option_fields))]),
                                    value=str(q['answer']+1))
                entries.append((question,option_fields,correct))
                questions_controls.controls.append(card([question,*option_fields,correct],bg='#F0EEFF'))
            for item in (existing['questions'] if existing else []):append_question(item)
            if not entries:append_question()
            def save(e):
                qs=[]
                for prompt,options,answer in entries:
                    opts=[(x.value or '').strip() for x in options]
                    if not (prompt.value or '').strip():return fail('Every question needs a prompt.')
                    if any(not x for x in opts):return fail('Fill all answer choices.')
                    qs.append({'prompt':prompt.value.strip(),'choices':opts,'answer':int(answer.value)-1})
                data={'title':(title_input.value or '').strip(),'explanation':(explanation.value or '').strip(),
                      'grade':grade.value,'subject':subject.value,'emoji':emoji.value or '📚','questions':qs}
                try:
                    if existing:api.call('PUT',f"/lessons/{existing['id']}",data)
                    else:api.call('POST','/lessons',data)
                    go('parent_lessons')
                except ApiError as exc:fail(exc)
            def delete(e):
                try:
                    api.call('DELETE',f"/lessons/{existing['id']}")
                    go('parent_lessons')
                except ApiError as exc:fail(exc)
            root.controls.extend([title(head,'Write a lesson and add questions.',back='parent_lessons'),
                card([title_input,grade,subject,emoji,explanation]),
                txt('🧩 Questions',24,INK,True),questions_controls,
                btn('＋ Add another question',lambda e:(append_question(),page.update()),BLUE),
                btn('Save lesson ✓',save,GREEN)])
            if existing:
                root.controls.append(notice('Deleting a lesson also removes its saved quiz attempts.'))
                root.controls.append(btn('Delete lesson',delete,PINK))
        page.update()

    def edit_child(child):
        editing_child[0]=child
        go('child_edit')
    def pick_subject(subject):
        current_subject[0]=subject
        go('lessons')
    def pick_lesson(lesson):
        current_lesson[0]=lesson
        go('lesson')
    def show_progress(child):
        selected_child[0]=child
        go('progress')
    def edit_lesson(lesson):
        editing_lesson[0]=lesson
        go('lesson_edit')
    def start_quiz(e=None):
        quiz_state.update(index=0,answers=[],feedback=False,selected=None)
        go('quiz')
    def finish_or_next(e):
        if quiz_state['index']+1<len(current_lesson[0]['questions']):
            quiz_state['index']+=1
            quiz_state['feedback']=False
            quiz_state['selected']=None
            go('quiz')
        else:
            try:
                latest_result[0]=api.call('POST','/attempts',{'lesson_id':current_lesson[0]['id'],
                                                              'answers':quiz_state['answers']})
                go('results')
            except ApiError as exc:fail(exc)

    try:catalog.update(api.call('GET','/catalog'))
    except ApiError as exc:
        root.controls.extend([title('Could not connect'),notice(str(exc),'#FFE3E4'),
                              btn('Retry',lambda e:go('landing'))])
        page.update()
        return
    go('landing')

if __name__=='__main__':
    ft.run(main)
