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
    st.session_state.initial_data = pd.read_csv('initial_dataset.csv',dtype={'Year': str})[['Year','Month','ProfitActual']].rename(columns = {'ProfitActual':'Profit'})
    st.session_state.forecast_data = pd.read_csv('forecasted_output_prophet.csv')[['Date','Profit']].rename(columns={'Profit': 'Forecasted Profit (AI)'})
    st.session_state.forecast_data['Year'] = pd.to_datetime(st.session_state.forecast_data['Date']).dt.year
    st.session_state.forecast_data['Month'] = pd.to_datetime(st.session_state.forecast_data['Date']).dt.month_name()
    st.session_state.forecast_data['Year_Month'] =  st.session_state.forecast_data['Year'].astype(str) + ' ' + st.session_state.forecast_data['Month'].str.slice(0, 3) 
    st.session_state.initial_data['Year_Month'] = st.session_state.initial_data['Year'].astype(str) + ' ' + st.session_state.initial_data['Month'].str.slice(0, 3)
    st.session_state.suggestion_data = pd.read_csv('suggestion_data.csv', dtype={'Year': str})
    st.session_state.final_outcome = {}
    st.session_state.final_outcome['Year'] = st.session_state.forecast_data['Year'].astype("str")
    st.session_state.final_outcome['Month'] = st.session_state.forecast_data['Month']
    st.session_state.final_outcome['Predicted Outcome (AI)'] = st.session_state.forecast_data['Forecasted Profit (AI)']
        
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
    
    # [data-testid = "stMarkdownContainer"]{
    #     color: white;    
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
        selected_option = st.selectbox("Select the Project", [""] +["q-gcp-00863-fsihackathon-23-12"])
        if selected_option:
            selected_option = st.selectbox("Select the Dataset", [""] +["ba_synthesizer_forecast_modifier"])
            if selected_option:
                selected_option = st.selectbox("Select the Table", [""] +["forecasted_output_firstpass"])
                if selected_option:        
                    header_html = """
                    <div style="text-align: center;">
                        <h1 style= "color: beige;">Expected Outcome Information</h1>
                    </div>
                    """
                    st.markdown(header_html, unsafe_allow_html=True)
                    selected_option = st.selectbox("Select the 'Prediction' column from the dataset to analyze", [""] +["Profit","Sales","Rention","R&D Expenses","Administration expense"])
                    if selected_option:
                        selected_option = st.selectbox("Select the 'Year' to Predict", [""] +["2024","2025","2026","2027","2028"])
                        st.write("")
                        if selected_option:
                            col1,col2,col3 = st.columns(spec=[5,7,3.5],gap="small")
                            with col3:
                                if st.button("Show Predictions"):
                                    st.session_state.page_number = 3
                                    st.rerun()
                        else:
                            st.write("Select Any option")
                    else:
                        st.write("Select Any option")
                else:
                    st.write("Select Any option")
            else:
                st.write("Select Any option")
        else:
            st.write("Select Any option")
               
def dataframe_with_selections(df):
    
    df_with_selections = df.copy()
    df_with_selections.insert(0, "Select", False)

    # Get dataframe row-selections from user with st.data_editor
    edited_df = st.data_editor(
        df_with_selections,
        hide_index=True,
        column_config={"Select": st.column_config.CheckboxColumn(required=True),
                       "Suggestion":{"alignment": "left"},
                       "PremiumsCollected":{"alignment": "left"},
                       "OverheadCharges":{"alignment": "left"},
                       "HeadCount":{"alignment": "left"},
                       "MarketingExpense":{"alignment": "left"},
                       "R&DExpense":{"alignment": "left"},
                       "AdminstrationExpenses":{"alignment": "left"},
                       "DesiredProfit":{"alignment": "left"}},
        use_container_width=True,
        disabled=df.columns,
    )

    # Filter the dataframe using the temporary column, then drop the column
    selected_rows = edited_df[edited_df.Select]
    return selected_rows.drop('Select', axis=1).reset_index(drop=True)
            
# Function to change the profit in suggestion Screen 
def change_profit(df):
    state = st.session_state["edited_df"]
    for index, updates in state["edited_rows"].items():
        for key, value in updates.items():
            st.session_state["selected_data"].loc[st.session_state["selected_data"].index == index, key] = value
        Profit =  st.session_state.selected_data.at[index, 'PremiumsCollected'] - st.session_state.selected_data.loc[index, ['OverheadCharges','HeadCount','MarketingExpense','R&DExpense','AdminstrationExpenses']].sum()
        st.session_state.selected_data.loc[st.session_state["selected_data"].index == index, "DesiredProfit"] = Profit

def forecast_prediction():
    col1, col2 = st.columns([2,2])
    with col1:
        st.data_editor(st.session_state.forecast_data[['Year_Month', 'Forecasted Profit (AI)']],
                       column_config={"Year_Month": {"alignment": "left"},"Forecasted Profit (AI)":{"alignment": "left"}},
                       disabled=True,
                       use_container_width=True,
                       height=450,
                       hide_index= True)
        

    with col2:

        data = pd.concat([st.session_state.initial_data[['Year_Month','Profit']],st.session_state.forecast_data[['Year_Month','Forecasted Profit (AI)']]])        
        fig = px.bar(data, x='Year_Month', y=['Profit','Forecasted Profit (AI)'])

        fig.update_layout(
            legend_title_text="Profits",
            xaxis_title = 'Year Trend',
            yaxis_title = 'Profit',
            title = 'Predictions',
            paper_bgcolor='#FFFFFF',
            plot_bgcolor='#FFFFFF')
            
        #fig.show()
        st.plotly_chart(fig)

