import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
#import plotly.figure_factory as ff


st.title('Uber pickups in NYC')

DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
            'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

@st.cache_data
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

data_load_state = st.text('Loading data...')
data = load_data(10000)
data_load_state.text("Done!")

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

st.subheader('Number of pickups by hour')
hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
st.bar_chart(hist_values)

# Some number in the range 0-23
hour_to_filter = st.slider('hour', 0, 23, 17)
filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

st.subheader('Map of all pickups at %s:00' % hour_to_filter)
# Use PyDeck for 3D map
#print(filtered_data.columns) #Use this to check the column names.
chart_data = filtered_data[['lat', 'lon']] # Create a new dataframe with only the lat and long.  Make sure these column names are correct.
chart_data.rename(columns={'lat': 'lat', 'lon': 'lon'}, inplace=True) # Rename the columns so that it works with pydeck

st.pydeck_chart(
    pdk.Deck(
        map_style=None,  # You can choose a map style, or set to None for a simple map
        initial_view_state=pdk.ViewState(
            latitude=40.73, # approximate NYC latitude
            longitude=-73.99, # approximate NYC longitude
            zoom=11,
            pitch=50, # Add a pitch to make it 3D
        ),
        layers=[
            pdk.Layer(
                "HexagonLayer", # Use a HexagonLayer to show density in 3D
                data=chart_data,
                get_position="[lon, lat]",
                radius=200,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True, # This is important for 3D
            ),
            pdk.Layer( # Add a ScatterplotLayer for individual points (optional, can be combined with HexagonLayer)
                "ScatterplotLayer",
                data=chart_data,
                get_position="[lon, lat]",
                get_color="[200, 30, 0, 160]",
                get_radius=100, # Adjust the radius of the points
            ),
        ],
    )
)

data['timestamp'] = pd.to_datetime(data['date/time'])

# ดึงข้อมูลนาที
data['minute'] = data['timestamp'].dt.minute

# นับจำนวนเคสในแต่ละนาที
minute_counts = data.groupby('minute').size().reset_index(name='case_count')

# สร้าง Bar Chart
fig3 = px.bar(minute_counts, x='minute', y='case_count',
             labels={'minute': 'นาที', 'case_count': 'จำนวนเคส'},
             title='จำนวนเคสในแต่ละนาที (0-59)')
#fig3.show()

st.plotly_chart(fig3)

if "counter" not in st.session_state:
    st.session_state.counter = 0

st.session_state.counter += 1

st.header(f"This page has run {st.session_state.counter} times.")
st.button("Push to increase runtimes")
