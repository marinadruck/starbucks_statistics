"""
Name: Marina Fossati Druck
CS230: CS230-4
Data: Starbucks Locations
URL:
Description: This program will analyze data from Starbucks Locations, the User can find locations based on country, state, and city. The User can also see what places have the most locations.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pydeck as pdk


def styling():  # CSS
    st.markdown("""
        <style>
            /* Existing styles for tabs */
            .stTabs [data-baseweb="tab-list"] {
                gap: 80px;
            }
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                white-space: pre-wrap;
                background-color: rgba(30,57,50,0);
                color: white;
                border-radius: 4px 4px 0px 0px;
                gap: 1px;
                padding-top: 1px;
                padding-bottom: 10px;
            }
            .stTabs [aria-selected="true"] {
                color: rgba(65,113,86,1);
            }
            .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
                font-size: 25px;
            }
            .stTabs [data-baseweb="tab-highlight"] {
                background-color: rgba(40,88,61,1);
            }

            /* New style for text wrapping */
            .stMarkdownContainer, .stText {
                white-space: normal;  /* Ensures text wraps within its container */
            }
        </style>
    """, unsafe_allow_html=True) #[ST4] Font and page design


def nav_tab():
    stats_choice, stats_highest_general = st.tabs(["Chosen City","General Stats"])
    with stats_choice:
        choice_page()
    with stats_highest_general:
        highest_page()


def get_data():  #[PY3] A function that returns a value and is called in at least two different places in your program
    return pd.read_excel("starbucks_10000_sample.xlsx")


#I had to put these outside any function because they will be used in many different functions so its simpler
df = get_data()
#Sidebar - to select country, state, and city
#[ST1](selectbox)
unique_countries = sorted([country for country in df["CountryCode"].unique()]) #[PY4] List comprehension
selected_country = st.sidebar.selectbox("Select Country", unique_countries) #[ST4](sidebar)
selected_state = st.sidebar.selectbox("Select State", df[df["CountryCode"] == selected_country]["CountrySubdivisionCode"].unique())
selected_city = st.sidebar.selectbox("Select City", df[(df["CountryCode"] == selected_country) & (df["CountrySubdivisionCode"] == selected_state)]["City"].unique())


#[DA4] & [DA5] Filtering data based on user selection to 3 categories: city , state and country
filtered_df_city = df[(df["CountryCode"] == selected_country) & (df["CountrySubdivisionCode"] == selected_state) & (df["City"] == selected_city)]
filtered_df_state = df[(df["CountryCode"] == selected_country) & (df["CountrySubdivisionCode"] == selected_state)]
filtered_df_country = df[(df["CountryCode"] == selected_country)]


def header():
    styling()
    #using html to have the green background around starbucks
    st.markdown(
        '<div style="display:inline-block;background-color:#1C4C31;color:#ffffff;font-size:45px;border-radius:2%; font-weight: bold;">Starbucks</div><div style="background-color:#00000000;color:#ffffff;font-size:45px;border-radius:2%; font-weight: bold;display: inline-block">&nbsp Statistics</div>',
        unsafe_allow_html=True) #[ST4] Font and page design
    #*** - to make italic and bold
    st.caption("***Find the Closest Starbucks To You***")

def display_location_details(filtered_df):
    st.write(f"Details of Starbucks locations in {selected_city}")
    for index, row in filtered_df.iterrows(): #[DA8] Iterrows
        st.text(f"Location ID: {row['Id']}")
        st.text(f"Address: {row['Street1']}")
        st.text(f"Latitude: {row['Latitude']}, Longitude: {row['Longitude']}")
        st.text("----------")


def choice_page():
    st.title(f"Stats for {selected_city}, {selected_state}, {selected_country}")
    city_count, state_count, country_count = st.columns(3)
    with city_count:
        st.header(f"No. of Starbucks locations in {selected_city}")
        st.subheader(f"{len(filtered_df_city)}")
        Map(filtered_df_city, 10)
        details_button = st.button("Show Details", key="city")  # Store the button press state
    with state_count:
        st.header(f"No. of Starbucks locations in {selected_state}")
        st.subheader(f"{len(filtered_df_state)}")
        Map(filtered_df_state, 4)
    with country_count:
        st.header(f"No. of Starbucks locations in {selected_country}")
        st.subheader(f"{len(filtered_df_country)}")
        Map(filtered_df_country, 1)

    if details_button:  #Check if details should be displayed
        display_location_details(filtered_df_city)


def location_summary(df, region_col='CountryCode', region='US'): #[PY2] A function that returns more than one value
    region_df = df[df[region_col] == region]
    total_locations = region_df.shape[0]
    avg_locations_per_city = region_df['City'].value_counts().mean()
    max_locations_in_city = region_df['City'].value_counts().max()

    return total_locations, avg_locations_per_city, max_locations_in_city

def highest_page():
    high_score()
    top_count = st.slider("Top Count:", min_value=1, max_value=6, value=3) #[ST2] At least three Streamlit different widgets (sliders)
    graph_top(top_count)

    total, avg, max_loc = location_summary(df, 'CountryCode', selected_country)
    st.write(f"In {selected_country}, there are a total of {total} Starbucks locations, with an average of {avg:.2f} per city. The highest number of locations in any single city is {max_loc}.")

def Map(filtered_df,zoom=10): #[PY1] A function with two or more parameters, one of which has a default value & [VIZ1] Map
    st.write("Starbucks locations")
    view_state = pdk.ViewState(
        latitude=np.median(filtered_df["Latitude"]),
        longitude=np.median(filtered_df["Longitude"]),
        zoom=zoom
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_df,
        get_position=["Longitude", "Latitude"],
        get_radius=100,
        get_fill_color=[255, 0, 0],
        pickable=True,
    )
    tooltip = {"text": "Starbucks Location"}
    map_ = pdk.Deck( #[VIZ1][VIZ4] Map
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=view_state,
        layers=[layer],
        tooltip=tooltip
    )
    st.pydeck_chart(map_)


def graph_top(count=5):
    plt.rcParams.update({'font.size': 5})
    def top_countries():
        st.write(f"Top {count} Countries with most Starbucks locations")

        #[DA2] Sorting data in ascending or descending order, by one or more columns
        #(the below line for value_counts() function does sort the values in ascending order
        country_counts = df["CountryCode"].value_counts() #[DA7] Add/create new frequency count
        country_counts=country_counts[0:count]
        fig ,ax = plt.subplots() #[VIZ1] At least three different types of charts with titles, colors, labels, legends
        ax.bar(country_counts.index, country_counts.values)

        plt.style.use('_mpl-gallery')
        plt.xlabel("Country")
        plt.ylabel("Number of Locations")
        st.pyplot(fig)

    def top_states():
        st.write(f"Top {count} States with most Starbucks locations")
        state_counts = df["CountrySubdivisionCode"].value_counts().head(count)
        fig, ax = plt.subplots()
        ax.plot(state_counts.index.astype(str), state_counts.values, marker='o', linestyle='-', color='green')
        plt.xlabel("State")
        plt.ylabel("Number of Locations")
        plt.title("Top States by Starbucks Locations")
        st.pyplot(fig)

    def top_cities(): #calculates the total of starbucks locations of the cities being considered and the percentage of each city
        st.write(f"Top {count} Cities with most Starbucks locations")
        city_counts = df["City"].value_counts().head(count)
        fig, ax = plt.subplots()
        ax.pie(city_counts, labels=city_counts.index, autopct='%1.1f%%', startangle=90, colors=plt.cm.Pastel1.colors)
        plt.title("Top Cities by Starbucks Locations")
        st.pyplot(fig)


    st.divider()
    top_countries()
    st.divider()
    top_states()
    st.divider()
    top_cities()
    st.divider()

def high_score():
    city_count, state_count, country_count = st.columns(3)
    with city_count:
        st.write("City with the most Starbucks locations in the world:")
        city_most_locations = df["City"].value_counts().idxmax()
        city_locations_count = df["City"].value_counts().max() #[DA3] Top largest or smallest values of a column
        st.title(f"{city_most_locations}\n  {city_locations_count} locations")
    with state_count:
        st.write("State with the most Starbucks locations in the world:")
        state_most_locations = df["CountrySubdivisionCode"].value_counts().idxmax()
        state_locations_count = df["CountrySubdivisionCode"].value_counts().max()
        st.title(f"{state_most_locations}\n {state_locations_count} locations")

    with country_count:
        st.write("Country with the most Starbucks locations in the world:")
        country_most_locations = df["CountryCode"].value_counts().idxmax()
        country_locations_count = df["CountryCode"].value_counts().max()
        st.title(f"{country_most_locations}\n  {country_locations_count} locations")

def main():
    df = get_data()
    header()
    nav_tab()



if __name__ == '__main__':
    main()