def input_prediction():
    # st.session_state.forecast_data = st.session_state.forecast_data.rename(columns = {'Forecasted Profit (AI)':'AI suggested profits'})
    st.session_state.forecast_data['Desired Profits'] = st.session_state.forecast_data['Forecasted Profit (AI)']
    
    Desired_profit = st.data_editor(
        st.session_state.forecast_data[['Year_Month','Forecasted Profit (AI)','Desired Profits']],
        key='forecast_data_df',
        disabled=["Year_Month",'Forecasted Profit (AI)'],
        use_container_width=True, 
        height=450,
        hide_index= True,
        column_config={
            "Year_Month": {"alignment": "left"},
            "Forecasted Profit (AI)": {"alignment": "left"},
            "Desired Profits" : {"alignment": "left"}
            }
        )['Desired Profits']

    st.session_state.final_outcome['Desired outcome(Manual)'] = Desired_profit 

def suggestions():

    selected_data = dataframe_with_selections(st.session_state.suggestion_data).reset_index(drop=True)
    st.session_state.selected_data = selected_data.reset_index(drop=True)
    
    st.data_editor(st.session_state.selected_data,use_container_width=True,
                   column_config={"Suggestion" : {"alignment": "left"},
                       "PremiumsCollected":{"alignment": "left"},
                       "OverheadCharges":{"alignment": "left"},
                       "HeadCount":{"alignment": "left"},
                       "MarketingExpense":{"alignment": "left"},
                       "R&DExpense":{"alignment": "left"},
                       "AdminstrationExpenses":{"alignment": "left"},
                       "DesiredProfit":{"alignment": "left"}},
                   disabled=True,
                   hide_index=True
                   )
    st.session_state.selected_data.reset_index(drop=True)
    
def edit_suggestions():
    header_html = """
            <div style="text-align: left;">
                <h1 style= "color: beige;">Input Suggestions</h1>
            </div>
        """
    st.markdown(header_html, unsafe_allow_html=True)
    st.session_state.selected_data.reset_index(drop=True)
    Target_profit = st.data_editor(
        st.session_state.selected_data,
        key='edited_df',
        disabled=['Suggestion','Year','Month','DesiredProfit'],
        use_container_width=True, 
        height=450,
        hide_index= True,
        column_config={
        "DesiredProfit": st.column_config.NumberColumn(
        format="%dcr"),
        "Suggestion" : {"alignment": "left"},
        "Year": {"alignment": "left"},
        "Month": {"alignment": "left"},
        "DesiredProfit": {"alignment": "left"},
        "PremiumsCollected": {"alignment": "left"},
        "OverheadCharges": {"alignment": "left"},
        "HeadCount": {"alignment": "left"},
        "MarketingExpense": {"alignment": "left"},
        "R&DExpense": {"alignment": "left"},
        "AdminstrationExpenses":{"alignment": "left"}     
        },
        on_change= change_profit,
        args=[st.session_state.selected_data]
        )['DesiredProfit']
    st.session_state.final_outcome['Target Profit (AI + Manual)'] = Target_profit


    with st.container(border=True):
        header_html = """
                <div style="text-align: center;">
                    <h1 style= "color: beige;">Rules</h1>
                </div>
            """
        st.markdown(header_html, unsafe_allow_html=True)
        st.write("HELLO")
    
def final_outcome():
    
    header_html = """
            <div style="text-align: left;">
                <h1 style= "color: beige;">Final Outcome</h1>
            </div>
        """
    st.markdown(header_html, unsafe_allow_html=True)
    data = pd.DataFrame(st.session_state.final_outcome)
    st.data_editor(data,column_config= {"Year":{"alignment": "left"},"Month": {"alignment": "left"},"Predicted Outcome (AI)":{"alignment": "left"},"Desired outcome(Manual)":{"alignment": "left"},"Target Profit (AI + Manual)":{"alignment": "left"}},disabled= True,use_container_width=True, height=455,hide_index=True)

    header_html = """
        <div style="text-align: center;">
            <h1 style= "color: beige;">Comparison</h1>
        </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
    x1 = data['Month']
    y1 = data['Predicted Outcome (AI)']
    y2 = data['Desired outcome(Manual)']
    y3 = data['Target Profit (AI + Manual)']
    fig = px.line(data, x=x1, y=[y1,y2,y3])
    fig.update_layout(
            legend_title_text="Profits",
            xaxis_title = 'Months',
            yaxis_title = 'Profit',
            title = 'Predictions for the Year 2024',
            paper_bgcolor='#FFFFFF',
            plot_bgcolor='#FFFFFF')
    
    st.plotly_chart(fig,use_container_width=True)
    
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
        input_prediction()

    if selected4 == 'Suggestion':
        suggestions()
        
    if selected4 == 'Edit Suggestion':     
        edit_suggestions()
    
    if selected4 == 'Final Outcome':
        final_outcome()


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
