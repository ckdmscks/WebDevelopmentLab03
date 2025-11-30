import streamlit as st
import requests
import pandas as pd

api_key = 'cAnQL8sTZR9PXqVkTlJJfAO2etBrIh63ojCXCwNx' #this is our key

st.title("Asteroid Data Information -- Choose What you Want to See!")


st.divider()
st.write('This page allows for the following:')
st.write('**1:** Select a data range and retrieve a list of asteroids that will approach near Earth within that range.')
st.write('**2:** View a bar chart that displays speeds of those asteroids.')
st.write('**3:** Explore additional asteroid data of your choice with an area chart visualization.')
st.divider()

#start = '2024-06-01' #this is to test - we will add inputs
#end = '2024-06-07'
st.write("Selet a date range (within 7 days) to retrieve near-Earth asteroid data:")
start = st.date_input("Select start date") #these inputs must be within 7 days of each other now or it will error 
end = st.date_input("Select end date")

response = requests.get( 'https://api.nasa.gov/neo/rest/v1/feed', params={'start_date': str(start), 'end_date': str(end), 'api_key': api_key })

data = response.json()

st.header("Near-Earth Asteroid Names and Close Approach Dates Within Selected Date Range")



#build the list
asteroids = []
#each 'date_objects' is a list of asteroids for that date, so we must do an inner loop to add each item individually
for date_objects in data['near_earth_objects'].values():
    for item in date_objects:
        asteroids.append(item)


#
for item in asteroids: #print the facts
    st.write(f"**Name:** {item['name']}")
    st.write(f"**Close approach date:** {item['close_approach_data'][0]['close_approach_date']}")
    st.divider()








#make a barchart

names = []
for item in asteroids:
    names.append(item['name'])
speeds = []
for item in asteroids:
    speeds.append(float(item['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']))

data_for_barchart = {'Name':names,'Speed':speeds}

dta = pd.DataFrame(data_for_barchart)




st.subheader('Asteroid Speeds (km/h)')
st.bar_chart(dta, x='Name', y='Speed')


#dynamic display - this will be an area type of chart and will allow the user to select what typa data they want to see

st.subheader('Explore More Asteroid Data -- of Your Choice!')
option_chose = st.radio('Select another data point to see',['Miss Distance (km)', 'Estimated Diameter (minimum) (m)', 'Estimated Diameter (maximum) (m)'])

list_of_chosen = []

for item in asteroids:
    if option_chose == 'Miss Distance (km)':
        list_of_chosen.append(float(item['close_approach_data'][0]['miss_distance']['kilometers']))
    elif option_chose == 'Estimated Diameter (minimum) (m)':
        list_of_chosen.append(float(item['estimated_diameter']['meters']['estimated_diameter_min']))
    elif option_chose == 'Estimated Diameter (maximum) (m)':
        list_of_chosen.append(float(item['estimated_diameter']['meters']['estimated_diameter_max']))

data_for_areachart = {'Name':names,option_chose: list_of_chosen}

dataaa = pd.DataFrame(data_for_areachart)



st.area_chart(dataaa,x = 'Name', y=option_chose)


