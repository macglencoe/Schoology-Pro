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
        

class Period:
    def __init__(self,data,session_state):
        self.id = data['period_id'].replace('p','')
        self.title = data['period_title']
        self.metadata = data
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
    def __init__(self,data,section_id,session_state):
        sc = session_state['sc']
        self.enrollment_id = data['enrollment_id']
        self.section_id = section_id
        self.id = data['assignment_id']
        self.grade = data['grade']
        #self.exception = data['exception']
        self.max = data['max_points']
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
            del self
            return
        #_assignments[self.id] = self
        session_state['_assignments'][self.id] = self


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
                    course['section_id'],session_state
                )
        try:
            sc.get_grading_categories(course['section_id'])
        except requests.exceptions.HTTPError:
            return
        for category in sc.get_grading_categories(course['section_id']):
            Category(category,session_state)
    return returncourses


    
def reloadcourse(sel_string, session_state):
    olist = session_state['olist']
    _courses = session_state['_courses']
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

def save_cookie(session_state):
    uid = session_state.me['uid']
    session_id = session_state['session_id']
    if uid in user_cookies:
        del cookie_datas[user_cookies[uid]]
        del user_cookies[uid]
    user_cookies[uid] = session_id
    cookie_datas[session_id] = session_state

def get_session(session_id):
    if session_id in cookie_datas:
        return cookie_datas[session_id]
    return False

def save_userstate(session_state):
    sc = schoolopy.Schoology(session_state['auth'])
    uid = sc.get_me()['uid']

    user_states[uid] = {key:val for (key,val) in session_state.items()}

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
    else:
        return False

cookie_datas = {}
user_cookies = {}
user_states = {}

school_domain = 'https://bcs.schoology.com'