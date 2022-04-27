import schoologydata as scdata

def overviewpage(st,params):
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
                for id in m.periods:
                    if id in st.session_state['_demoperiods']:
                        period = st.session_state['_demoperiods'][id])
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

def display_categories(st,params,m,p):
    for cat in st.session_state['_democategories'].values():
        if cat.course_id == m.id:
            st.subheader(cat.title)
            with st.expander('Edit Assignments'):
                has_asgs = asg_editors(st,cat,p,m)
            if has_asgs:
                display_catchart(st,m,p,cat)

def display_catchart(st,m,p,c):
    dataframe_id = (f'{m.id} {p.id} {c.id}')
    period_dfid = f'{m.id} {p.id}'
    rerun = False if period_dfid in st.session_state.demopercharts else True
    method = st.radio(
        'Calculation Type',
        ('Point Average','Percent Average'),
        help='Compare the different methods with your grade on Schoology to determine which method that category uses.',
        key= f'demomethod {dataframe_id}',
        on_change = del_chart,args=([st,dataframe_id])
    )
    advanced = st.checkbox(
        'Advanced',
        key = f'demoadvanced {dataframe_id}'
    )

    if True:
        if method == 'Point Average' and advanced:
            df = st.session_state.demodataframes[dataframe_id]
            display_df = df[['title','grade','max','url']].copy()
            total_earned = str(df['grade'].sum())
            total_max = str(df['max'].sum())
            gradefloat = round(df['grade'].sum()/df['max'].sum(), 4)
            gradedecimal = str(gradefloat)
            gradepercent = str(gradefloat*100)
            st.dataframe(display_df)
            st.latex(
                r'\frac{'+total_earned+r'}{'+total_max+r'}='+gradedecimal+r'\times100='+gradepercent+r'%'
            )
    if dataframe_id in st.session_state.democharts:
        st.altair_chart(
            st.session_state.democharts[dataframe_id],
            use_container_width=True
        )
        return
    if method == 'Point Average':
        c.method = 2
        chart = pointaverage_chart(c,p,m)
        if chart:
            st.altair_chart(
                chart,
                use_container_width=True
            )
            st.experimental_rerun()
                
    if method == 'Percent Average':
        c.method = 1
        chart = percentaverage_chart(c,p,m)
        if chart:
            st.altair_chart(
                chart,
                use_container_width=True
            )
            st.experimental_rerun()
        else:
            print('chart fail')
    if rerun:
        st.experimental_rerun()

def asg_editors(st,cat,per,sec):
    dfid = f'{sec.id} {per.id} {cat.id}'
    asglist = [asg for asg in
              st.session_state['_demoassignments'].values() if
              asg.category == cat.id and
              asg.period == per.id and
              asg.section_id == sec.id]
    if len(asglist) == 0:
        st.error(
            'No assignments were found in this category!\nIf you think this is incorrect, please [tell me about it](https://github.com/macglencoe/Schoology-Pro#bugs-and-feature-requests)'
        )
        if st.checkbox(
            'Manually set score',
            key = f'demomanualscore {dfid}'
        ):
            gradeselect = st.number_input(
                'Grade out of 100',
                key = f'demogradeselect {dfid}',
                value = 0,
            )
            df = pd.DataFrame([
            {
                    'title' : "Should Not Be Seen",
                    'max' : 100,
                    'grade' : gradeselect
                }
            ])
            st.session_state.demodataframes[dfid] = df
        else:
            if dfid in st.session_state.demodataframes:
                del st.session_state.demodataframes[dfid]
        return False
    select_asg = st.selectbox(
        'Select an assignment',
        [asg.title for asg in asglist],
        key = f'selected_demoassignment {dfid}',
        on_change = del_chart,args=([st,dfid])
    )
    for asg in asglist:
        if asg.title == select_asg:
            break
    excused = st.checkbox(
        'Excused',
        value = True if asg.grade is None else False,
        key = f'demoexcused {asg.id}',
        on_change = del_chart,args=([st,dfid])
    )
    notassigned = st.checkbox(
        'Not Assigned',
        value = True if asg.max is None else False,
        key = f'demonotassigned {asg.id}'
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
            key = f'demoearned {asg.id}',
            on_change = del_chart,args=([st,dfid])
        )
        asg.max = st.number_input(
            'Maximum Points',
            min_value = 0,
            value = int(asg.max),
            key = f'demomax {asg.id}',
            on_change = del_chart,args=([st,dfid])
        )
        asg.percent = round(asg.grade/asg.max,3)
    return True


def del_chart(st,dataframe_id):
    sec_id,per_id,cat_id = dataframe_id.split()
    if dataframe_id in st.session_state.charts:
        del st.session_state.charts[dataframe_id]
    else:
        st.error('No category chart found')
