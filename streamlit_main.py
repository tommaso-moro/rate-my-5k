import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pymongo
import os
from dotenv import load_dotenv
from streamlit.state.session_state import SessionState
load_dotenv('.env')
from streamlit_logic import Model
from streamlit_echarts import st_echarts #https://share.streamlit.io/andfanilo/streamlit-echarts-demo/master/app.py


## CONNECT TO MONGO ##
def get_mongo_collection():
    mongo_server_url = st.secrets["MONGO_URI"]
    client = pymongo.MongoClient(mongo_server_url) 
    db_name = st.secrets["DB_NAME"]
    col_name = st.secrets["COLLECTION_NAME"]
    mongo_col = client.get_database(db_name)[col_name]
    """
    if using os.getenv locally:
        mongo_server_url = os.getenv('MONGO_URI')
        client = pymongo.MongoClient(mongo_server_url) 
        db_name = os.getenv('DB_NAME')
        col_name = os.getenv('COLLECTION_NAME')
        mongo_col = client.get_database("db_name")["col_name"]
    """
    return mongo_col

# get time in seconds (e.g. 20:15 is 1215 seconds)
def get_time_in_seconds(minutes, seconds):
    return (minutes*60 + seconds)


## SESSION STATE ##
if 'model' not in st.session_state:
    st.session_state['model'] = Model(get_mongo_collection())
if 'tot_num_running_performances' not in st.session_state:
    st.session_state['tot_num_running_performances'] = st.session_state.model.get_tot_num_running_performances()
if 'tot_num_running_events' not in st.session_state:
    st.session_state['tot_num_running_events'] = st.session_state.model.get_tot_num_events()
if 'user_age' not in st.session_state:
    st.session_state['user_age'] = 0
if 'user_gender' not in st.session_state:
    st.session_state['user_gender'] = 0
if 'user_minutes' not in st.session_state:
    st.session_state['user_minutes'] = 0
if 'user_seconds' not in st.session_state:
    st.session_state['user_seconds'] = 0
if 'tot_num_faster_runs' not in st.session_state:
    st.session_state['tot_num_faster_runs'] = 0
if 'tot_num_slower_runs' not in st.session_state:
    st.session_state['tot_num_slower_runs'] = 0
if 'num_faster_runs_by_age' not in st.session_state:
    st.session_state['num_faster_runs_by_age'] = 0
if 'num_slower_runs_by_age' not in st.session_state:
    st.session_state['num_slower_runs_by_age'] = 0
if 'num_faster_runs_by_gender' not in st.session_state:
    st.session_state['num_faster_runs_by_gender'] = 0
if 'num_slower_runs_by_gender' not in st.session_state:
    st.session_state['num_slower_runs_by_gender'] = 0
if 'num_faster_runs_by_age_and_gender' not in st.session_state:
    st.session_state['num_faster_runs_by_age_and_gender'] = 0
if 'num_slower_runs_by_age_and_gender' not in st.session_state:
    st.session_state['num_slower_runs_by_age_and_gender'] = 0
if 'show_results' not in st.session_state:
    st.session_state['show_results'] = False
if 'bar_chart_type' not in st.session_state:
    st.session_state['bar_chart_type'] = 'Percentages of faster/slower runs'



## LAYOUT ##
header = st.container()
input_form = st.container()
result_stats = st.container()


def handle_begin_btn_click(age, gender, minutes, seconds):
    with st.spinner('Calculating results...'):
        user_time_in_seconds = get_time_in_seconds(minutes, seconds)
        st.session_state.user_age = age
        st.session_state.user_gender = gender
        st.session_state.user_minutes = minutes
        st.session_state.user_seconds = seconds
        result_stats = st.session_state.model.get_stats(user_time_in_seconds, age, gender)
        st.session_state.tot_num_faster_runs = result_stats['tot_num_faster_runs']
        st.session_state.tot_num_slower_runs = result_stats['tot_num_slower_runs']
        st.session_state.num_faster_runs_by_age = result_stats['num_faster_runs_by_age']
        st.session_state.num_slower_runs_by_age = result_stats['num_slower_runs_by_age']
        st.session_state.num_faster_runs_by_gender = result_stats['num_faster_runs_by_gender']
        st.session_state.num_slower_runs_by_gender = result_stats['num_slower_runs_by_gender']
        st.session_state.num_faster_runs_by_age_and_gender = result_stats['num_faster_runs_by_age_and_gender']
        st.session_state.num_slower_runs_by_age_and_gender = result_stats['num_slower_runs_by_age_and_gender']
    #st.balloons()
    st.session_state.show_results = True

def handle_start_over_btn():
    st.session_state.show_results = False

