"""E-Learning Academy Flet client, Version 0.1 (family development preview).
Run the FastAPI backend first. Never expose this prototype API to the internet.
"""
import flet as ft

try:
    from .api import AcademyAPI, ApiError
except ImportError:
    from api import AcademyAPI, ApiError

APP_BG = '#F7F7FF'
NAVY = '#203153'
PURPLE = '#6753CF'
CARDS = '#FFFFFF'
AVATARS = ['🌟','🦊','🐻','🐼','🐱','🦁','🚀','🦋']


def main(page: ft.Page):
    page.title = 'E-Learning Academy'
    page.bgcolor = APP_BG
    page.padding = 16
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.LIGHT
    api = AcademyAPI()
    selected_student = None
    current_lesson = None
    screen = 'welcome'
    catalog = {'grades':[],'subjects':[]}

    content = ft.Column(spacing=14, expand=True)
    page.add(ft.SafeArea(content=content))

    def banner(message, color='#FFF0CD'):
        return ft.Container(content=ft.Text(message, color=NAVY, size=14),bgcolor=color,padding=12,border_radius=12)

    def header(title, subtitle=None, back=None):
        controls=[]
        if back:
            controls.append(ft.TextButton('← Back',on_click=lambda e: navigate(back)))
        controls.append(ft.Text(title,size=27,weight=ft.FontWeight.BOLD,color=NAVY))
        if subtitle:
            controls.append(ft.Text(subtitle,size=14,color='#63728E'))
        return ft.Column(controls,spacing=6)

    def panel(children, color=CARDS):
        return ft.Container(content=ft.Column(children,spacing=12), bgcolor=color,
                            padding=18,border_radius=18)

    def button(label, handler, primary=True):
        return ft.Button(content=label,on_click=handler,
                         bgcolor=PURPLE if primary else '#E9E6FF',
                         color='#FFFFFF' if primary else NAVY)

    def show_error(exc):
        content.controls.insert(0,banner(str(exc),'#FFE2E2'))
        page.update()

    def navigate(where):
        nonlocal screen
        screen=where
        try:
            render()
        except ApiError as exc:
            content.controls.clear()
            content.controls.append(header('Connection problem'))
            content.controls.append(banner(str(exc),'#FFE2E2'))
            content.controls.append(button('Try again',lambda e: navigate(where)))
            page.update()

    def option_list(values):
        return [ft.DropdownOption(key=v,text=v) for v in values]

    def render():
        content.controls.clear()
        if screen == 'welcome':
            content.controls.extend([
                header('🎒 E-Learning Academy','Explore • Play • Learn'),
                panel([ft.Text('Hi, little learners! 👋',size=24,weight=ft.FontWeight.BOLD,color=NAVY),
                       ft.Text('Pick your profile to begin your next adventure.',size=16)]),
            ])
            students=api.call('GET','/students')
            for student in students:
                content.controls.append(panel([
                    ft.Row([ft.Text(student['avatar'],size=36),ft.Column([
                        ft.Text(student['name'],weight=ft.FontWeight.BOLD,size=19),
                        ft.Text(f"{student['grade']} · {student['language']}",size=12,color='#63728E')])]),
                    button('Start learning',lambda e,s=student: choose_student(s))
                ]))
            content.controls.extend([
                button('＋ Add child profile',lambda e:navigate('add_student'),False),
                button('🔒 Parent lesson editor',lambda e:navigate('parent_login'),False),
                ft.Text('🔐 Family development preview. Use only on a trusted local network.',size=12,color='#63728E')
            ])

        elif screen == 'add_student':
            name = ft.TextField(label='Child name / nickname',max_length=50)
            grade = ft.Dropdown(label='Grade',options=option_list(catalog['grades']),value='Preschool')
            language = ft.Dropdown(label='Preferred language',options=option_list(['English','Urdu']),value='English')
            avatar=ft.Dropdown(label='Choose picture/avatar',options=option_list(AVATARS),value='🌟')
            def save(e):
                if not (name.value or '').strip(): return show_error('Please enter a name.')
                try:
                    api.call('POST','/students',{'name':name.value,'grade':grade.value,
                                         'language':language.value,'avatar':avatar.value})
                    navigate('welcome')
                except ApiError as ex:show_error(ex)
            content.controls.extend([header('Add a little learner',back='welcome'),
                                     panel([name,grade,language,avatar,button('Save profile',save)])])

        elif screen == 'dashboard':
            student=selected_student
            content.controls.extend([
                header(f"{student['avatar']} Hello, {student['name']}!",'Ready for a learning adventure?',back='welcome'),
                panel([ft.Text('Choose a subject 📚',size=20,weight=ft.FontWeight.BOLD),
                       ft.Text(f"Your level: {student['grade']}  •  Language: {student['language']}")]),
            ])
            for subject in catalog['subjects']:
                content.controls.append(button(f'📘 {subject}',lambda e,s=subject: choose_subject(s),False))
            content.controls.append(button('🏆 My progress',lambda e:navigate('progress')))
            content.controls.append(button('Switch student',lambda e:navigate('welcome'),False))

        elif screen == 'lessons':
            subject=chosen_subject[0]
            content.controls.append(header(f'📚 {subject}',f"{selected_student['grade']} lessons",back='dashboard'))
            lessons=api.call('GET','/lessons?grade='+quote(selected_student['grade'])+'&subject='+quote(subject))
            if not lessons:
                content.controls.append(banner('No lessons here yet. Parents can add lessons in the editor.'))
            for lesson in lessons:
                content.controls.append(panel([
                    ft.Text(lesson['emoji']+' '+lesson['title'],size=18,weight=ft.FontWeight.BOLD),
                    ft.Text(lesson['explanation'][:105]+'…' if len(lesson['explanation'])>105 else lesson['explanation'],size=14),
                    button('Open lesson →',lambda e,l=lesson:choose_lesson(l))
                ]))

        elif screen == 'lesson':
            lesson=current_lesson
            content.controls.extend([
                header(f"{lesson['emoji']} {lesson['title']}",f"{lesson['grade']} • {lesson['subject']}",back='lessons'),
                panel([ft.Text('Let’s learn! ✨',size=22,weight=ft.FontWeight.BOLD),
                       ft.Text(lesson['explanation'],size=19,color=NAVY,selectable=True),
                       banner('Narration/audio assets will be introduced in the next build. This version provides readable instructions.'),
                       button('Take the quiz 🧩',lambda e:navigate('quiz'))])
            ])

        elif screen == 'quiz':
            questions=current_lesson['questions']
            answers=[None for _ in questions]
            content.controls.append(header('🧩 Knowledge Challenge',current_lesson['title'],back='lesson'))
            for index, question in enumerate(questions):
                group=ft.RadioGroup(content=ft.Column([
                    ft.Radio(value=str(i),label=choice)
                    for i,choice in enumerate(question['choices'])
                ]))
                def on_select(e,idx=index,g=group):
                    answers[idx]=int(g.value) if g.value is not None else None
                group.on_change=on_select
                content.controls.append(panel([
                    ft.Text(f"Question {index+1}: {question['prompt']}",size=18,weight=ft.FontWeight.BOLD),group
                ]))
            def submit(e):
                if any(answer is None for answer in answers):
                    return show_error('Please answer every question first.')
                try:
                    result=api.call('POST','/attempts',{'student_id':selected_student['id'],
                                        'lesson_id':current_lesson['id'],'answers':answers})
                    score[0]=result
                    navigate('result')
                except ApiError as ex: show_error(ex)
            content.controls.append(button('Check my answers ⭐',submit))

        elif screen == 'result':
            result=score[0]
            content.controls.extend([header('🎉 Great effort!',back='dashboard'),panel([
                ft.Text('⭐' * result['stars']+'☆'*(3-result['stars']),size=46),
                ft.Text(f"You got {result['correct']} out of {result['total']} correct!",size=23,weight=ft.FontWeight.BOLD),
                ft.Text('Keep practising. Every try helps you grow!'),
                button('Try again',lambda e:navigate('quiz'),False),
                button('Choose another lesson',lambda e:navigate('lessons'))
            ])])

        elif screen == 'progress':
            p=api.call('GET',f"/progress/{selected_student['id']}")
            content.controls.extend([header('🏆 My Learning Progress',selected_student['name'],back='dashboard'),
                panel([ft.Text(f"Completed lessons: {p['completed_lessons']}",size=19),
                       ft.Text(f"Quiz attempts: {p['total_attempts']}",size=19)])])
            for a in p['attempts'][:30]:
                content.controls.append(panel([ft.Text(f"{a['title']} — {a['correct']}/{a['total']}"),
                                               ft.Text(a['subject'],size=12,color='#63728E')]))

        elif screen == 'parent_login':
            pin=ft.TextField(label='Parent PIN',password=True,can_reveal_password=True)
            def login(e):
                try:
                    api.login(pin.value or '')
                    navigate('parent')
                except ApiError as ex:show_error(ex)
            content.controls.extend([header('🔒 Parent area',back='welcome'),
                    panel([ft.Text('Enter the parent PIN to manage lessons.'),pin,
                           button('Unlock editor',login)])])

        elif screen == 'parent':
            content.controls.extend([header('🛠️ Manage lessons',back='welcome'),
                                     button('＋ Create new lesson',lambda e:open_editor(None))])
            for lesson in api.call('GET','/lessons'):
                content.controls.append(panel([
                    ft.Text(f"{lesson['emoji']} {lesson['title']}",weight=ft.FontWeight.BOLD),
                    ft.Text(f"{lesson['grade']} • {lesson['subject']}",size=12),
                    button('Edit lesson',lambda e,l=lesson:open_editor(l),False)
                ]))

        elif screen == 'editor':
            existing=editing_lesson[0]
            title=ft.TextField(label='Lesson title',value=existing['title'] if existing else '')
            explanation=ft.TextField(label='Explanation / lesson content',value=existing['explanation'] if existing else '',multiline=True,min_lines=3,max_lines=7)
            grade=ft.Dropdown(label='Grade',options=option_list(catalog['grades']),value=existing['grade'] if existing else 'Preschool')
            subject=ft.Dropdown(label='Subject',options=option_list(catalog['subjects']),value=existing['subject'] if existing else 'English')
            emoji=ft.TextField(label='Lesson emoji',value=existing['emoji'] if existing else '📚')
            existing_questions=existing['questions'] if existing else []
            question_fields=[]
            questions_column=ft.Column(spacing=12)

            def add_question(q=None):
                q=q or {'prompt':'','choices':['','',''],'answer':0}
                prompt=ft.TextField(label='Question',value=q['prompt'])
                choices=[ft.TextField(label=f'Choice {i+1}',value=q['choices'][i] if i<len(q['choices']) else '') for i in range(3)]
                correct=ft.Dropdown(label='Correct choice',options=option_list(['1','2','3']),value=str(q['answer']+1))
                question_fields.append((prompt,choices,correct))
                questions_column.controls.append(panel([prompt,*choices,correct],color='#F1F0FF'))

            for q in existing_questions:
                # The first release supports 3 choices in the editor. Additional choices in
                # existing lessons are retained by API until they are explicitly edited.
                add_question(q)
            if not existing_questions:
                add_question()

            def save(e):
                qs=[]
                for prompt,choices,correct in question_fields:
                    qs.append({'prompt':(prompt.value or '').strip(),
                               'choices':[(c.value or '').strip() for c in choices],
                               'answer':int(correct.value or '1')-1})
                data={'grade':grade.value,'subject':subject.value,'title':(title.value or '').strip(),
                      'explanation':(explanation.value or '').strip(),'emoji':emoji.value or '📚','questions':qs}
                try:
                    if existing:
                        api.call('PUT',f"/lessons/{existing['id']}",data,admin=True)
                    else:
                        api.call('POST','/lessons',data,admin=True)
                    navigate('parent')
                except ApiError as ex:show_error(ex)
            def delete(e):
                if existing:
                    try:
                        api.call('DELETE',f"/lessons/{existing['id']}",admin=True)
                        navigate('parent')
                    except ApiError as ex:show_error(ex)
            content.controls.extend([header('Edit lesson' if existing else 'Create a lesson',back='parent'),
                panel([title,grade,subject,emoji,explanation]),
                ft.Text('Quiz questions',size=20,weight=ft.FontWeight.BOLD),
                questions_column,
                button('＋ Add question',lambda e:(add_question(),page.update()),False),
                button('Save lesson',save),
            ])
            if existing:
                content.controls.append(ft.Text('Deleting a lesson also deletes its quiz attempts.',size=12,color='#A04444'))
                content.controls.append(button('Delete lesson',delete,False))
        page.update()

    def choose_student(student):
        nonlocal selected_student
        selected_student=student
        navigate('dashboard')
    chosen_subject=['English']
    def choose_subject(subject):
        chosen_subject[0]=subject
        navigate('lessons')
    def choose_lesson(lesson):
        nonlocal current_lesson
        current_lesson=lesson
        navigate('lesson')
    editing_lesson=[None]
    def open_editor(lesson):
        editing_lesson[0]=lesson
        navigate('editor')
    score=[None]
    from urllib.parse import quote
    try:
        catalog.update(api.call('GET','/catalog'))
    except ApiError as exc:
        content.controls.append(banner(str(exc),'#FFE2E2'))
        content.controls.append(button('Retry connection',lambda e:navigate('welcome')))
        page.update()
        return
    navigate('welcome')

if __name__ == '__main__':
    ft.run(main)
