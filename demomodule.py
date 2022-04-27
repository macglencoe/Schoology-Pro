import schoologydata as scdata

def demo_overviewpage(st,params):
    go_home = st.button('Return to Home')
    
    if "demo_generated" not in st.session_state:
        scdata.demosetup(st.session_state)

    st.image('Visual_Grader.png',width=125)

    if 'title' in params:
        ind = st.session_state.democourselist.index(
            params['title'][0]
        ) + 1
    else:
        ind = 0
    
    st.title('Course View')
    st.selectbox(
        'Select a course. (Some courses are duplicate. This is fine, as they will both be loaded.)',
        ['Select a Course'] + st.session_state['democourselist'],
        key = 'selected_democourse',
        index = ind
    )
    if st.session_state['selected_democourse'] != 'Select a Course':
        st.experimental_set_query_params(
            page='DemoCourse',
            title=st.session_state.selected_democourse
        )
        with st.spinner(f'Loading Grades for: {st.session_state["selected_democourse"]}'):
            placeholder = st.empty()
            if st.session_state['selected_democourse'] not in st.session_state['loaded_democourses']:
                placeholder.info('This might take a while, since this is the first time loading this course. Afterwards, loading this course should be instant.')
            matches = scdata.demoload(st.session_state)
            for m in matches:
                period_grades = []
                st.title(f'{m.title}')
                st.write(m.periods)
                st.write(st.session_state['_demoperiods'])
                for id in m.periods:
                    if id in st.session_state['_demoperiods']:
                        period = st.session_state['_demoperiods'][id]
                        dfid = f'{m.id} {period.id}'
                        if st.button(
                            period.title,
                            key = f'showdemoper {m.id} {period.id}'
                        ):
                            st.experimental_set_query_params(
                                page='DemoPeriod',
                                id=f'{m.id} {period.id}'
                            )
                        if dfid in st.session_state.demoperiod_grades:
                            grade = st.session_state.demoperiod_grades[dfid]
                            st.caption(
                                str(round(grade,4))+'%'
                            )
                        else:
                            grade = None
                            st.caption('Grade not calculated yet.\nClick the button to calculate.')
                        if dfid in st.session_state.demoperiod_mod:
                            st.caption('❗ This Grading Period is modified.')
                        period_grades.append(grade)
                if None not in period_grades:
                    avg = sum(period_grades) / len(period_grades)
                    st.write('Semester: '+str(round(avg,2))+'%')
                    if avg < 60:
                        letter='F'
                    elif avg < 70:
                        letter='D'
                    elif avg < 80:
                        letter='C'
                    elif avg < 90:
                        letter='B'
                    else:
                        letter='A'
                    st.header(letter)
                else:
                    st.write('All periods in semester must be calculated to show the semester grade.')
    if go_home:
        st.experimental_set_query_params(
            page='Home'
        )