#config dict for the pie chart
def get_pie_chart_config(num_faster_runs, num_slower_runs):
    options = {
            "title": {"text": "", "subtext": "", "left": "center"},
            "tooltip": {"trigger": "item"},
            "legend": {"orient": "vertical", "left": "left"},
            "series": [
                {
                    "name": "",
                    "type": "pie",
                    "radius": "50%",
                    "data": [
                        {"value": num_faster_runs, "name": "Share of faster 5ks"},
                        {"value": num_slower_runs, "name": "Share of slower 5ks"},
                    ],
                    "emphasis": {
                        "itemStyle": {
                            "shadowBlur": 10,
                            "shadowOffsetX": 0,
                            "shadowColor": "rgba(0, 0, 0, 0.5)",
                        }
                    },
                }
            ],
        }
    return options

#config dict for the bar chart
def get_bar_chart_config(num_overall_faster_runs, num_overall_slower_runs, num_faster_runs_by_age, num_slower_runs_by_age, num_faster_runs_by_gender, num_slower_runs_by_gender, num_faster_runs_by_age_and_gender, num_slower_runs_by_age_and_gender):
    config = {
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "legend": {
                "data": ["Faster runs", "Slower runs"]
            },
            "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
            "xAxis": {"type": "value"},
            "yAxis": {
                "type": "category",
                "data": ["Overall", "Same gender", "Same age group", "Same gender and age group"],
            },
            "series": [
                {
                    "name": "Faster runs",
                    "color": "#e74c3c",
                    "type": "bar",
                    "stack": "total",
                    "label": {"show": False},
                    "emphasis": {
                        "focus": "series",
                        "itemStyle": {
                            "shadowBlur": 10,
                            "shadowOffsetX": 0,
                            "shadowColor": "rgba(0, 0, 0, 0.5)",
                        }
                    },
                    "data": [num_overall_faster_runs, num_faster_runs_by_gender, num_faster_runs_by_age, num_faster_runs_by_age_and_gender],
                },
                {
                    "name": "Slower runs",
                    "type": "bar",
                    "color": "#f1c40f",
                    "stack": "total",
                    "label": {"show": False},
                    "emphasis": {
                        "focus": "series",
                        "itemStyle": {
                                "shadowBlur": 10,
                                "shadowOffsetX": 0,
                                "shadowColor": "rgba(0, 0, 0, 0.5)",
                        }
                    },
                    "data": [num_overall_slower_runs, num_slower_runs_by_gender, num_slower_runs_by_age, num_slower_runs_by_age_and_gender],
                },
            ],
        }
    return config

   



#HEADER
with header:
    st.title('Rate my 5k :man-running:')
    st.header('Welcome, runner!')
    st.subheader('This is a data-driven app which allows you to compare your running performance over 5 kilometers to the performance of other runners.')
    st.write('To give you a reliable comparison we use data from ', st.session_state.tot_num_running_performances, ' 5k running performances from runners who participated in ', st.session_state.tot_num_running_events,
        'timed 5k running events in the UK. The data includes information about runners\' **times**, **gender** and **age groups**, so we can give you gender- and age-specific insights. **Enjoy** :rocket:')
    st.caption("Made with love by Tommaso Moro (tommsmoro@gmail.com)")
    st.write('\n')
    st.write('\n')

#INPUT FORM
with input_form:
    if (st.session_state.show_results == False):
        age = st.slider("Select your age", min_value=10, max_value=90, value=25, step=1)
        gender = st.radio("What is your gender?", ('Male', 'Female'))
        st.write('You can run a 5k in: ')
        col1, col2 = st.columns(2)
        minutes = col1.number_input('minutes:', value=25, step=1, min_value=12)
        seconds = col2.number_input('seconds', value=30, step=1, max_value=59)
        if (st.session_state.user_gender != 'Prefer not to say'):
            st.write('You are a ', age, ' years old ', gender.lower())
        else:
            st.write('You are ', age, ' years old ')
        st.write('Your 5k time is ', int(minutes), ' minutes and ', int(seconds), ' seconds.')

        st.write('\n')
        st.write('\n')
        st.write('\n')
        col1, col2, col3, col4, col5 = st.columns([0.7,0.7,1,0.7,0.7])
        col3.button("Give me those stats!", on_click=handle_begin_btn_click, args=[age, gender, minutes, seconds])

    else:
        col1, col2, col3, col4, col5 = st.columns([1.2,1.2,1,1.2,1.2])
        col3.button("Start over!", on_click=handle_start_over_btn)


