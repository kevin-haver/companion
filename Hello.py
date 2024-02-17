import streamlit as st
from streamlit.logger import get_logger
import json
from collections import Counter

LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="Companion",
        page_icon=":seedling:",
    )

    st.write("# Welcome to Companion :seedling:")

    # Specify the file path for the plant data
    file_path = 'plants.json'

    # Read the JSON file
    with open('plants.json') as f:
        data = json.load(f)

    # Create list of all plant names
    plant_names = [p['plantName'] for p in data['plants']]

    st.write('### Selection')
    selected_plants = st.multiselect(
    'Which plants would you like in your garden?',
    plant_names, [])

    # By which plants is each plant helped?
    plants_helped_by = {plant['plantName']: [companion['plantName'] for companion in data['plants'] if companion['plantCode'] in plant['companionPlantCodes']] for plant in data['plants']}

    # Which plant does each plant help?
    plants_help = {companion['plantName']: [plant['plantName'] for plant in data['plants'] if companion['plantCode'] in plant['companionPlantCodes']] for companion in data['plants']}

    # What are the positive effects between the current plants?
    st.write('### Companions')
    st.write('Plants that help eachother:')
    helping_plants = []
    for plant in selected_plants:
        helped_plants = [p for p in plants_help[plant] if p in selected_plants]
        helping_plants += [p for p in plants_helped_by[plant] if p not in selected_plants]
        if helped_plants:
          st.write('-', plant, 'helps', ', '.join(helped_plants))
    
    # Which plants can be added to the garden for more positive effects?
    st.write('### Recommendations')
    st.write('Great plants to add to your garden:')    
    for helping_plant, cnt in Counter(helping_plants).most_common(10):
      helped_plants = [p for p in plants_help[helping_plant] if p in selected_plants]
      st.write('-', helping_plant, 'helps', ', '.join(helped_plants))

if __name__ == "__main__":
    run()
