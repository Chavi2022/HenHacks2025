# tree.py

decisionTree = {
    "root": {
        "question": "Dost thou experience any of these ailments: fever, hacking cough, shortness of breath, or wearisome fatigue?",
        "fever": "fever",
        "cough": "cough",
        "shortness_of_breath": "shortness_of_breath",
        "fatigue": "fatigue",
        "none": "age",
    },
    "fever": {
        "question": "Doth thy fever rise above 38 degrees by the physician’s measure?",
        "yes": "high_fever",
        "no": "low_fever",
    },
    "cough": {
        "question": "Is thy cough both persistent and troublesome, as though it lingereth without relief?",
        "yes": "persistent_cough",
        "no": "mild_cough",
    },
    "high_fever": {
        "question": "Hast thou been beset by chills or a racing pulse alongside thy fever?",
        "yes": "flu_like_symptoms",
        "no": "common_cold",
    },
    "low_fever": {
        "question": "Hast thou a sore throat or a mild cough to accompany thy lesser fever?",
        "yes": "upper_respiratory_infection",
        "no": "mild_viral_infection",
    },
    "persistent_cough": {
        "question": "Is thy cough joined by pain in the chest or a wheezing in thy breaths?",
        "yes": "serious_respiratory_condition",
        "no": "upper_respiratory_infection",
    },
    "mild_cough": {
        "question": "Doth thy cough show signs of abating over time?",
        "yes": "recovering_mild_cough",
        "no": "monitor_for_changes",
    },
    "flu_like_symptoms": {
        "question": "Dost thou endure aches of muscle or body pangs?",
        "yes": "influenza",
        "no": "viral_infection",
    },
    "common_cold": {
        "question": "Hast thou a runny nose or feeling of congestion within thy head?",
        "yes": "common_cold_diagnosis",
        "no": "mild_infection",
    },
    "shortness_of_breath": {
        "question": "Art thou burdened by tightness or pain within thy chest?",
        "yes": "serious_respiratory_issue",
        "no": "mild_breathing_issue",
    },
    "serious_respiratory_issue": {
        "question": "Hast thou inhaled dust, smoke, or other foul irritants of late?",
        "yes": "allergic_reaction_or_asthma",
        "no": "potential_respiratory_infection",
    },
    "fatigue": {
        "question": "Doth thy fatigue come with dizziness or fainting spells?",
        "yes": "serious_cardiovascular_issue",
        "no": "general_fatigue",
    },
    "serious_cardiovascular_issue": {
        "question": "Hast thou a known history of heart troubles or high pressure of the blood?",
        "yes": "cardiovascular_condition",
        "no": "investigate_further",
    },
    "age": {
        "question": "May I know thy years? How long hast thou walked upon this earth?",
        "<10": "weight_child",
        "10-18": "weight_teen",
        "18-50": "gender",
        ">50": "older_adult",
    },
    "weight_child": {
        "question": "Pray tell, what is thy weight? (in stones, pounds, or kilograms as thou preferst)",
        "low_weight": "low_weight_child",
        "normal_weight": "normal_weight_child",
        "high_weight": "high_weight_child",
    },
    "weight_teen": {
        "question": "Again, how heavy art thou, good youth? (in such measure as thou knowest best)",
        "low_weight": "low_weight_teen",
        "normal_weight": "normal_weight_teen",
        "high_weight": "high_weight_teen",
    },
    "gender": {
        "question": "Art thou male, female, or of another condition thou wilt name?",
        "male": "adult_male",
        "female": "pregnancy",
        # If you wish to handle "other" or "non-binary" in a medieval sense,
        # you can add an additional branch here.
    },
    "pregnancy": {
        "question": "Art thou with child or in the midst of thy monthly courses?",
        "pregnant": "pregnancy",
        "menstruating": "menstruation",
        "no": "adult_female",
    },
    "menstruation": {
        "question": "Art thy monthly pains severe, with great bleeding or dire cramps?",
        "yes": "severe_menstruation",
        "no": "normal_menstruation",
    },
    "older_adult": {
        "question": "Hast thou any enduring maladies such as the sugar-sickness, heart-woes, or the malady of high blood pressure?",
        "yes": "chronic_condition",
        "no": "healthy_older_adult",
    },
    # Additional branches can remain or be added with similar medieval style
}
