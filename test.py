"""
We can use this page to test API calls easily without committing to the full Streamlit app.
"""



import requests
import pandas as pd


start = '2024-06-01' #this is to test - we will add inputs
end = '2024-06-07'
api_key = 'cAnQL8sTZR9PXqVkTlJJfAO2etBrIh63ojCXCwNx'

response = requests.get( 'https://api.nasa.gov/neo/rest/v1/feed', params={'start_date': str(start), 'end_date': str(end), 'api_key': api_key })
data = response.json()





asteroids = []

for date_objects in data['near_earth_objects'].values():
    for item in date_objects:
        asteroids.append(item)

names = []
for item in asteroids:
    names.append(item['name'])
speeds = []
for item in asteroids:
    speeds.append(float(item['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']))


for item in asteroids: #first 5 because it's too long
    print(f"**Name:** {item['name']}")
    print(f"**Close approach date:** {item['close_approach_data'][0]['close_approach_date']}")
    print(item)
   


data_for_barchart = pd.DataFrame({'name':names,'speed':speeds})
print(data_for_barchart)