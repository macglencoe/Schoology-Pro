import os
import schoolopy
import requests
from bs4 import BeautifulSoup
import random

class Course:
    def __init__(self,data,session_state):
        self.title = data['section_title']
        self.id = data['id']
        self.periods = [str(x) for x in data['grading_periods']]
        self.metadata = data
        self.forbidden = False
        #_courses[self.id] = self
        session_state['loaded_courses'].append(self.title)
        session_state['_courses'][self.id] = self
    def even_catweights(self,ss):
        categories = [
            cat for cat in ss._categories.values() if
            cat.course_id == self.id and
            cat.weight == 0
        ]
        if len(categories) == 0:
            return
        new_weight = 100 / len(categories)
        for cat in categories:
            cat.weight = new_weight

class Period:
    def __init__(self,data,session_state):
        self.id = data['period_id'].replace('p','')
        self.title = data['period_title']
        self.metadata = data
        self.modified = False
        #_periods[self.id] = self
        session_state['_periods'][self.id] = self

class Category:
    def __init__(self,data,session_state):
        self.id = data['id']
        self.title = data['title']
        self.course_id = data['realm_id']
        self.weight = data['weight']
        if 'calculation_type' in data:
            self.method = data['calculation_type']
        else:
            self.method = 2
        self.metadata = data
        #_categories[self.id] = self
        session_state['_categories'][self.id] = self

class Assignment:
    def __init__(self,data,section_id,period_id,session_state):
        sc = session_state['sc']
        self.enrollment_id = data['enrollment_id']
        self.section_id = section_id
        self.id = data['assignment_id']
        self.grade = data['grade']
        self.grade_original = data['grade']
        self.max = data['max_points']
        self.max_original = data['max_points']
        if self.max and self.grade:
            self.percent = round(
                self.grade / self.max, 3
            )
        elif self.grade is 0:
            self.percent = 0
        else:
            self.percent = None
        
        #if self.max is None:
            #self.exception = "Not yet assigned"
        #elif self.grade is None:
            #self.exception = "Excused"
        #elif self.exception and self.grade == 0:
            #self.exception = "Missing"
        if 'web_url' in data.keys():
            self.url = data['web_url'].replace('app','bcs')
        self.category = data['category_id']
        try:
            metadata = sc.get_assignment(self.section_id,self.id)
            self.title = metadata['title']
            self.period = metadata['grading_period']
        except requests.exceptions.HTTPError:
            self.title = self.id
            self.period,sep,tail = period_id.partition('p')
        #_assignments[self.id] = self
        session_state['_assignments'][self.id] = self
    def reset(self):
        self.grade = self.grade_original
        self.max = self.max_original

class DemoCourse:
    def __init__(self,title,id,ss):
        self.title = title
        self.id = id
        self.periods = ['1','2','3','4']
        ss['loaded_democourses'].append(self.title)
        ss['_democourses'][self.id] = self
    def even_catweights(self,ss):
        categories = [
            cat for cat in ss._democategories.values() if
            cat.course_id == self.id and
            cat.weight == 0
        ]
        if len(categories) == 0:
            return
        new_weight = 100 / len(categories)
        for cat in categories:
            cat.weight = new_weight

class DemoPeriod:
    def __init__(self,id,title,ss):
        self.id = id
        self.title = title
        if self.id in ss['_demoperiods']:
            self.id =+ '*'
        ss['_demoperiods'][self.id] = self

class DemoCategory:
    def __init__(
            self,id,title,course_id,
            weight,method,ss
        ):
        self.id = id
        if id in session_state['_democategories']:
            return
        self.title = title
        self.course_id = course_id
        self.weight = weight
        self.method = method
        session_state['_democategories'][self.id] = self

class DemoAssignment:
    def __init__(
            self,id,title,grade,max,
            section_id,period_id,category_id,
            ss
        ):
        self.id = id
        self.title = title
        self.grade = grade
        self.grade_original = grade
        self.max = max
        self.max_original = max
        self.section_id = section_id
        self.period = period_id
        self.category = category_id
        if self.max and self.grade:
            self.percent = round(
                self.grade / self.max, 3
            )
        elif self.grade is 0:
            self.percent = 0
        else:
            self.percent = None
        ss['_demoassignments'][self.id] = self
    def reset(self):
        self.grade = self.grade_original
        self.max = self.max_original

