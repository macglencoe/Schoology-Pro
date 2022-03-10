import streamlit as st
import schoologydata as scdata
import webbrowser
import time

#g

def overviewpage():
    print("overviewpage() was called")

    if st.button("Clear Cache"):
        st.session_state.clear()
        st.experimental_rerun()
    
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
                    st.session_state['auth'] = scdata.auth
                    break
        with st.spinner('Logging in...'):
            scdata.threelegged()
            st.session_state['sc'] = scdata.sc
            st.session_state['me'] = scdata.me
            st.session_state['olist'] = scdata.olist
            st.session_state['courselist'] = scdata.courselist
            st.session_state['_courses'] = scdata._courses
            st.session_state['_periods'] = scdata._periods
            st.session_state['_categories'] = scdata._categories
            st.session_state['_assignments'] = scdata._assignments
    if 'logged_in' in st.session_state:
        with st.spinner('Loading...'):
            scdata.sc = st.session_state['sc']
            scdata.me = st.session_state['me']
            scdata.olist = st.session_state['olist']
            scdata.auth = st.session_state['auth']
        if not scdata.auth.authorize():
            st.error("Authorization token invalid. Refreshing in 5 seconds.")
            time.sleep(5)
            st.session_state.clear()
            st.experimental_rerun()
        
    st.success('Logged in')

    st.title('Course View')
    st.selectbox(
        'Select a course. (Some courses are duplicate. This is fine, as they will both be loaded.)',
        st.session_state['courselist'],
        key = 'selected_course', on_change = cbox_change
    )
    if st.session_state['cbox_haschanged']:
        with st.spinner(f'Loading Grades for: {st.session_state["selected_course"]}'):
            matches = scdata.loadcourse(
                st.session_state['selected_course']
            )
            for m in matches:
                st.header(m.title)
                for id in m.periods:
                    if id in scdata._periods:
                        period = scdata._periods[id]
                        #st.button(label = period.title)
                        st.subheader(period.title)
                        display_categories(m,period)
    print("overviewpage() ended")

def display_categories(m,p):
    for cat in scdata._categories.values():
        if cat.course_id == m.id:
            #st.button(cat.title, key = f'{p.id} {cat.id}')
            with st.expander(cat.title):
                display_assignments(m,p,cat)

def display_assignments(m,p,c):
    for asgn in scdata._assignments.values():
        if asgn.section_id == m.id and asgn.period == p.id and asgn.category == c.id:
            st.button(
                f'{asgn.title}   {asgn.grade}/{asgn.max}',
                key = f'{m.id} {p.id} {c.id} {asgn.id}'
            )

def cbox_change():
    st.session_state['cbox_haschanged'] = True

if 'cbox_haschanged' not in st.session_state:
    st.session_state['cbox_haschanged'] = False

overviewpage()
print("last line")