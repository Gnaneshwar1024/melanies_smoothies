# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col


# Write directly to the app
st.title(f":cup_with_straw: Customize your Smoothie!:cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smoothie! 
  """
)
# option=st.selectbox('What is your favourate fruit?',('select one','Banana','Strawberries','Mango'))
# st.write('You have selected:', option)
cnx = st.connection("snowflake")
session = cnx.session()


name_on_smoothie = st.text_input("Name on Smoothie", "")
if name_on_smoothie:
    st.write("The name on smoothie is", name_on_smoothie)
else:
    st.write("Enter name on smoothie")
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()
pd_df = my_dataframe.to_pandas()
incredients_list=st.multiselect('Choose upto 5 incredients: ',
                               my_dataframe, max_selections=5)

# if incredients_list:
#     st.text(incredients_list)

incredients_string=''
if incredients_list:
    for incredients in incredients_list:
        incredients_string += incredients + ' '
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == incredients, 'SEARCH_ON'].iloc[0]
        # st.write('The search value for ', incredients,' is ', search_on, '.')
        st.subheader(incredients+' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/"+search_on)
# st.text(smoothiefroot_response.json())
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width = True)
    st.write('You have selected '+incredients_string)
    my_insert_stmt = """insert into orders(ingredients, name_on_order) values ('"""+ incredients_string+"""','"""+name_on_smoothie+"""')"""
    # st.write(my_insert_stmt)
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        try:
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered! '+name_on_smoothie, icon="✅")
        except Exception as e:
            st.write(e)