def loadcourse(session_state):
    sc = session_state['sc']
    olist = session_state['olist']
    _courses = session_state['_courses']
    _periods = session_state['_periods']
    sel_string = session_state['selected_course']
    loaded_courses = session_state['loaded_courses']
    matches = []
    returncourses = []

    if sel_string in loaded_courses:
        return reloadcourse(sel_string, session_state)

    for c in olist:
        coursetitle = sc.get_section(c['section_id'])['section_title']
        if sel_string in coursetitle or coursetitle in sel_string:
            matches.append(c)
    print("                  ",end='\r')
    if len(matches) == 0:
        print(f"Course \"{sel_string}\" couldn't be found")
        return
    for course in matches:
        if course['section_id'] not in _courses.keys():
            Course(
                sc.get_section(course['section_id']),
                session_state
            )
        returncourses.append(
            _courses[course['section_id']]
        )
        for period in course['period']:
            if period['period_id'] not in _periods.keys():
                Period(period, session_state)
            for asgn in period['assignment']:
                Assignment(
                    asgn,
                    course['section_id'], period['period_id'],
                    session_state
                )
        try:
            sc.get_grading_categories(course['section_id'])
        except requests.exceptions.HTTPError:
            return
        for category in sc.get_grading_categories(course['section_id']):
            Category(category,session_state)
    return returncourses 

def demoload(
        session_state,catcount=3,asgncount=5
    ):
    _courses = session_state['_democourses']
    _periods = session_state['_demoperiods']
    sel_string = session_state['selected_democourse']
    loaded_courses = session_state['loaded_democourses']
    matches = []
    returncourses = []
    course_titles = session_state['democourselist']
    courses = [(title,str(random.randrange(1,100))) for title in course_titles]

    periods = ["1st Quarter","2nd Quarter","3rd Quarter","4th Quarter"]
    
    categories = [
        (f"Category {x}",str(random.randrange(1,10000))) for x in range(catcount)
    ]

    assignments = [
        (f"Assignment {x}",str(random.randrange(1,10000))) for x in range(asgncount)
    ]
    if sel_string in loaded_courses:
        return demoreloadcourse(sel_string, session_state)

    for c in courses:
        coursetitle = c[0]
        if sel_string in coursetitle or coursetitle in sel_string:
            matches.append(c)
    if len(matches) == 0:
        print(f"Course \"{sel_string}\" couldn't be found")
        return
    for sec in matches:
        categories = [
            (f"Category {x}",random.randrange(1,10000)) for x in range(catcount)
        ]

        if sec[1] not in _courses.keys():
            DemoCourse(
                sec[0],sec[1],
                session_state
            )
        returncourses.append(
            _courses[sec[1]]
        )
        for x,per in enumerate(periods):
            if str(x+1) not in _periods.keys():
                DemoPeriod(str(x+1),per,session_state)
            continue
            totalweight = 100   
            for cat in categories:
                isweighted = random.choice([True,False])
                if isweighted:
                    weight = random.randint(1,totalweight)
                    totalweight -= weight
                else:
                    weight = 0
                DemoCategory(
                    cat[1],cat[0],sec[1],
                    weight, random.choice([1,2]),
                    session_state
                )
                for asg in assignments:
                    max = random.randrange(1,101)
                    grade = random.randint(0,max)
                    DemoAssignment(
                        asg[1],asg[0],grade,max,
                        sec[1], str(x+1), cat[1],
                        session_state
                    )
    return returncourses

def reloadcourse(sel_string, session_state):
    olist = session_state['olist']
    _courses = session_state['_courses']
    returncourses = []
    for c in _courses.values():
        if c.title == sel_string:
            returncourses.append(c)
    return returncourses
    
def demoreloadcourse(sel_string, session_state):
    _courses = session_state['_democourses']
    returncourses = []
    for c in _courses.values():
        if c.title == sel_string:
            returncourses.append(c)
    return returncourses

apikey = '65d4d1f05710a0eb66658122d7cc426e062100b60'
apisecret = 'f90c6f8faa564767831e6c4c41acb4f4'

