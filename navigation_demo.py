from st_aggrid import grid_options_builder
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
import altair as alt
from streamlit_option_menu import option_menu
import plotly.express as px
import plotly.graph_objects as go
import time

def init_session_state():
    st.session_state.page_number = 1
    st.session_state.initial_data = pd.read_csv('initial_dataset.csv', dtype={'Year': str})[['Year','Month','Profit Actual']]
    forecast_data = pd.read_csv('forecasted_output_prophet.csv')[['Date','Profit']]
    forecast_data['Month'] = pd.to_datetime(forecast_data['Date']).dt.month_name()
    forecast_data['Year'] = pd.to_datetime(forecast_data['Date']).dt.year
    forecast_data['Year_Month'] =  forecast_data['Year'].astype(str) + ' ' + forecast_data['Month'].str.slice(0, 3) 
    st.session_state.forecast_data = forecast_data
    st.session_state.suggestion_data = pd.read_csv('suggestion_data.csv', dtype={'Year': str})
        
# Create an instance of the app state
if "page_number" not in st.session_state:
    init_session_state()
    
def typewriter(text: str, speed: int):
    tokens = text.split()
    container = st.empty()
    for index in range(len(tokens) + 1):
        curr_full_text = " ".join(tokens[:index])
        container.markdown(curr_full_text)
        time.sleep(1 / speed)
    
def home_page():
    # st.title("Home")
    text_size = """
    <style>
    [data-testid = "stMarkdownContainer"] {
        text-align: center;    
    }
    
    .st-emotion-cache-5rimss p {
    font-size: xxx-large;
    # font-weight: bold;
    color: beige; 
    }
    </style>
    """
    
    st.markdown(text_size,unsafe_allow_html=True)
    
    text = "Hello world !!"
    speed = 10
    typewriter(text=text, speed=speed)
    text = "Welcome to see the future."
    typewriter(text=text, speed=speed)
    col1,col2,col3 = st.columns(spec=[10,8,10],gap="large")
    with col3:
        if st.button("Connect Dataset For Predictions"):
            st.session_state.page_number = 2
            st.rerun()
    
def connection_details():
    # st.header("Data Information")
    
    header_html = """
    <div style="text-align: center;">
        <h1 style= "color: beige;">Connection Information</h1>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
    
    center = """
    <style>
    
    # [data-testid = "stMarkdownContainer"] {
    #     text-align: center;    
    # }
    .st-emotion-cache-16idsys p{
    font-size: large;
    font-weight: bold;
    color: #EBECEC; 
    }
    </style>
    """
    st.markdown(center,unsafe_allow_html=True)
    col1, col2,col3 = st.columns(spec=[5,7,5],gap="small")
    with col2:
    
        selected_option = st.selectbox("Select the Project", [" ","q-gcp-00863-fsihackathon-23-12"])
        selected_option = st.selectbox("Select the Dataset", [" ","ba_synthesizer_forecast_modifier"])
        selected_option = st.selectbox("Select the Table", [" ","forecasted_output_firstpass"])
        
        header_html = """
        <div style="text-align: center;">
            <h1 style= "color: beige;">Expected Outcome Information</h1>
        </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)
        selected_option = st.selectbox("Select the 'Prediction' column from the dataset to analyze", ["","Profit","Sales","Rention","R&D Expenses","Administration expense"])
        selected_option = st.selectbox("Select the 'Year' to Predict", ["","2024","2025","2026","2027","2028"])

        st.write("")
        col1,col2,col3 = st.columns(spec=[5,7,3.5],gap="small")
        with col3:
            if st.button("Show Predictions"):
                st.session_state.page_number = 3
                st.rerun()
                
def dataframe_with_selections(df):
    
    df_with_selections = df.copy()
    df_with_selections.insert(0, "Select", False)

    # Get dataframe row-selections from user with st.data_editor
    edited_df = st.data_editor(
        df_with_selections,
        hide_index=True,
        column_config={"Select": st.column_config.CheckboxColumn(required=True)},
        disabled=df.columns,
    )

    # Filter the dataframe using the temporary column, then drop the column
    selected_rows = edited_df[edited_df.Select]
    return selected_rows.drop('Select', axis=1)
            
# Function to change the profit in suggestion Screen 
def change_profit(df):
    state = st.session_state["edited_df"]
    for index, updates in state["edited_rows"].items():
        for key, value in updates.items():
            st.session_state["selected_data"].loc[st.session_state["selected_data"].index == index, key] = value
        sum_values = st.session_state.selected_data.loc[index, ['OverheadCharges', 'HeadCount', 'MarketingExpense', 'AdminstrationExpenses']].sum()
        st.session_state.selected_data.loc[st.session_state["selected_data"].index == index, "Profit Forecast/Prediction"] = sum_values
        #Premiums collected	Overhead charges( operation Expense ) (unavoidable expense)   0.7- 1.3	Head count (Salaries) 0.4 - 0.9	Marketing Expense 0.3-0.8	R&D Expense 0.5 - 1	Adminstration Expenses  0.5 -0.9    

