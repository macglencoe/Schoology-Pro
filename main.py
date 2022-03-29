import streamlit as st
import extra_streamlit_components as stx
import altair as alt
import pandas as pd
import numpy as np
import secrets
import schoologydata as scdata
import requests.exceptions
import time

def overviewpage():
    print("overviewpage() was called")

    logocol,cachecol,userdatacol = st.columns(3)

    logocol.image('logo.png')
    if cachecol.button("Clear Cache"):
        st.session_state.clear()
        st.experimental_rerun()
    if userdatacol.button(
        "Clear User Data",
        disabled = False if 'logged_in' in st.session_state
        else True
    ):
        cleared = scdata.del_userstate(
            st.session_state.me['uid']
        )
        if cleared:
            st.session_state.clear()
            st.experimental_rerun()
        else:
            st.error('Your data is either already cleared or not saved yet.')

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
            st.info('Recovered session data')
            for key,val in oldstate.items():
                st.session_state[key] = val
                

    if 'logged_in' not in st.session_state:
        with st.spinner('Loading courses...'):
            progbar = st.progress(0.0)
            st.info(
                'Loading up all of your courses is pretty time-consuming.\nLuckily, this data is saved for you, so next time you authorize, everything should already be there for you.'
            )
            scdata.threelegged(st.session_state,progbar)
            #scdata.twolegged(st.session_state)
            progbar.progress(1.0)
            if not st.session_state['auth']:
                st.error('Not Authorized. Refreshing in 5 seconds.')
                time.sleep(5)
                st.session_state.clear()
    #st.experimental_rerun()


        
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
                            display_perchart(m,period)
                            display_categories(m,period)
    print("overviewpage() ended")


def authorize():
    while True:
        time.sleep(3)
        if st.session_state['auth'].authorize():
            return
    
def display_categories(m,p):
    for cat in st.session_state['_categories'].values():
        if cat.course_id == m.id:
            st.subheader(cat.title)
            st.write(cat.weight)
            with st.expander('Edit Assignments'):
                has_asgs = asg_editors(cat,p,m)
            if has_asgs:
                display_catchart(m,p,cat)
def asg_editors(cat,per,sec):
    dfid = f'{sec.id} {per.id} {cat.id}'
    asglist = [asg for asg in
              st.session_state['_assignments'].values() if
              asg.category == cat.id and
              asg.period == per.id and
              asg.section_id == sec.id]
    if len(asglist) == 0:
        st.error(
            'No assignments were found in this category!\nIf you think this is incorrect, please [tell me about it](https://github.com/macglencoe/Schoology-Pro#bugs-and-feature-requests)'
        )
        return False
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
    return True


def display_catchart(m,p,c):
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




def display_perchart(sec,per):
    dfid = f'{sec.id} {per.id}'
    refresh = st.button(
        'Refresh Chart',
        key = f'refresh {dfid}',
        on_click = del_perchart,args=([dfid])
    )
    if dfid in st.session_state.percharts:
        st.altair_chart(
            st.session_state.percharts[dfid],
            use_container_width=True
        )
        return
    chart = period_chart(sec,per)
    if chart:
        st.altair_chart(
            chart,
            use_container_width=True
        )
    else:
        print('chart fail')


def period_chart(sec,per):
    dfid = f'{sec.id} {per.id}'
    source = cats_DataFrame(sec,per)
    if source is None:
        return False
    st.session_state.period_dfs[dfid] = source
    domainmax = 100.0

    earnbar = alt.Chart(source).mark_bar().encode(
        x = alt.X('sum(factor)',
                scale=alt.Scale(
                     domain=(0,domainmax),nice=False),
                axis=alt.Axis(labels=False)),
        color = alt.Color('title',legend=alt.Legend(
            orient='bottom',direction='vertical',
            columns = 1
        ))
    )
    maxbar = alt.Chart(source).mark_bar().encode(
        x = alt.X('sum(weight)',
                 scale=alt.Scale(
                     domain=(0,domainmax),nice = False),
                 axis=alt.Axis(labels=True)),
        color = alt.Color('title',legend=alt.Legend(
            orient='bottom',direction='vertical',
            columns = 1
        ))
    )
    rule = alt.Chart(source).mark_rule(color='white').encode(
        x='sum(factor)'
    )
    text = alt.Chart(source).transform_joinaggregate(
        TotalMax = 'sum(weight)',
        TotalGrade = 'sum(factor)',
    ).transform_calculate(
        TotalPercent = 'datum.TotalGrade / datum.TotalMax * 100'
    ).mark_text(
        align='left',dx=5,dy=-8,color='white').encode(
        x = 'sum(factor)',
        text = alt.Text(
            'sum(factor):O',format=',.0f'
        ),
    )
    earnlayer = (earnbar+rule+text)
    bars = alt.vconcat(earnlayer,maxbar)
    st.session_state.percharts[dfid] = bars
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


def cats_DataFrame(sec,per):
    catdf_tuples = []
    for cat in st.session_state._categories.values():
        if cat.course_id != sec.id:
            continue
        dfid = f'{sec.id} {per.id}'
        dfs = [
            df for id,df in st.session_state.dataframes.items()
            if dfid in id
        ]
        catdf_tuples.extend([(cat,df) for df in dfs])
    
    daf = pd.DataFrame([
        {
            'title' : cat.title,
            'weight' : cat.weight,
            'grade' : ((df['grade'].sum()/df['max'].sum())*100)/2 if
            cat.method == 2 else
            ((df['percent'].sum()/len(df))*100)/2
        }
        for cat,df in catdf_tuples
    ])
    if len(daf) == 0:
        return None
    daf['factor'] =(daf['grade']*(daf['weight']/100))/2
    return daf

def cbox_change():
    st.session_state['cbox_haschanged'] = True

def del_chart(dataframe_id):
    if dataframe_id in st.session_state.charts:
        del st.session_state.charts[dataframe_id]
        st.experimental_rerun()
    else:
        print('No chart was deleted.')
def del_perchart(dataframe_id):
    if dataframe_id in st.session_state.percharts:
        del st.session_state.percharts[dataframe_id]
        st.experimental_rerun()
    else:
        print('No chart was deleted.')

def update_session_state(key,val):
    st.session_state[key] = val


st.set_page_config(
    page_title = 'Schoology', layout='wide',
    page_icon = 'favicon.ico'
)

if 'percharts' not in st.session_state:
    st.session_state['percharts'] = {}

if 'period_dfs' not in st.session_state:
    st.session_state['period_dfs'] = {}

if 'charts' not in st.session_state:
    st.session_state['charts'] = {}

if 'dataframes' not in st.session_state:
    st.session_state['dataframes'] = {}


if 'cbox_haschanged' not in st.session_state:
    st.session_state['cbox_haschanged'] = False

overviewpage()

print("last line")
#gaega