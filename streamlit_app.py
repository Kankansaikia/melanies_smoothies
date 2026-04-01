import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

st.title(":cup_with_straw: Customize Your Smoothie!:cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie: ")

cnx = st.connection("snowflake")
session = cnx.session()

# Load data
my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert to pandas
pd_df = my_dataframe.to_pandas()

# Multiselect (FIXED)
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'],
    max_selections=5
)

ingredients_string = ''

if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Get SEARCH_ON value
        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen,
            'SEARCH_ON'
        ].iloc[0]

        st.write(f"The search value for {fruit_chosen} is {search_on}")

        st.subheader(fruit_chosen + ' Nutrition Information')

        # FIXED API CALL
        response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )

        st.json(response.json())

# Button outside
time_to_insert = st.button("Submit Order")

if time_to_insert and ingredients_list:
    my_insert_stmt = f"""
    insert into smoothies.public.orders(ingredients, name_on_order)
    values ('{ingredients_string}','{name_on_order}')
    """

    session.sql(my_insert_stmt).collect()
    st.success('Your Smoothie is ordered!', icon="✅")
