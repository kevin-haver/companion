import streamlit as st
import csv
import pandas as pd
from itertools import combinations

def read_companion_effects(file_path):
    """Reads companion effects from a CSV file."""
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        return {(row[0], row[1]): row[2] for row in reader}

def get_all_plants(companion_effects):
    """Gets all unique plant names from companion effects."""
    all_plants = set()
    for pair in companion_effects.keys():
        all_plants.update(pair)
    return sorted(all_plants)

def find_helper_plants(plant, companion_effects):
    """Finds helper plants for a given plant."""
    return [p1 for (p1, p2), effect in companion_effects.items() if p2 == plant]

def generate_combinations(preferred_plants, companion_effects, max_plants):
    """Generates combinations of preferred plants and their helper plants."""
    combinations_list = []
    for size in range(1, max_plants):
        for combo in combinations(preferred_plants, size):
            combinations_list.append(combo)
            helper_plants = []
            for plant in combo:
                helper_plants.extend(find_helper_plants(plant, companion_effects))
            for helper_plant in helper_plants:
                if helper_plant not in combo:
                    new_combination = list(combo) + [helper_plant]
                    if tuple(new_combination) not in combinations_list:
                        combinations_list.append(tuple(new_combination))
    return combinations_list

def calculate_combination_score(combination, companion_effects):
    """Calculates the score of a combination based on companion effects."""
    pairs = [(plant1, plant2) for plant1 in combination for plant2 in combination if plant1 != plant2]
    return sum(1 for pair in pairs if companion_effects.get(pair))

def design_garden_beds(all_combinations, companion_effects, preferred_plants):
    """Designs garden beds based on combinations of plants."""
    df = pd.DataFrame([{'Combination': combo,
             'Score': calculate_combination_score(combo, companion_effects),
            'Plants': len(combo),
            'Preferred_plants': sum(1 for plant in combo if plant in preferred_plants)} for combo in all_combinations]
    )

    df_sorted = df.sort_values(by=['Score', 'Preferred_plants', 'Plants'], ascending=[False, False, True])

    garden_beds = []
    for _, row in df_sorted.iterrows():
        combination = row['Combination']
        for bed in garden_beds:
            if any(plant in bed for plant in combination):
                break
        else:
            garden_beds.append(combination)

    return garden_beds

def print_garden_beds(garden_beds, companion_effects, preferred_plants):
    """Prints the designed garden beds."""
    for i, bed in enumerate(garden_beds, start=1):
        with st.container(border=True):
            st.write('**' + 'Garden bed ' + str(i) + '**')         
            for plant, col in zip(bed, st.columns(len(bed))):
                if plant in preferred_plants:
                    col.button(plant, type='primary', help='Plant selected by you')
                else:
                    col.button(':bulb: ' + plant, help='Recommended plant that helps other plants in your selection')
            expander = st.expander("See effects")
        pairs = [(plant1, plant2) for plant1 in bed for plant2 in bed if plant1 != plant2]
        for pair in pairs:
            effect = companion_effects.get(pair)
            if effect:
                expander.write(f"- {pair[0]} helps {pair[1]} by {effect}")

def run():
    st.set_page_config(
        page_title="Companion",
        page_icon=":seedling:",
    )

    st.markdown("""
            <style>
                div[data-testid="column"] {
                    width: fit-content !important;
                    flex: unset;
                }
                div[data-testid="column"] * {
                    width: fit-content !important;
                }
            </style>
            """, unsafe_allow_html=True)

    st.write("# Welcome to Companion :seedling:")
    st.write('### Selection')

    with st.sidebar:
        st.write('**Legend**')
        st.button('Selected plant', type='primary', help='Plant selected by you')
        st.button(':bulb: Recommended plant', help='Recommended plant that helps other plants in your selection')
    
        st.write('**Settings**')
        max_plants = st.slider('Max plants per garden bed', 2, 5, 4, 1)

    companion_effects = read_companion_effects('companion_effects.csv')
    plant_names = get_all_plants(companion_effects)
    
    preferred_plants = st.multiselect(
    'Which plants would you like in your garden?',
    plant_names, [])

    if preferred_plants:
        st.write('### Garden design')
        st.markdown('Plant these in the same garden bed for optimal beneficial effects') 

        all_combinations = generate_combinations(preferred_plants, companion_effects, max_plants)
        garden_beds = design_garden_beds(all_combinations, companion_effects, preferred_plants)
        print_garden_beds(garden_beds, companion_effects, preferred_plants)

if __name__ == "__main__":
    run()