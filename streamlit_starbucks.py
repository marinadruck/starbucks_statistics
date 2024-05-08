import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pydeck as pdk


def styling(): #CSS
    st.markdown("""
        <style>

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
    font-size:25px;
    }
            .stTabs [data-baseweb="tab-highlight"] {
        background-color:rgba(40,88,61,1) ;
    }


        </style>""", unsafe_allow_html=True) #[ST4] Font and page design


def nav_tab():
    stats_choice, stats_highest_general = st.tabs(["Chosen City","General Stats"])
    with stats_choice:
        choice_page()
    with stats_highest_general:
        highest_page()


def get_data():  #[PY3] A function that returns a value and is called in at least two different places in your program
    return pd.read_excel("/Users/marina/Library/CloudStorage/OneDrive-BentleyUniversity/first_python/Projects/Final_Project/starbucks_10000_sample.xlsx")


#I had to put these outside any function because they will be used in many different functions so its simpler
df = get_data()
#Sidebar - to select country, state, and city
#[ST1](selectbox)
selected_country = st.sidebar.selectbox("Select Country", df["CountryCode"].unique()) #[ST4](sidebar)
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


def choice_page():

    st.title(f"Stats for {selected_city}, {selected_state}, {selected_country} ")
    city_count, state_count, country_count = st.columns(3)
    with city_count:
        st.header(f"No. of Starbucks locations in {selected_city}")
        st.subheader(f"{len(filtered_df_city)}")

        Map(filtered_df_city,10)
    with state_count:
        st.header(f"No. of Starbucks locations in {selected_state}")
        st.subheader(f"{len(filtered_df_state)}")

        Map(filtered_df_state,4)
    with country_count:
        st.header(f"No. of Starbucks locations in {selected_country}")
        st.subheader(f"{len(filtered_df_country)}")

        Map(filtered_df_country, 1)

def highest_page():
    high_score()
    top_count = st.slider("Top Count:", min_value=1, max_value=6, value=3) #[ST2] At least three Streamlit different widgets (sliders)
    graph_top(top_count)

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
        state_counts= state_counts[0:count]#[DA1] Cleaning or manipulating data

        fig, ax = plt.subplots() #[VIZ2] At least three different types of charts with titles, colors, labels, legends
        ax.bar(state_counts.index.astype(str), state_counts.values)
        plt.xlabel("State")
        plt.ylabel("Number of Locations")
        st.pyplot(fig)
    def top_cities():

        st.write(f"Top {count} Cities with most Starbucks locations")
        city_counts = df["City"].value_counts().head(count)
        city_counts=city_counts[0:count]
        fig, ax = plt.subplots() #[VIZ3] At least three different types of charts with titles, colors, labels, legends
        ax.bar(city_counts.index, city_counts.values)

        plt.xlabel("City")
        plt.ylabel("Number of Locations")
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
