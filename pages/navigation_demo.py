
import streamlit as st

# Define the app state using st.session_state
def init_session_state():
    st.session_state.page_number = 1

# Create an instance of the app state
if "page_number" not in st.session_state:
    init_session_state()

def page_one():
    st.title("Page One")
    st.write("This is the content of Page One.")
    if st.button("Go to Page Two"):
        # Change the app state to go to Page Two
        st.session_state.page_number = 2
        st.experimental_rerun()

def page_two():
    st.title("Page Two")
    st.write("This is the content of Page Two.")
    if st.button("Go to Page One"):
        # Change the app state to go back to Page One
        st.session_state.page_number = 1
        st.experimental_rerun()

# Main app logic
def main():
    if st.session_state.page_number == 1:
        page_one()
    elif st.session_state.page_number == 2:
        page_two()

# Run the app
if __name__ == "__main__":
    main()
