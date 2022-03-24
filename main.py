import streamlit as st
import extra_streamlit_components as stx
import altair as alt
import pandas as pd
import secrets
import schoologydata as scdata
import requests.exceptions
import time

def overviewpage():
    print("overviewpage() was called")

    if st.button("Clear Cache"):
        st.session_state.clear()
        st.experimental_rerun()
    
    if 'logged_in' not in st.session_state:
        st.session_state['auth'] = scdata.get_auth()
        print(st.session_state['auth'].request_authorization())
        logincol,loginheader = st.columns(2)
        with logincol:
            st.subheader(
                '[Login with Schoology](%s)' % st.session_state['auth'].request_authorization()
            )
        with loginheader:
            st.write('Logging in with Schoology ensures that your credentials are secure.')
        
        with st.spinner('Waiting for authorization...'):
            authorize()

        if scdata.get_userstate(st.session_state):
            oldstate = scdata.get_userstate(st.session_state)
            st.write('Old session state recovered')
            st.write([key for key in oldstate.keys()])
            st.sesson_state = oldstate
        else:
            scdata.save_userstate(st.session_state)
    if st.button('clear user states'):
        scdata.clearstates()
    st.write(scdata.user_states)
    st.write([key for key in st.session_state.keys()])
    st.write([
        key for key in scdata.user_states['70925587'].keys()
    ])

    if 'logged_in' not in st.session_state:
        with st.spinner('Loading courses...'):
            #st.info(
            #    'Loading all of your courses can be pretty time-consuming.\n Luckily, if you have cookies enabled, you won\'t have to wait every time.'
            #)
            scdata.threelegged(st.session_state)
            #scdata.twolegged(st.session_state)
            if not st.session_state['auth']:
                st.error('Not Authorized. Refreshing in 5 seconds.')
                time.sleep(5)
                st.session_state.clear()
        st.experimental_rerun()
        
    scdata.save_userstate(st.session_state)
        
    st.write('You are logged in as %s' % st.session_state['me']['name_display'])

    st.title('Course View')
    st.selectbox(
        'Select a course. (Some courses are duplicate. This is fine, as they will both be loaded.)',
        ['Select a Course'] + st.session_state['courselist'],
        key = 'selected_course',
        index = 0
    )
    if st.session_state['selected_course'] != 'Select a Course':
        with st.spinner(f'Loading Grades for: {st.session_state["selected_course"]}'):
            placeholder = st.empty()
            if st.session_state['selected_course'] not in st.session_state['loaded_courses']:
                placeholder.info('This might take a while, since this is the first time loading this course. Afterwards, loading this course should be instant.')
            matches = scdata.loadcourse(st.session_state)
            scdata.save_userstate(st.session_state)
            for m in matches:
                st.header(m.title)
                for id in m.periods:
                    if id in st.session_state['_periods']:
                        period = st.session_state['_periods'][id]
                        showper = st.checkbox(
                            period.title,
                            key = f'showper {m.id} {period.id}'
                        )
                        if showper:
                            display_categories(m,period)
    print("overviewpage() ended")

def authorize():
    while True:
        time.sleep(3)
        if st.session_state['auth'].authorize():
            return
    
#f
def display_categories(m,p):
    for cat in st.session_state['_categories'].values():
        if cat.course_id == m.id:
            st.subheader(cat.title)
            with st.expander('Edit Assignments'):
                asg_editors(cat,p,m)
            display_chart(m,p,cat)

def asg_editors(cat,per,sec):
    dfid = f'{sec.id} {per.id} {cat.id}'
    asglist = [asg for asg in
              st.session_state['_assignments'].values() if
              asg.category == cat.id and
              asg.period == per.id and
              asg.section_id == sec.id]
    select_asg = st.selectbox(
        'Select an assignment',
        [asg.title for asg in asglist],
        key = f'selected_assignment {dfid}',
        on_change = del_chart,args=([dfid])
    )
    for asg in asglist:
        if asg.title == select_asg:
            break
    excused = st.checkbox(
        'Excused',
        value = True if asg.grade is None else False,
        key = f'excused {asg.id}',
        on_change = del_chart,args=([dfid])
    )
    notassigned = st.checkbox(
        'Not Assigned',
        value = True if asg.max is None else False,
        key = f'notassigned {asg.id}'
    )
    if notassigned:
        asg.max = None
    if excused:
        asg.grade = None
    if not excused and asg.grade is None:
        asg.grade = 0
    if not notassigned and asg.max is None:
        asg.max = 1
    if not notassigned and not excused:
        asg.grade = st.number_input(
            'Earned Points',
            min_value = 0,
            value = int(asg.grade),
            key = f'earned {asg.id}',
            on_change = del_chart,args=([dfid])
        )
        asg.max = st.number_input(
            'Maximum Points',
            min_value = 0,
            value = int(asg.max),
            key = f'max {asg.id}',
            on_change = del_chart,args=([dfid])
        )
        asg.percent = round(asg.grade/asg.max,3)
    
    
                
                    