def forecast_prediction():
    forecast_data = st.session_state.forecast_data
    initial_data = st.session_state.initial_data
    initial_data = initial_data.rename(columns = {'Profit Actual':'Profit'})
    initial_data['IsInitial'] = True
    forecast_data['IsInitial'] = False
    overall_data  = pd.concat([initial_data[['Month', 'Year', 'Profit', 'IsInitial']], forecast_data[['Month', 'Year', 'Profit', 'IsInitial']]])
    
    overall_data['Year_Month'] =  overall_data['Year'].astype(str) + ' ' + overall_data['Month'].str.slice(0, 3) 
    col1, col2 = st.columns([2,2])
    with col1:
        st.table(forecast_data[['Year_Month', 'Profit']].rename(columns = {'Profit': 'Forecasted Profits'}))
        
    with col2:
        x1 = overall_data['Year_Month']
        y1 = overall_data.apply(lambda x:0 if x['IsInitial'] == True else x['Profit'], axis=1)#overall_data[overall_data['IsInitial'] == True]['Profit']
        y2 = overall_data.apply(lambda x:0 if x['IsInitial'] == False else x['Profit'], axis=1) #overall_data[overall_data['IsInitial'] == False]['Profit']
        fig = px.bar(overall_data, x=x1, y=[y1,y2], labels={'column1':'Actual profit', 'column2': 'Forecasted profit'})
        fig.update_layout(
            title = 'Predictions',
            paper_bgcolor='#FFFFFF',
            plot_bgcolor='#FFFFFF')
            
        #fig.show()
        st.plotly_chart(fig)

def app_screens():
    
    if st.session_state.get('switch_button', False):
        st.session_state['menu_option'] = (st.session_state.get('menu_option', 0) + 1) % 5
        manual_select = st.session_state['menu_option']
    else:
        manual_select = None
        
        
    selected4 = option_menu(None, ["Forecast Prediction", "Input Prediction", "Suggestion", 'Edit Suggestion','Final Outcome'], 
    icons=['house', 'cloud-upload', "list-task", 'gear','happy'], 
    orientation="horizontal", manual_select=manual_select, key='menu_4')
    st.button(f"Move to next: Screen ", key='switch_button')
    
    # Forecast Prediction Screen
    if selected4 == 'Forecast Prediction':
        forecast_prediction()
            
    if selected4 == 'Input Prediction':
        forecast_data_df = st.session_state.forecast_data[['Year_Month', 'Profit']]
        forecast_data_df = forecast_data_df.rename(columns = {'Profit':'AI suggested profits'})
        forecast_data_df['Desired Profits'] = forecast_data_df['AI suggested profits']
        prediction_input = st.data_editor(
            forecast_data_df,
            key='forecast_data_df',
            disabled=["Year_Month",'AI suggested profits'],
            use_container_width=True, 
            height=450,
            hide_index= True,
            column_config={
            "WP": st.column_config.NumberColumn(
            format="%dcr")},
            args=[forecast_data_df]
            )
        st.session_state.prediction_input = prediction_input
        

    if selected4 == 'Suggestion':
        # col1, col2 = st.columns([2,2])
        
        # with col1:
        selection_data = dataframe_with_selections(st.session_state.suggestion_data)
        st.session_state.selected_data = selection_data
            
        # with col2:
        #st.write("Your selection:")
        st.write(selection_data)
        
    if selected4 == 'Edit Suggestion':
        # col1, col2 = st.columns(spec=[0.7, 0.3],gap="small")
        # with col1:
        
        st.title("Input Suggestions")
        st.data_editor(
            st.session_state.selected_data,
            key='edited_df',
            disabled=["Desired Profit"],
            use_container_width=True, 
            height=450,
            hide_index= True,
            column_config={
            "WP": st.column_config.NumberColumn(
            format="%dcr")},
            on_change= change_profit,
            args=[st.session_state.selected_data]
            )
        # with col2:
        st.title("Rules")
        st.write("HELLO")
    
    if selected4 == 'Final Outcome':
        col1, col2 = st.columns(2)
        data = st.session_state.selected_data
        with col1:
            st.title("Predictions")
            st.data_editor(data,disabled= True,use_container_width=True, height=455,hide_index=True)
        with col2:
            # st.title("Outcome")
            x1 = data['Month']
            # y1 = data['Profit Actual']
            y2 = data['DesiredProfit']
            fig = px.line(data, x=x1, y=[y2])
            st.plotly_chart(fig, theme="streamlit")
            # st.line_chart(data=st.session_state.selected_data, x='Profit Forecast/Prediction',y='Month',use_container_width=True)


def main():
    st.set_page_config(layout="wide")
    st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"/>',
    unsafe_allow_html=True,
        )
    page_bg_img = """
    <style>
    [data-testid = "stAppViewContainer"] {
    background: linear-gradient(270deg, #223e80 0%, #23b082 100%)
    }
    [data-testid = "stHeader"] {
        background-color: rgba(0,0,0,0);
    }
    [data-testid = "stToolbar"] {
        right: 2rem;
    }
    </style>
    """
    st.markdown(page_bg_img,unsafe_allow_html=True)
    header_html = """
    <div style="text-align: center;">
        <h1 style= "color: white;">NBA Synthesizer & Forecast modifier </h1>
    </div>
"""
    st.markdown(header_html, unsafe_allow_html=True)
    if st.session_state.page_number == 1:
        home_page() 
    elif st.session_state.page_number == 2:
        connection_details()
    elif st.session_state.page_number == 3:
        app_screens()

# Run the app
if __name__ == "__main__":
    main()
