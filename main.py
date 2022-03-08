import streamlit as st
import schoologydata as scdata
import webbrowser
import time

logged_in = False

def loginpage():
    global logged_in
    print("loginpage() was called")
    placeholder = st.empty()
    with placeholder.container():
        st.title('Login to Schoology')
        st.write('[Go to Schoology](%s)' % scdata.authurl)
        st.write('Schoology will ask you to authorize this application.')
        st.write('Authorizing this application only applies to this session. None of your information is saved.')
        with st.spinner('Waiting for authorization...'):
            while True:
                time.sleep(3)
                if scdata.auth.authorize():
                    break
    placeholder.write('Authorized!')
    logged_in = True

def overviewpage():
    print("overviewpage() was called")

    if st.button("Clear Cache"):
        st.session_state.clear()
        #for x in st.session_state:
            
        #del st.session_state['logged_in']
    
    logincol,loginheader = st.columns(2)

    with logincol:
        st.subheader('[Login with Schoology](%s)' % scdata.authurl)
    with loginheader:
        st.write('Logging in with Schoology ensures that your credentials are secure.')
    if 'logged_in' not in st.session_state:
        with st.spinner('Waiting for authorization...'):
            while True:
                time.sleep(3)
                if scdata.auth.authorize():
                    st.session_state['logged_in'] = True
                    break
        with st.spinner('Logging in...'):
            scdata.threelegged()
            st.session_state['courselist'] = scdata.courselist
            st.session_state['_courses'] = scdata._courses
            st.session_state['_periods'] = scdata._periods
            st.session_state['_categories'] = scdata._categories
            st.session_state['_assignments'] = scdata._assignments
    st.success('Logged in')

    placeholder = st.empty()
    with placeholder.container():
        st.title('Course View')
        st.selectbox(
            'Select a course', st.session_state['courselist'],
            index = 0, key = 'selected_course'
        )
        scdata.loadcourse(st.session_state['selected_course'])
        for x in scdata._periods.values():
            st.button(label = x.title)
            
        
        
    print("overviewpage() endedr")

def coursepage(coursetitle):
    print("coursepage() was called")
    global current
    print("current was made global")
    current.empty()
    print("current was emptied")
    page = current.container()
    print("page was declared")
    page.title(coursetitle)
    print("page title was constructed")
    return





current = st.empty()
print("before loginpage()")
if not logged_in:
    #loginpage()
    overviewpage()
print("last line")