def display_chart(m,p,c):
    #asgndict = {}
    #for asgn in st.session_state['_assignments'].values():
    #    if(
    #        asgn.section_id == m.id and 
    #        asgn.period == p.id and 
    #        asgn.category == c.id
    #    ):
    #        asgndict[asgn.title] = asgn.grade 
    #        st.button(
    #            f'{asgn.title}   {asgn.grade}/{asgn.max}',
    #            key = f'{m.id} {p.id} {c.id} {asgn.id}'
    #        )
    dataframe_id = (f'{m.id} {p.id} {c.id}')
    method = st.radio(
        'Calculation Type',
        ('Point Average','Percent Average'),
        help='Compare the different methods with your grade on Schoology to determine which method that category uses.',
        key= f'method {dataframe_id}',
        on_change = del_chart,args=([dataframe_id])
    )
    refresh = st.button(
        'Refresh Chart',
        key = f'refresh {dataframe_id}',
        on_click = del_chart,args=([dataframe_id])
    )

    if dataframe_id in st.session_state.charts:
        st.altair_chart(
            st.session_state.charts[dataframe_id],
            use_container_width=True
        )
        return
    if method == 'Point Average':
        chart = pointaverage_chart(c,p,m)
        if chart:
            st.altair_chart(
                chart,
                use_container_width=True
            )
    if method == 'Percent Average':
        chart = percentaverage_chart(c,p,m)
        if chart:
            st.altair_chart(
                chart,
                use_container_width=True
            )
        else:
            print('chart fail')

def percentaverage_chart(cat,per,sec):
    dataframe_id = (f'{sec.id} {per.id} {cat.id}')
    source = asgs_DataFrame(cat,per,sec)
    if source is None:
        return False
    st.session_state.dataframes[dataframe_id] = source
    domainmax = len(source)

    earnbar = alt.Chart(source).mark_bar().encode(
        x = alt.X('sum(percent)',
                 scale=alt.Scale(
                     domain=(0,domainmax),nice = False),
                axis=alt.Axis(labels=False)),
        color = alt.Color('title',legend=alt.Legend(
            orient='bottom',direction='vertical',
            columns = 1
        ))
    )
    maxbar = alt.Chart(source).mark_bar().encode(
        x = alt.X('count(percent)',
                 scale=alt.Scale(
                     domain=(0,domainmax),nice = False),
                 axis=alt.Axis(labels=False)),
        color = alt.Color('title',legend=alt.Legend(
            orient='bottom',direction='vertical',
            columns = 1
        ))
    )
    rule = alt.Chart(source).mark_rule(color='white').encode(
        x='sum(percent)'
    )
    text = alt.Chart(source).transform_joinaggregate(
        TotalMax = 'count(percent)',
        TotalGrade = 'sum(percent)',
    ).transform_calculate(
        TotalPercent = 'datum.TotalGrade / datum.TotalMax * 100'
    ).mark_text(
        align='left',dx=5,dy=-8,color='white').encode(
        x = 'sum(percent)',
        text = alt.Text(
            'TotalPercent:O',format=',.0f'
        ),
    )
    earnlayer = (earnbar+rule+text)
    bars = alt.vconcat(earnlayer,maxbar)
    st.session_state.charts[dataframe_id] = bars
    return bars

def pointaverage_chart(cat,per,sec):
    dataframe_id = (f'{sec.id} {per.id} {cat.id}')
    source = asgs_DataFrame(cat,per,sec)
    if source is None:
        return False
    st.session_state.dataframes[dataframe_id] = source
    domainmax = source['max'].sum()
    
    earnbar = alt.Chart(source).mark_bar().encode(
        x = alt.X('sum(grade)',
                 scale=alt.Scale(
                     domain=(0,domainmax),nice = False),
                axis=alt.Axis(labels=False)),
        color = alt.Color('title',legend=alt.Legend(
            orient='bottom',direction='vertical',
            columns = 1
        ))
    )
    maxbar = alt.Chart(source).mark_bar().encode(
        x = alt.X('sum(max)',
                 scale=alt.Scale(
                     domain=(0,domainmax),nice = False),
                 axis=alt.Axis(labels=False)),
        color = alt.Color('title',legend=alt.Legend(
            orient='bottom',direction='vertical',
            columns = 1
        ))
    )
    rule = alt.Chart(source).mark_rule(color='white').encode(
        x='sum(grade)'
    )
    text = alt.Chart(source).transform_joinaggregate(
        TotalMax = 'sum(max)',
        TotalGrade = 'sum(grade)',
    ).transform_calculate(
        TotalPercent = 'datum.TotalGrade / datum.TotalMax * 100'
    ).mark_text(
        align='left',dx=5,dy=-8,color='white').encode(
        x = 'sum(grade)',
        text = alt.Text(
            'TotalPercent:O',format=',.0f'
        ),
    )
    earnlayer = (earnbar+rule+text)
    bars = alt.vconcat(earnlayer,maxbar)
    st.session_state.charts[dataframe_id] = bars
    return bars
    

def asgs_DataFrame(cat,per,sec):
    daf = pd.DataFrame([
        asg.__dict__ for asg in
        st.session_state._assignments.values() if
        asg.category == cat.id and
        asg.period == per.id and
        asg.section_id == sec.id and
        asg.max is not None and
        asg.grade is not None
    ])
    if len(daf) == 0:
        return None
    return daf

def cbox_change():
    st.session_state['cbox_haschanged'] = True

def del_chart(dataframe_id):
    if dataframe_id in st.session_state.charts:
        del st.session_state.charts[dataframe_id]
        st.experimental_rerun()
    else:
        print('No chart was deleted.')

@st.cache(allow_output_mutation=True)
def get_manager():
    return stx.CookieManager()

st.set_page_config(
    page_title = 'Schoology', layout='wide'
)

if 'charts' not in st.session_state:
    st.session_state['charts'] = {}

if 'dataframes' not in st.session_state:
    st.session_state['dataframes'] = {}


if 'cbox_haschanged' not in st.session_state:
    st.session_state['cbox_haschanged'] = False

cookiemanager = get_manager()

try:
    overviewpage()
except requests.exceptions.HTTPError as err:
    print(err)
print("last line")
#gaega