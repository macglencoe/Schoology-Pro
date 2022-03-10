import os
import schoolopy
import requests
from bs4 import BeautifulSoup

class Course:
    def __init__(self,data):
        self.title = data['section_title']
        self.id = data['id']
        #self.periods = data['grading_periods']
        self.periods = [str(x) for x in data['grading_periods']]
        self.metadata = data
        self.forbidden = False
        _courses[self.id] = self
        

class Period:
    def __init__(self,data):
        self.id = data['period_id'].replace('p','')
        self.title = data['period_title']
        self.metadata = data
        _periods[self.id] = self

class Category:
    def __init__(self,data):
        self.id = data['id']
        self.title = data['title']
        self.course_id = data['realm_id']
        self.weight = data['weight']
        self.metadata = data
        _categories[self.id] = self

class Assignment:
    def __init__(self,data,section_id):
        self.enrollment_id = data['enrollment_id']
        self.section_id = section_id
        self.id = data['assignment_id']
        self.grade = data['grade']
        self.exception = data['exception']
        self.max = data['max_points']
        if self.max is None:
            self.exception = "Not yet assigned"
        elif self.grade is None:
            self.exception = "Excused"
        elif self.exception and self.grade == 0:
            self.exception = "Missing"
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
        _assignments[self.id] = self


def loadcourse(sel_string):
    matches = []
    for c in olist:
        print("Loading courses ",end='')
        advspinner()
        coursetitle = sc.get_section(c['section_id'])['section_title']
        if sel_string in coursetitle or coursetitle in sel_string:
            matches.append(c)
    print("                  ",end='\r')
    if len(matches) == 0:
        print(f"Course \"{sel_string}\" couldn't be found")
        return
    returncourses = []
    for course in matches:
        if course['section_id'] not in _courses.keys():
            Course(sc.get_section(course['section_id']))
        returncourses.append(_courses[course['section_id']])
        for period in course['period']:
            if period['period_id'] not in _periods.keys():
                Period(period)
            for asgn in period['assignment']:
                print("Loading grades ",end='')
                advspinner()
                Assignment(asgn,course['section_id'])
        try:
            sc.get_grading_categories(course['section_id'])
        except requests.exceptions.HTTPError:
            return
        for category in sc.get_grading_categories(course['section_id']):
            Category(category)
    return returncourses


spinner = '|'
def advspinner():
    global spinner
    spinnerlist = ['|','/','-','\\']
    index = spinnerlist.index(spinner)
    if index == 3:
        index = -1
    spinner = spinnerlist[index+1]
    print(spinner+'\r',flush=True,end='')



apikey = '65d4d1f05710a0eb66658122d7cc426e062100b60'
apisecret = 'f90c6f8faa564767831e6c4c41acb4f4'

def twolegged(key,secret):
    global sc
    auth = schoolopy.Auth(key,secret)
    if not auth.authorize():
        raise SystemExit('Key or secret is invalid')
    sc = schoolopy.Schoology(
        auth
    )
    
    

def threelegged():
    global sc
    global me
    global olist
    global courselist
    if authurl is not None:
        pass
        #print("Click the following link to authorize this app with Schoology:")
        #print(authurl)
    if not auth.authorize():
        raise SystemExit('Account was not authorized.')
    sc = schoolopy.Schoology(auth)
    me = sc.get_me()['uid']
    olist = sc.get_user_grades(me)
    courselist=[]
    for c in olist:
        section = sc.get_section(c['section_id'])
        sectiontitle = section['section_title']
        courselist.append(sectiontitle)
        
    
olist=[]
DOMAIN = 'https://bcs.schoology.com'
auth = schoolopy.Auth(
    apikey,apisecret, three_legged=True,
    domain = DOMAIN
)
authurl = auth.request_authorization()

#sc = threelegged(apikey,apisecret)

#sc = twolegged(apikey,apisecret)


#print('You are logged in as %s' % sc.get_me().name_display)

_courses = {}
_periods = {}
_categories = {}
_assignments = {}

#me = sc.get_me()['uid']
#olist = sc.get_user_grades(me)
#print("Initializing...",end='\r')
#loadcourse('ENG LA 12')

#print('\r',end='')
#for course in _courses.values():
#    print(course.title)
#for asgn in _assignments.values():
#    print(asgn.title,end='')
#    print(f' {asgn.grade}/{asgn.max}')
#    if asgn.exception:
#        print(asgn.exception)