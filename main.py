import streamlit as st
import schoologydata as scdata
import webbrowser
import time

def overviewpage():
    print("overviewpage() was called")

    if st.button("Clear Cache"):
        st.session_state.clear()
        st.experimental_rerun()
    
    if 'logged_in' not in st.session_state:
        scdata.get_auth(st.session_state)
        logincol,loginheader = st.columns(2)
        with logincol:
            st.subheader(
                '[Login with Schoology](%s)' % st.session_state['auth_url']
            )
        with loginheader:
            st.write('Logging in with Schoology ensures that your credentials are secure.')
        
        with st.spinner('Waiting for authorization...'):
            while True:
                time.sleep(3)
                if st.session_state['auth'].authorize():
                    st.session_state['logged_in'] = True
                    break
        with st.spinner('Logging in...'):
            scdata.threelegged(st.session_state)
        st.experimental_rerun()
    elif 'logged_in' in st.session_state:
        if not scdata.test_auth(st.session_state):
            st.error("Authorization token invalid. Refreshing in 5 seconds.")
            time.sleep(5)
            st.session_state.clear()
            st.experimental_rerun()
        
    st.write('You are logged in as %s' % 
             st.session_state['me']['name_display'])

    st.title('Course View')
    st.selectbox(
        'Select a course. (Some courses are duplicate. This is fine, as they will both be loaded.)',
        st.session_state['courselist'],
        key = 'selected_course', on_change = cbox_change
    )
    if st.session_state['cbox_haschanged']:
        with st.spinner(f'Loading Grades for: {st.session_state["selected_course"]}'):
            placeholder = st.empty()
            if st.session_state['selected_course'] not in st.session_state['loaded_courses']:
                placeholder.info('This might take a while, since this is the first time loading this course. Afterwards, loading this course should be instant.')
            matches = scdata.loadcourse(st.session_state)
            placeholder.empty()
            for m in matches:
                st.header(m.title)
                for id in m.periods:
                    if id in st.session_state['_periods']:
                        period = st.session_state['_periods'][id]
                        #st.button(label = period.title)
                        st.subheader(period.title)
                        display_categories(m,period)
    print("overviewpage() ended")

def display_categories(m,p):
    for cat in st.session_state['_categories'].values():
        if cat.course_id == m.id:
            #st.button(cat.title, key = f'{p.id} {cat.id}')
            with st.expander(cat.title):
                display_assignments(m,p,cat)

def display_assignments(m,p,c):
    for asgn in st.session_state['_assignments'].values():
        if(
            asgn.section_id == m.id and 
            asgn.period == p.id and 
            asgn.category == c.id
        ):
            st.button(
                f'{asgn.title}   {asgn.grade}/{asgn.max}',
                key = f'{m.id} {p.id} {c.id} {asgn.id}'
            )

def cbox_change():
    st.session_state['cbox_haschanged'] = True

if 'cbox_haschanged' not in st.session_state:
    st.session_state['cbox_haschanged'] = False

st.set_page_config(
    page_title = 'Schoology', layout='wide'
)

overviewpage()
print("last line")