#RESULTS STATS
with result_stats:
    if (st.session_state.tot_num_faster_runs != 0 and st.session_state.tot_num_slower_runs != 0 and st.session_state.show_results == True):
        overall_percentile = st.session_state.model.get_percentile(st.session_state.tot_num_faster_runs, st.session_state.tot_num_slower_runs)
        percentile_by_age = st.session_state.model.get_percentile(st.session_state.num_faster_runs_by_age, st.session_state.num_slower_runs_by_age)
        percentile_by_gender = st.session_state.model.get_percentile(st.session_state.num_faster_runs_by_gender, st.session_state.num_slower_runs_by_gender)
        percentile_by_age_and_gender = st.session_state.model.get_percentile(st.session_state.num_faster_runs_by_age_and_gender, st.session_state.num_slower_runs_by_age_and_gender)

        st.title('Your results')
        st.header('A high-level glance')
        st.write(st.session_state.tot_num_running_performances, ' 5k running performances from ', st.session_state.tot_num_running_events, ' running events have been analyzed.')
        st.write("- **Overall**, ", overall_percentile, "% of 5k runs are slower than yours and ", round((100-percentile_by_age),2), "% of them are faster.")
        st.write("- **In your age group**, ", percentile_by_age, "% of 5k runs are slower than yours and ", round((100-percentile_by_age),2), "% of them are faster.")
        st.write("- ", percentile_by_gender, "% of 5k runs by people of your **same gender** are slower than yours and ",round((100-percentile_by_gender),2), "% of them are faster.")
        st.write("- **In your same age group and gender**, ", percentile_by_age_and_gender, " % of runs are slower than yours and ", round((100-percentile_by_age_and_gender),2), "% of them are faster.")

        st.write("\n")
        st.caption("PS. Hover over the barchart!")
        st.write("\n")
        bar_chart_config = st.radio("Bar chart shows", ('Percentages of faster/slower runs', 'Number of faster/slower runs'))
        if bar_chart_config == 'Percentages of faster/slower runs':
            st.write("\n")
            st_echarts(options=get_bar_chart_config(
            round((100-overall_percentile),2),
            overall_percentile,
            round((100-percentile_by_age),2),
            percentile_by_age,
            round((100-percentile_by_gender),2),
            percentile_by_gender,
            round((100-percentile_by_age_and_gender),2),
            percentile_by_age_and_gender
            ), height="500px")
        else:
            st_echarts(options=get_bar_chart_config(
                st.session_state.tot_num_faster_runs,
                st.session_state.tot_num_slower_runs,
                st.session_state.num_faster_runs_by_age,
                st.session_state.num_slower_runs_by_age,
                st.session_state.num_faster_runs_by_gender,
                st.session_state.num_slower_runs_by_gender,
                st.session_state.num_faster_runs_by_age_and_gender,
                st.session_state.num_slower_runs_by_age_and_gender
            ), height="500px")

        st.write("\n")
        st.write("\n")
        st.write("\n")

        ## general results ##
        st.subheader('Comparison with all runners')
        st.write("In a hypothetical race with all runners, your performance would rank ", st.session_state.tot_num_faster_runs, " out of ", st.session_state.tot_num_slower_runs, ".")
        st_echarts(
            options=get_pie_chart_config(st.session_state.tot_num_faster_runs, st.session_state.tot_num_slower_runs), height="600px",
        )

        st.write('\n')
        
        ## age-specific results ##
        st.subheader('Now, let\'s break things down by **_age_**!')
        st.write("In a hypothetical race with runners in your same age group, your performance would rank ", st.session_state.num_faster_runs_by_age, " out of ", st.session_state.num_faster_runs_by_age+st.session_state.num_slower_runs_by_age, ".")
        st_echarts(
            options=get_pie_chart_config(st.session_state.num_faster_runs_by_age, st.session_state.num_slower_runs_by_age), height="600px",
        )
        st.write('\n')

        ## gender-specific results ##
        st.subheader('Now, let\'s break things down by **_gender_**!')
        st.write("In a hypothetical race with runners of your same gender, your performance would rank ", st.session_state.num_faster_runs_by_gender, " out of ", st.session_state.num_faster_runs_by_gender+st.session_state.num_slower_runs_by_gender, ".")
        st_echarts(
            options=get_pie_chart_config(st.session_state.num_faster_runs_by_gender, st.session_state.num_slower_runs_by_gender), height="600px",
        )
        st.write('\n')

        ## age- and gender-specific results ##
        st.subheader('Now, let\'s break things down by **_age_** and **_gender_**!')
        st.write("In a hypothetical race with runners of your same gender who are also in your same age group, your performance would rank ", st.session_state.num_faster_runs_by_age_and_gender, " out of ", st.session_state.num_faster_runs_by_age_and_gender+st.session_state.num_slower_runs_by_age_and_gender, ".")
        st_echarts(
            options=get_pie_chart_config(st.session_state.num_faster_runs_by_age_and_gender, st.session_state.num_slower_runs_by_age_and_gender), height="600px",
        )

        
                
#st.write(st.session_state) -> useful for debugging




