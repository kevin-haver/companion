import streamlit as st
from streamlit.logger import get_logger
import json
from collections import Counter
import itertools
import pandas as pd

LOGGER = get_logger(__name__)

# Specify the file path for the plant data
file_path = 'plants.json'

# Read the JSON file
with open('plants.json') as f:
    data = json.load(f)

# Create list of all plant names
plant_names = [p['plantName'] for p in data['plants']]

# By which plants is each plant helped?
plants_helped_by = {plant['plantName']: [companion['plantName'] for companion in data['plants'] if companion['plantCode'] in plant['companionPlantCodes']] for plant in data['plants']}

# Which plant does each plant help?
plants_help = {companion['plantName']: [plant['plantName'] for plant in data['plants'] if companion['plantCode'] in plant['companionPlantCodes']] for companion in data['plants']}


# Get all effects between plants
def get_effects(plants):
    effects = set()
    for plant in plants:
        helped_plants = plants_help.get(plant, set())
        effects.update((plant, helped) for helped in helped_plants if helped in plants)
    return effects

# Generate recommendations by adding a helping plant to each combination
def get_recommendations(combination):
    recommendations = set()
    for plant in combination:
        for helping_plant in plants_helped_by.get(plant, set()):
            if helping_plant not in combination:
                recommendations.add(helping_plant)
    return recommendations

# Generate all possible combinations of 3 plants and rank them by highest score
def get_best_combinations(plants):
    combinations = {tuple(sorted(combo)) for combo in itertools.combinations(plants, 3)}
    combinations_ranked = []
    for combination in combinations:
        effects = get_effects(combination)
        score = len(effects)
        recommendations = get_recommendations(combination)
        for recommendation in recommendations:
            recommendation_combinaton = combination + (recommendation,)
            # Only keep effects where the recommendation is helping, not where it is helped
            recommendation_effects = set([effect for effect in get_effects(recommendation_combinaton) if effect[1] != recommendation_combinaton[-1]])
            recommendation_effects -= effects
            recommendation_score = len(recommendation_effects)
            combinations_ranked.append((combination, score, effects, recommendation, recommendation_combinaton, recommendation_score, recommendation_effects))
    df = pd.DataFrame(combinations_ranked, columns=['Combination', 'Score', 'Effects', 'Recommendation', 'Recommendation_Combination', 'Recommendation_Score', 'Recommendation_Effects'])
    return df.sort_values(by=['Score', 'Recommendation_Score'], ascending=[False, False])

# Design garden beds by picking the best combinations, preventing duplicate plants
def design_garden_beds(df):
    garden_beds = []
    selected_plants = set()
    while not df.empty:
        max_score_row = df.iloc[0]
        max_score_combination = max_score_row['Combination']
        max_score_recommendation_combination = max_score_row['Recommendation_Combination']
        max_score = max_score_row['Score'] + max_score_row['Recommendation_Score']
        garden_beds.append((
            max_score_combination,
            max_score_row['Score'],
            max_score_row['Effects'],
            max_score_row['Recommendation'],
            max_score_recommendation_combination,
            max_score_row['Recommendation_Score'],
            max_score_row['Recommendation_Effects'],
            max_score
        ))
        selected_plants.update(max_score_combination)
        selected_plants.update(max_score_recommendation_combination)
        df = df[~df['Combination'].apply(lambda x: any(plant in selected_plants for plant in x))]
        df = df[~df['Recommendation'].apply(lambda x: any(plant in selected_plants for plant in x))]
    garden_beds_df = pd.DataFrame(garden_beds, columns=df.columns.tolist() + ['Combination', 'Score', 'Effects', 'Recommendation', 'Recommendation_Combination','Recommendation_Score', 'Recommendation_Effects', 'Total_Score'])
    return garden_beds_df

def run():
    st.set_page_config(
        page_title="Companion",
        page_icon=":seedling:",
    )

    st.write("# Welcome to Companion :seedling:")

    st.write('### Selection')
    selected_plants = st.multiselect(
    'Which plants would you like in your garden?',
    plant_names, [])

    # What are the positive effects between the current plants?
    st.write('### Companions')
    st.write('These plants help eachother:')
    helping_plants = []
    for plant in selected_plants:
        helped_plants = [p for p in plants_help[plant] if p in selected_plants]
        helping_plants += [p for p in plants_helped_by[plant] if p not in selected_plants]
        if helped_plants:
          st.write('-', plant, 'helps', ', '.join(helped_plants))
    
    # Which plants can be added to the garden for more positive effects?
    st.write('### Recommendations')
    st.write('These plants are great additios to your garden:')    
    for helping_plant, cnt in Counter(helping_plants).most_common(10):
      helped_plants = [p for p in plants_help[helping_plant] if p in selected_plants]
      st.write('-', helping_plant, 'helps', ', '.join(helped_plants))

    # Get the best combinations
    st.write('### Combinations')
    st.write('This is what your garden beds could look like:') 
    combinations_df = get_best_combinations(selected_plants)

    # Design garden beds
    garden_beds_df = design_garden_beds(combinations_df)

    # Iterate through each row of the garden_beds_df
    for index, row in garden_beds_df.iterrows():
        combination = row['Combination']
        original_score = row['Score']
        original_effects = row['Effects']
        recommendation = row['Recommendation']
        recommendation_combination = row['Recommendation_Combination']
        recommendation_score = row['Recommendation_Score']
        recommendation_effects = row['Recommendation_Effects']

        # Print the positive effects for the original combination
        original_plants_string = ', '.join(combination)
        st.write(f"Combine {original_plants_string} for {original_score} positive effects")
        for effect in original_effects:
            st.write("-", effect[0], "helps", effect[1])

        # Print the positive effects for the recommendation
        if recommendation:
            additional_score = recommendation_score
            st.write(f"\nAdd {recommendation} for {additional_score} additional effects")
            for effect in recommendation_effects:
                st.write("-", effect[0], "helps", effect[1])
        st.write()

if __name__ == "__main__":
    run()