def twolegged(session_state):
    auth = schoolopy.Auth(apikey,apisecret)
    sc = schoolopy.Schoology(
        auth
    )
    me = sc.get_me()
    olist = sc.get_user_grades(me['uid'])
    courselist=[]
    for c in olist:
        section = sc.get_section(c['section_id'])
        sectiontitle = section['section_title']
        courselist.append(sectiontitle)
    session_state['logged_in'] = True
    session_state['auth'] = auth
    session_state['sc'] = sc
    session_state['me'] = me
    session_state['olist'] = olist
    session_state['courselist'] = courselist
    session_state['_courses'] = {}
    session_state['_periods'] = {}
    session_state['_categories'] = {}
    session_state['_assignments'] = {}
    session_state['loaded_courses'] = []
    

def threelegged(session_state,progbar):
    auth = session_state['auth']
    if not auth.authorize():
        raise SystemExit('Account was not authorized.')
    sc = schoolopy.Schoology(auth)
    me = sc.get_me()
    olist = sc.get_user_grades(me['uid'])
    courselist=[]
    progstep = 1 / len(olist)
    progress = 0.0
    for c in olist:
        section = sc.get_section(c['section_id'])
        sectiontitle = section['section_title']
        courselist.append(sectiontitle)
        progress += progstep
        progbar.progress(progress)
    session_state['logged_in'] = True
    session_state['sc'] = sc
    session_state['me'] = me
    session_state['olist'] = olist
    session_state['courselist'] = courselist
    session_state['_courses'] = {}
    session_state['_periods'] = {}
    session_state['_categories'] = {}
    session_state['_assignments'] = {}
    session_state['loaded_courses'] = []
    save_userstate(session_state)

def demosetup(session_state):
    course_titles = [
        "PERSONAL FINANCE", "COMP SCI", "GRAPHIC DESIGN",
        "ENGLISH XII", "CREATIVE WRITING", "HOME ECONOMICS",
        "SPANISH II", "FRENCH II", "ALGEBRA II", "CALCULUS",
        "GEOMETRY", "BAND", "ORCHESTRA", "DRAMA",
        "PHYSICAL EDUCATION", "BIOLOGY", "PHYSICS",
        "PSYCHOLOGY", "CIVICS/GOVT", "WORLD HISTORY",
        "PHOTOGRAPHY", "WOODWORKING", "AGRICULTURE"
    ]
    session_state['_democourses'] = {}
    session_state['_demoperiods'] = {}
    session_state['_democategories'] = {}
    session_state['_demoassignments'] = {}
    session_state['loaded_democourses'] = []
    session_state['democourselist'] = course_titles
    session_state['demo_generated'] = True

def get_auth():
    auth = schoolopy.Auth(
        apikey, apisecret, three_legged = True,
        domain = school_domain
    )
    return auth
    #session_state['auth_url'] = auth.request_authorization(callback_url='https://schoology-streamlit.macglencoe.repl.co/')

def test_auth(session_state):
    try:
        session_state['sc'].get_me()
    except Exception as err:
        print(err)
        return False
    return True


def save_userstate(session_state):
    sc = schoolopy.Schoology(session_state['auth'])
    uid = sc.get_me()['uid']

    #user_states[uid] = {key:val for (key,val) in session_state.items()}
    user_states[uid] = {
        'olist' : session_state.olist,
        'period_mod' : session_state.period_mod,
        'loaded_courses' : session_state.loaded_courses,
        'me' : session_state.me,
        'period_dfs': session_state.period_dfs,
        'period_grades': session_state.period_grades,
        '_assignments' : session_state._assignments,
        '_categories' : session_state._categories,
        '_periods' : session_state._periods,
        '_courses' : session_state._courses,
        'courselist' : session_state.courselist,
        'dataframes' : session_state.dataframes,
        'logged_in' : session_state.logged_in,
        'sc' : sc
    }

def get_userstate(session_state):
    auth = session_state['auth']
    sc = schoolopy.Schoology(auth)
    me = sc.get_me()
    uid = me['uid']

    if uid in user_states:
        return user_states[uid]
    return False

def del_userstate(uid):
    if uid in user_states.keys():
        user_states.pop(uid)
        return True
    return False

cookie_datas = {}
user_cookies = {}
user_states = {}

school_domain = 'https://bcs.schoology.com'
