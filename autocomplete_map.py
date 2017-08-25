# This module contains all the information needed for populating the 
# auto-complete field. Namely, the description, the doc_type, the
# field, the full name, and the type of data.
#
# "type" helps determine the comparison operators that are provided during 
# auto-complete. Can use "integer" to account for numerical comparisons and 
# "string" for other text searches.
#
# Note that in order for these to truly become searchable, must accommodate 
# them at the '/gql/_mapping' endpoint in app.py and in GraphQL. Commit: 
# https://github.com/jmatsumura/ihmp_portal_api/commit/f829c5f8baf2e0772324cfbc758144f6d5e57f54
# can show the minimum that needs to be changed. Abnormal values may need some
# additional handling in query.py in order to properly search the value in Neo4j.

gql_map = {}

# Project props
gql_map['project_name'] = {
    "description": "The name of the project within which the sequencing was organized", 
    "doc_type": "cases", 
    "field": "project.name", 
    "full": "project.name", 
    "type": "string"
    }
gql_map['project_subtype'] = {
    "description": "The subtype of the project", 
    "doc_type": "cases", 
    "field": "project.subtype", 
    "full": "project.subtype", 
    "type": "string"
    }

# Study props
gql_map['study_center'] = {
    "description": "The study's sequencing center", 
    "doc_type": "cases", 
    "field": "study.center", 
    "full": "study.center", 
    "type": "string"
    }
gql_map['study_contact'] = {
    "description": "The study's primary contact at the sequencing center", 
    "doc_type": "cases", 
    "field": "study.contact", 
    "full": "study.contact", 
    "type": "string"
    }
gql_map['study_description'] = {
    "description": "A longer description of the study", 
    "doc_type": "cases", 
    "field": "study.description", 
    "full": "study.description", 
    "type": "string"
    }
gql_map['study_name'] = {
    "description": "The name of the study", 
    "doc_type": "cases", 
    "field": "study_name", 
    "full": "study.name", 
    "type": "string"
    }
gql_map['study_srp_id'] = {
    "description": "NCBI Sequence Read Archive (SRA) project ID", 
    "doc_type": "cases", 
    "field": "study.srp_id", 
    "full": "study.srp_id", 
    "type": "string"
    }
gql_map['study_subtype'] = {
    "description": "The subtype of the study", 
    "doc_type": "cases", 
    "field": "study.subtype", 
    "full": "study.subtype", 
    "type": "string"
    }

# Subject props
gql_map['subject_gender'] = {
    "description": "The subject's sex", 
    "doc_type": "cases", 
    "field": "subject.gender", 
    "full": "subject.gender", 
    "type": "string"
    }
gql_map['subject_race'] = {
    "description": "The subject's race/ethnicity", 
    "doc_type": "cases", 
    "field": "subject.race", 
    "full": "subject.race", 
    "type": "string"
    }
gql_map['subject_subtype'] = {
    "description": "The subtype of the subject", 
    "doc_type": "cases", 
    "field": "subject.subtype", 
    "full": "subject.subtype", 
    "type": "string"
    }
gql_map['subject_uuid'] = {
    "description": "The subject's UUID", 
    "doc_type": "cases", 
    "field": "subject.uuid", 
    "full": "subject.uuid", 
    "type": "string"
    }
gql_map['subject_id'] = {
    "description": "The subject's per-study ID (can view in individual sample page)", 
    "doc_type": "cases", 
    "field": "subject.id", 
    "full": "subject.id", 
    "type": "string"
    }

# Subject attribute props
gql_map['subject_aerobics'] = {
    "description": "What is patient's baseline aerobic exercise level; type, minutes/week", 
    "doc_type": "cases", 
    "field": "subject.aerobics", 
    "full": "subject.aerobics", 
    "type": "string"
    }
gql_map['subject_alcohol'] = {
    "description": "What is patient's baseline alcohol consumption; type, drinks/week", 
    "doc_type": "cases", 
    "field": "subject.alcohol", 
    "full": "subject.alcohol", 
    "type": "string"
    }
gql_map['subject_allergies'] = {
    "description": "Does patient have allergies?", 
    "doc_type": "cases", 
    "field": "subject.allergies", 
    "full": "subject.allergies",
    "type": "string"
    }
gql_map['subject_asthma'] = {
    "description": "Does patient have asthma? Yes/No, duration", 
    "doc_type": "cases", 
    "field": "subject.asthma", 
    "full": "subject.asthma", 
    "type": "string"
    }
gql_map['subject_cad'] = {
    "description": "Does patient have coronary artery disease/myocardial infarction? Yes/No, duration", 
    "doc_type": "cases", 
    "field": "subject.cad", 
    "full": "subject.cad", 
    "type": "string"
    }
gql_map['subject_chf'] = {
    "description": "Does patient have chronic heart failure? Yes/No, duration", 
    "doc_type": "cases", 
    "field": "subject.chf", 
    "full": "subject.chf", 
    "type": "string"
    }
gql_map['subject_comment'] = {
    "description": "Free-text comment", 
    "doc_type": "cases", 
    "field": "subject.comment", 
    "full": "subject.comment", 
    "type": "string"
    }
gql_map['subject_contact'] = {
    "description": "Does patient agree to be contacted in the future?", 
    "doc_type": "cases", 
    "field": "subject.contact", 
    "full": "subject.contact", 
    "type": "string"
    }
gql_map['subject_diabetes'] = {
    "description": "Does patient have diabetes (including gestational)? Yes/No, duration", 
    "doc_type": "cases", 
    "field": "subject.diabetes", 
    "full": "subject.diabetes", 
    "type": "string"
    }
gql_map['subject_education'] = {
    "description": "Subject's highest level of educatio", 
    "doc_type": "cases", 
    "field": "subject.education", 
    "full": "subject.education", 
    "type": "string"
    }
gql_map['subject_family_history'] = {
    "description": "Family history of hereditary diseases or physiological conditions", 
    "doc_type": "cases", 
    "field": "subject.family_history", 
    "full": "subject.family_history", 
    "type": "string"
    }
gql_map['subject_gallbladder'] = {
    "description": "Does patient have gallbladder disease? Yes/No, duration, clarification", 
    "doc_type": "cases", 
    "field": "subject.gallbladder", 
    "full": "subject.gallbladder", 
    "type": "string"
    }
gql_map['subject_hyperlipidemia'] = {
    "description": "Does patient have hyperlipidemia? Yes/No, duration", 
    "doc_type": "cases", 
    "field": "subject.hyperlipidemia", 
    "full": "subject.hyperlipidemia", 
    "type": "string"
    }
gql_map['subject_hypertension'] = {
    "description": "Does patient have hypertension? Yes/No, duration", 
    "doc_type": "cases", 
    "field": "subject.hypertension", 
    "full": "subject.hypertension", 
    "type": "string"
    }
gql_map['subject_illicit_drug'] = {
    "description": "What is patient's baseline illicit drug history?", 
    "doc_type": "cases", 
    "field": "subject.ilicit_drug", 
    "full": "subject.ilicit_drug", 
    "type": "string"
    }
gql_map['subject_kidney'] = {
    "description": "Does patient have kidney disease? Yes/No, duration", 
    "doc_type": "cases", 
    "field": "subject.kidney", 
    "full": "subject.kidney", 
    "type": "string"
    }
gql_map['subject_liver'] = {
    "description": "Does patient have liver disease? Yes/No, duration, clarification", 
    "doc_type": "cases", 
    "field": "subject.liver", 
    "full": "subject.liver", 
    "type": "string"
    }
gql_map['subject_lmp'] = {
    "description": "When was patient's last menstrual period, if applicable", 
    "doc_type": "cases", 
    "field": "subject.lmp", 
    "full": "subject.lmp", 
    "type": "string"
    }
gql_map['subject_occupation'] = {
    "description": "Subject's occupation", 
    "doc_type": "cases", 
    "field": "subject.occupation", 
    "full": "subject.occupation", 
    "type": "string"
    }
gql_map['subject_osa'] = {
    "description": "Does patient have obstructive sleep apnea? Yes/No, duration", 
    "doc_type": "cases", 
    "field": "subject.osa", 
    "full": "subject.osa", 
    "type": "string"
    }
gql_map['subject_pancreatitis'] = {
    "description": "Does patient have pancreatitis? Yes/No, duration", 
    "doc_type": "cases", 
    "field": "subject.pancreatitis", 
    "full": "subject.pancreatitis", 
    "type": "string"
    }
gql_map['subject_postmenopausal'] = {
    "description": "Is patient postmenopausal? Yes/No, duration", 
    "doc_type": "cases", 
    "field": "subject.postmenopausal", 
    "full": "subject.postmenopausal", 
    "type": "string"
    }
gql_map['subject_pvd'] = {
    "description": "Does patient have peripheral vascular disease? Yes/No, duration", 
    "doc_type": "cases", 
    "field": "subject.pvd", 
    "full": "subject.pvd", 
    "type": "string"
    }
gql_map['subject_rx'] = {
    "description": "List all prescriptions and over the counter medication patient is taking at start of study", 
    "doc_type": "cases", 
    "field": "subject.rx", 
    "full": "subject.rx", 
    "type": "string"
    }
gql_map['subject_survey_id'] = {
    "description": "Center specific survey identifier", 
    "doc_type": "cases", 
    "field": "subject.survey_id", 
    "full": "subject.survey_id", 
    "type": "string"
    }
gql_map['subject_tobacco'] = {
    "description": "What is patient's baseline tobacco use, measured as number of packs per day x years smoked", 
    "doc_type": "cases", 
    "field": "subject.tobacco", 
    "full": "subject.tobacco", 
    "type": "string"
    }

# Visit props
gql_map['visit_date'] = {
    "description": "Date when the visit occurred", 
    "doc_type": "cases", 
    "field": "visit.date", 
    "full": "visit.date", 
    "type": "string"
    }
gql_map['visit_id'] = {
    "description": "The identifier used by the sequence center to uniquely identify the visit", 
    "doc_type": "cases", 
    "field": "visit.id", 
    "full": "visit.id", 
    "type": "long"
    }
gql_map['visit_interval'] = {
    "description": "The amount of time since the last visit (in days)", 
    "doc_type": "cases", 
    "field": "visit.interval", 
    "full": "visit.interval", 
    "type": "integer"
    }
gql_map['visit_number'] = {
    "description": "A sequential number that is assigned as visits occur for a subject", 
    "doc_type": "cases", 
    "field": "visit.number", 
    "full": "visit.number", 
    "type": "integer"
    }
gql_map['visit_subtype'] = {
    "description": "The subtype of the visit", 
    "doc_type": "cases", 
    "field": "visit.subtype", 
    "full": "visit.subtype", 
    "type": "integer"
    }

# Visit attribute props
gql_map['visit_hbi'] = {
    "description": "Was Harvey-Bradshaw index (HBI) completed?", 
    "doc_type": "cases", 
    "field": "visit.hbi", 
    "full": "visit.hbi", 
    "type": "string"
}
gql_map['visit_hbi_total'] = {
    "description": "Harvey-Bradshaw index (HBI) total score.", 
    "doc_type": "cases", 
    "field": "visit.hbi_total", 
    "full": "visit.hbi_total", 
    "type": "integer"
}
gql_map['visit_weight'] = {
    "description": "Subject weight at time of visit, in kg.", 
    "doc_type": "cases", 
    "field": "visit.weight", 
    "full": "visit.weight", 
    "type": "integer"
}
gql_map['visit_weight_diff'] = {
    "description": "Weight gain/loss since last visit.", 
    "doc_type": "cases", 
    "field": "visit.weight_diff", 
    "full": "visit.weight_diff", 
    "type": "string"
}
gql_map['visit_30m_gluc'] = {
    "description": "Glucose level 30 minutes after eating.", 
    "doc_type": "cases", 
    "field": "visit.30m_gluc", 
    "full": "visit.30m_gluc", 
    "type": "integer"
}
gql_map['visit_60m_gluc'] = {
    "description": "Glucose level 60 minutes after eating.", 
    "doc_type": "cases", 
    "field": "visit.60m_gluc", 
    "full": "visit.60m_gluc", 
    "type": "integer"
}
gql_map['visit_age'] = {
    "description": "Patient age at time of visit", 
    "doc_type": "cases", 
    "field": "visit.age", 
    "full": "visit.age", 
    "type": "integer"
}
gql_map['visit_bmi'] = {
    "description": "Subject BMI at time of visit, calculated as kg/m2.", 
    "doc_type": "cases", 
    "field": "visit.bmi", 
    "full": "visit.bmi", 
    "type": "integer"
}
gql_map['visit_height'] = {
    "description": "Subject height at time of visit, in cm.", 
    "doc_type": "cases", 
    "field": "visit.height", 
    "full": "visit.height", 
    "type": "integer"
}
gql_map['visit_fast_gluc'] = {
    "description": "Fasting glucose level.", 
    "doc_type": "cases", 
    "field": "visit.fast_gluc", 
    "full": "visit.fast_gluc", 
    "type": "integer"
}
gql_map['visit_sccai'] = {
    "description": "Was patient SCCAI (simple clinical colitis activity index) performed?", 
    "doc_type": "cases", 
    "field": "visit.sccai", 
    "full": "visit.sccai", 
    "type": "string"
}
gql_map['visit_sccai_total'] = {
    "description": "Patient SCCAI (simple clinical colitis activity index) score.", 
    "doc_type": "cases", 
    "field": "visit.sccai_total", 
    "full": "visit.sccai_total", 
    "type": "integer"
}
gql_map['visit_cheese'] = {
    "description": "Do you eat cheese?", 
    "doc_type": "cases", 
    "field": "visit.cheese", 
    "full": "visit.cheese", 
    "type": "string"
}
gql_map['visit_fruit_count'] = {
    "description": "How many times do you eat fruits and vegetables or pure fruit juice?", 
    "doc_type": "cases", 
    "field": "visit.fruit_count", 
    "full": "visit.fruit_count", 
    "type": "integer"
}
gql_map['visit_meat_red'] = {
    "description": "Do you eat read meat?", 
    "doc_type": "cases", 
    "field": "visit.meat_red", 
    "full": "visit.meat_red", 
    "type": "string"
}
gql_map['visit_fish'] = {
    "description": "Do you eat fish, fish products?", 
    "doc_type": "cases", 
    "field": "visit.fish", 
    "full": "visit.fish", 
    "type": "string"
}
gql_map['visit_fish_oil'] = {
    "description": "Do you eat oil rich fish?", 
    "doc_type": "cases", 
    "field": "visit.fish_oil", 
    "full": "visit.fish_oil", 
    "type": "string"
}
gql_map['visit_juice'] = {
    "description": "Do you drink fruit juice (not squash)?", 
    "doc_type": "cases", 
    "field": "visit.juice", 
    "full": "visit.juice", 
    "type": "string"
}
gql_map['visit_meat_product'] = {
    "description": "Do you eat processed meats?", 
    "doc_type": "cases", 
    "field": "visit.meat_product", 
    "full": "visit.meat_product", 
    "type": "string"
}
gql_map['visit_milk'] = {
    "description": "What kind of milk do you usually use?", 
    "doc_type": "cases", 
    "field": "visit.milk", 
    "full": "visit.milk", 
    "type": "string"
}
gql_map['visit_starch_type'] = {
    "description": "Do you eat potatoes, pasta or rice?", 
    "doc_type": "cases", 
    "field": "visit.starch_type", 
    "full": "visit.starch_type", 
    "type": "string"
}
gql_map['visit_sweets_count'] = {
    "description": "How many times do you eat sweets, chocolates, cakes, scones, sweet pies, pastries or biscuits?", 
    "doc_type": "cases", 
    "field": "visit.sweets_count", 
    "full": "visit.sweets_count", 
    "type": "integer"
}
gql_map['visit_alcohol'] = {
    "description": "Do you drink alcohol?", 
    "doc_type": "cases", 
    "field": "visit.alcohol", 
    "full": "visit.alcohol", 
    "type": "string"
}
gql_map['visit_veg_green'] = {
    "description": "Do you eat cooked green vegetables (fresh or frozen)?", 
    "doc_type": "cases", 
    "field": "visit.veg_green", 
    "full": "visit.veg_green", 
    "type": "string"
}
gql_map['visit_breadrolls'] = {
    "description": "Do you eat slices of bread/rolls?", 
    "doc_type": "cases", 
    "field": "visit.breadrolls", 
    "full": "visit.breadrolls", 
    "type": "string"
}
gql_map['visit_shellfish'] = {
    "description": "Do you eat shellfish?", 
    "doc_type": "cases", 
    "field": "visit.shellfish", 
    "full": "visit.shellfish", 
    "type": "string"
}
gql_map['visit_sugar'] = {
    "description": "Do you usually take sugar (or sugar substitute) in tea or coffee?", 
    "doc_type": "cases", 
    "field": "visit.sugar", 
    "full": "visit.sugar", 
    "type": "string"
}
gql_map['visit_veg'] = {
    "description": "Do you eat vegetables?", 
    "doc_type": "cases", 
    "field": "visit.veg", 
    "full": "visit.veg", 
    "type": "string"
}
gql_map['visit_dairy'] = {
    "description": "Do you eat dairy?", 
    "doc_type": "cases", 
    "field": "visit.dairy", 
    "full": "visit.dairy", 
    "type": "string"
}
gql_map['visit_fish_count'] = {
    "description": "How many times do you eat oil rich fish?", 
    "doc_type": "cases", 
    "field": "visit.fish_count", 
    "full": "visit.fish_count", 
    "type": "integer"
}
gql_map['visit_yogurt'] = {
    "description": "Do you eat yogurt or other foods containing active bacterial cultures?", 
    "doc_type": "cases", 
    "field": "visit.yogurt", 
    "full": "visit.yogurt", 
    "type": "string"
}
gql_map['visit_cereal_type'] = {
    "description": "Which type of breakfast cereal do you normally eat?", 
    "doc_type": "cases", 
    "field": "visit.cereal_type", 
    "full": "visit.cereal_type", 
    "type": "string"
}
gql_map['visit_veg_raw'] = {
    "description": "Do you eat raw vegetables or salad (including tomatoes)?", 
    "doc_type": "cases", 
    "field": "visit.veg_raw", 
    "full": "visit.veg_raw", 
    "type": "string"
}
gql_map['visit_veg_root'] = {
    "description": "Do you eat cooked root vegetables (fresh or frozen)?", 
    "doc_type": "cases", 
    "field": "visit.veg_root", 
    "full": "visit.veg_root", 
    "type": "string"
}
gql_map['visit_starch'] = {
    "description": "Do you eat starch?", 
    "doc_type": "cases", 
    "field": "visit.starch", 
    "full": "visit.starch", 
    "type": "string"
}
gql_map['visit_eggs'] = {
    "description": "Do you eat eggs?", 
    "doc_type": "cases", 
    "field": "visit.eggs", 
    "full": "visit.eggs", 
    "type": "string"
}
gql_map['visit_bread_spread'] = {
    "description": "What do you usually spread on bread?", 
    "doc_type": "cases", 
    "field": "visit.bread_spread", 
    "full": "visit.bread_spread", 
    "type": "string"
}
gql_map['visit_meat_white'] = {
    "description": "Do you eat white meat?", 
    "doc_type": "cases", 
    "field": "visit.meat_white", 
    "full": "visit.meat_white", 
    "type": "string"
}
gql_map['visit_fish_white'] = {
    "description": "Do you eat white fish?", 
    "doc_type": "cases", 
    "field": "visit.fish_white", 
    "full": "visit.fish_white", 
    "type": "string"
}
gql_map['visit_fruit'] = {
    "description": "Do you eat fruit?", 
    "doc_type": "cases", 
    "field": "visit.fruit", 
    "full": "visit.fruit", 
    "type": "string"
}
gql_map['visit_cereal'] = {
    "description": "Do you eat breakfast cereal?", 
    "doc_type": "cases", 
    "field": "visit.cereal", 
    "full": "visit.cereal", 
    "type": "string"
}
gql_map['visit_diet_drinks'] = {
    "description": "Do you drink diet soft drinks, tea or coffee with sugar?", 
    "doc_type": "cases", 
    "field": "visit.diet_drinks", 
    "full": "visit.diet_drinks", 
    "type": "string"
}
gql_map['visit_ice_cream'] = {
    "description": "Do you eat ice cream?", 
    "doc_type": "cases", 
    "field": "visit.ice_cream", 
    "full": "visit.ice_cream", 
    "type": "string"
}
gql_map['visit_bread'] = {
    "description": "What kind of bread do you usually eat?", 
    "doc_type": "cases", 
    "field": "visit.bread", 
    "full": "visit.bread", 
    "type": "string"
}
gql_map['visit_poultry'] = {
    "description": "Do you eat poultry?", 
    "doc_type": "cases", 
    "field": "visit.poultry", 
    "full": "visit.poultry", 
    "type": "string"
}
gql_map['visit_water'] = {
    "description": "Do you drink water?", 
    "doc_type": "cases", 
    "field": "visit.water", 
    "full": "visit.water", 
    "type": "string"
}
gql_map['visit_meat'] = {
    "description": "Do you eat meat?", 
    "doc_type": "cases", 
    "field": "visit.meat", 
    "full": "visit.meat", 
    "type": "string"
}
gql_map['visit_grains'] = {
    "description": "Do you eat whole grains?", 
    "doc_type": "cases", 
    "field": "visit.grains", 
    "full": "visit.grains", 
    "type": "string"
}
gql_map['visit_sweets'] = {
    "description": "Do you eat sweets, chocolates?", 
    "doc_type": "cases", 
    "field": "visit.sweets", 
    "full": "visit.sweets", 
    "type": "string"
}
gql_map['visit_biscuit'] = {
    "description": "Do you eat biscuits (including chocolate biscuits)?", 
    "doc_type": "cases", 
    "field": "visit.biscuit", 
    "full": "visit.biscuit", 
    "type": "string"
}
gql_map['visit_sugar_drinks'] = {
    "description": "Do you drink soft drinks, tea or coffee with sugar?", 
    "doc_type": "cases", 
    "field": "visit.sugar_drinks", 
    "full": "visit.sugar_drinks", 
    "type": "string"
}
gql_map['visit_beans'] = {
    "description": "Do you eat beans or pulses?", 
    "doc_type": "cases", 
    "field": "visit.beans", 
    "full": "visit.beans", 
    "type": "string"
}
gql_map['visit_soda'] = {
    "description": "Do you drink soft drinks/fizzy drinks?", 
    "doc_type": "cases", 
    "field": "visit.soda", 
    "full": "visit.soda", 
    "type": "string"
}
gql_map['visit_chips_crisps'] = {
    "description": "Do you eat chips, crisps, savory snacks?", 
    "doc_type": "cases", 
    "field": "visit.chips_crisps", 
    "full": "visit.chips_crisps", 
    "type": "string"
}
gql_map['visit_salt'] = {
    "description": "At table, how do you use salt?", 
    "doc_type": "cases", 
    "field": "visit.salt", 
    "full": "visit.salt", 
    "type": "string"
}
gql_map['visit_probiotic'] = {
    "description": "Do you take probiotics?", 
    "doc_type": "cases", 
    "field": "visit.probiotic", 
    "full": "visit.probiotic", 
    "type": "string"
}
gql_map['visit_pastry'] = {
    "description": "Do you eat cakes, scones, sweet pies and pastries?", 
    "doc_type": "cases", 
    "field": "visit.pastry", 
    "full": "visit.pastry", 
    "type": "string"
}
gql_map['visit_lunch_food'] = {
    "description": "Please enter the following information for LUNCH you ate: Time of day, Food, Amount (whatever unit easier to you).", 
    "doc_type": "cases", 
    "field": "visit.lunch_food", 
    "full": "visit.lunch_food", 
    "type": "string"
}
gql_map['visit_lunch_amt'] = {
    "description": "Please enter the following information for LUNCH you ate: Time of day, Food, Amount (whatever unit easier to you).", 
    "doc_type": "cases", 
    "field": "visit.lunch_amt", 
    "full": "visit.lunch_amt", 
    "type": "string"
}
gql_map['visit_lunch_tod'] = {
    "description": "Please enter the following information for LUNCH you ate: Time of day, Food, Amount (whatever unit easier to you).", 
    "doc_type": "cases", 
    "field": "visit.lunch_tod", 
    "full": "visit.lunch_tod", 
    "type": "string"
}
gql_map['visit_breakfast_food'] = {
    "description": "Please enter the following information for BREAKFAST you ate: Time of day, Food, Amount (whatever unit easier to you).", 
    "doc_type": "cases", 
    "field": "visit.breakfast_food", 
    "full": "visit.breakfast_food", 
    "type": "string"
}
gql_map['visit_breakfast_amt'] = {
    "description": "Please enter the following information for BREAKFAST you ate: Time of day, Food, Amount (whatever unit easier to you).", 
    "doc_type": "cases", 
    "field": "visit.breakfast_amt", 
    "full": "visit.breakfast_amt", 
    "type": "string"
}
gql_map['visit_breakfast_tod'] = {
    "description": "Please enter the following information for BREAKFAST you ate: Time of day, Food, Amount (whatever unit easier to you).", 
    "doc_type": "cases", 
    "field": "visit.breakfast_tod", 
    "full": "visit.breakfast_tod", 
    "type": "string"
}
gql_map['visit_dinner_food'] = {
    "description": "Please enter the following information for DINNER you ate: Time of day, Food, Amount (whatever unit easier to you).", 
    "doc_type": "cases", 
    "field": "visit.dinner_food", 
    "full": "visit.dinner_food", 
    "type": "string"
}
gql_map['visit_dinner_amt'] = {
    "description": "Please enter the following information for DINNER you ate: Time of day, Food, Amount (whatever unit easier to you).", 
    "doc_type": "cases", 
    "field": "visit.dinner_amt", 
    "full": "visit.dinner_amt", 
    "type": "string"
}
gql_map['visit_dinner_tod'] = {
    "description": "Please enter the following information for DINNER you ate: Time of day, Food, Amount (whatever unit easier to you).", 
    "doc_type": "cases", 
    "field": "visit.dinner_tod", 
    "full": "visit.dinner_tod", 
    "type": "string"
}
gql_map['visit_other_food_intake'] = {
    "description": "Please enter any other information that you want to include about your food consumption on the day.", 
    "doc_type": "cases", 
    "field": "visit.other_food_intake", 
    "full": "visit.other_food_intake", 
    "type": "string"
}
gql_map['visit_snacks_food'] = {
    "description": "Please enter the following information for SNACKS you ate: Time of day, Food, Amount (whatever unit easier to you).", 
    "doc_type": "cases", 
    "field": "visit.snacks_food", 
    "full": "visit.snacks_food", 
    "type": "string"
}
gql_map['visit_snacks_amt'] = {
    "description": "Please enter the following information for SNACKS you ate: Time of day, Food, Amount (whatever unit easier to you).", 
    "doc_type": "cases", 
    "field": "visit.snacks_amt", 
    "full": "visit.snacks_amt", 
    "type": "string"
}
gql_map['visit_snacks_tod'] = {
    "description": "Please enter the following information for SNACKS you ate: Time of day, Food, Amount (whatever unit easier to you).", 
    "doc_type": "cases", 
    "field": "visit.snacks_tod", 
    "full": "visit.snacks_tod", 
    "type": "string"
}
gql_map['visit_study_disease_status'] = {
    "description": "Status of subject health in reference to study disease.", 
    "doc_type": "cases", 
    "field": "visit.study_disease_status", 
    "full": "visit.study_disease_status", 
    "type": "string"
}
gql_map['visit_study_disease_comment'] = {
    "description": "Ontology data associated with iHMP disease classes. Disease nodes describe phenotypic traits of a subject.", 
    "doc_type": "cases", 
    "field": "visit.study_disease_comment", 
    "full": "visit.study_disease_comment", 
    "type": "string"
}
gql_map['visit_study_disease_name'] = {
    "description": "Ontology data associated with iHMP disease classes. Disease nodes describe phenotypic traits of a subject.", 
    "doc_type": "cases", 
    "field": "visit.study_disease_name", 
    "full": "visit.study_disease_name", 
    "type": "string"
}
gql_map['visit_study_disease_disease_ontology_id'] = {
    "description": "Ontology data associated with iHMP disease classes. Disease nodes describe phenotypic traits of a subject.", 
    "doc_type": "cases", 
    "field": "visit.study_disease_disease_ontology_id", 
    "full": "visit.study_disease_disease_ontology_id", 
    "type": "string"
}
gql_map['visit_study_disease_umls_concept_id'] = {
    "description": "Ontology data associated with iHMP disease classes. Disease nodes describe phenotypic traits of a subject.", 
    "doc_type": "cases", 
    "field": "visit.study_disease_umls_concept_id", 
    "full": "visit.study_disease_umls_concept_id", 
    "type": "string"
}
gql_map['visit_study_disease_nci_id'] = {
    "description": "Ontology data associated with iHMP disease classes. Disease nodes describe phenotypic traits of a subject.", 
    "doc_type": "cases", 
    "field": "visit.study_disease_nci_id", 
    "full": "visit.study_disease_nci_id", 
    "type": "string"
}
gql_map['visit_study_disease_mesh_id'] = {
    "description": "Ontology data associated with iHMP disease classes. Disease nodes describe phenotypic traits of a subject.", 
    "doc_type": "cases", 
    "field": "visit.study_disease_mesh_id", 
    "full": "visit.study_disease_mesh_id", 
    "type": "string"
}
gql_map['visit_study_disease_description'] = {
    "description": "Ontology data associated with iHMP disease classes. Disease nodes describe phenotypic traits of a subject.", 
    "doc_type": "cases", 
    "field": "visit.study_disease_description", 
    "full": "visit.study_disease_description", 
    "type": "string"
}
gql_map['visit_walking_hours'] = {
    "description": "During the last 7 days, on how many days did patient walk for at least 10 minutes at a time? This includes walking at work and at home, walking to travel from place to place, and any other walking that done solely for recreation, sport, exercise or leisure.", 
    "doc_type": "cases", 
    "field": "visit.walking_hours", 
    "full": "visit.walking_hours", 
    "type": "integer"
}
gql_map['visit_walking_minutes'] = {
    "description": "During the last 7 days, on how many days did patient walk for at least 10 minutes at a time? This includes walking at work and at home, walking to travel from place to place, and any other walking that done solely for recreation, sport, exercise or leisure.", 
    "doc_type": "cases", 
    "field": "visit.walking_minutes", 
    "full": "visit.walking_minutes", 
    "type": "integer"
}
gql_map['visit_walking_days'] = {
    "description": "During the last 7 days, on how many days did patient walk for at least 10 minutes at a time? This includes walking at work and at home, walking to travel from place to place, and any other walking that done solely for recreation, sport, exercise or leisure.", 
    "doc_type": "cases", 
    "field": "visit.walking_days", 
    "full": "visit.walking_days", 
    "type": "integer"
}
gql_map['visit_activity_change_30d'] = {
    "description": "If activity level has changed over the last 30 days, please specify what is different?", 
    "doc_type": "cases", 
    "field": "visit.activity_change_30d", 
    "full": "visit.activity_change_30d", 
    "type": "string"
}
gql_map['visit_activity_30d'] = {
    "description": "Activity level over the last 30 days?", 
    "doc_type": "cases", 
    "field": "visit.activity_30d", 
    "full": "visit.activity_30d", 
    "type": "string"
}
gql_map['visit_mod_activity_hours'] = {
    "description": "During the last 7 days, on how many days did patient do moderate physical activities like carrying light loads, bicycling at a regular pace, or doubles tennis? Do not include walking.", 
    "doc_type": "cases", 
    "field": "visit.mod_activity_hours", 
    "full": "visit.mod_activity_hours", 
    "type": "integer"
}
gql_map['visit_mod_activity_minutes'] = {
    "description": "During the last 7 days, on how many days did patient do moderate physical activities like carrying light loads, bicycling at a regular pace, or doubles tennis? Do not include walking.", 
    "doc_type": "cases", 
    "field": "visit.mod_activity_minutes", 
    "full": "visit.mod_activity_minutes", 
    "type": "integer"
}
gql_map['visit_mod_activity_days'] = {
    "description": "During the last 7 days, on how many days did patient do moderate physical activities like carrying light loads, bicycling at a regular pace, or doubles tennis? Do not include walking.", 
    "doc_type": "cases", 
    "field": "visit.mod_activity_days", 
    "full": "visit.mod_activity_days", 
    "type": "integer"
}
gql_map['visit_activity_change_3m'] = {
    "description": "If activity level has changed over the last 3 months, please specify what is different?", 
    "doc_type": "cases", 
    "field": "visit.activity_change_3m", 
    "full": "visit.activity_change_3m", 
    "type": "string"
}
gql_map['visit_activity_3m'] = {
    "description": "Activity level over the last 3 months?", 
    "doc_type": "cases", 
    "field": "visit.activity_3m", 
    "full": "visit.activity_3m", 
    "type": "string"
}
gql_map['visit_vig_activity_hours'] = {
    "description": "During the last 7 days, on how many days did patient do vigorous physical activities like heavy lifting, digging, aerobics, or fast bicycling? Think about only those physical activities that done for at least 10 minutes at a time.", 
    "doc_type": "cases", 
    "field": "visit.vig_activity_hours", 
    "full": "visit.vig_activity_hours", 
    "type": "integer"
}
gql_map['visit_vig_activity_minutes'] = {
    "description": "During the last 7 days, on how many days did patient do vigorous physical activities like heavy lifting, digging, aerobics, or fast bicycling? Think about only those physical activities that done for at least 10 minutes at a time.", 
    "doc_type": "cases", 
    "field": "visit.vig_activity_minutes", 
    "full": "visit.vig_activity_minutes", 
    "type": "integer"
}
gql_map['visit_vig_activity_days'] = {
    "description": "During the last 7 days, on how many days did patient do vigorous physical activities like heavy lifting, digging, aerobics, or fast bicycling? Think about only those physical activities that done for at least 10 minutes at a time.", 
    "doc_type": "cases", 
    "field": "visit.vig_activity_days", 
    "full": "visit.vig_activity_days", 
    "type": "integer"
}
gql_map['visit_hosp'] = {
    "description": "In past two weeks, has patient been hospitalized?", 
    "doc_type": "cases", 
    "field": "visit.hosp", 
    "full": "visit.hosp", 
    "type": "string"
}
gql_map['visit_cancer'] = {
    "description": "Has patient been diagnosed with cancer? If YES, provide details (e.g. I had a cold on 01/02/2012 and recovered on 01/07/2012; I received a heart surgery on 02/12/2012).", 
    "doc_type": "cases", 
    "field": "visit.cancer", 
    "full": "visit.cancer", 
    "type": "string"
}
gql_map['visit_stool_soft'] = {
    "description": "Number of liquid or very soft stools in the past 24 hours", 
    "doc_type": "cases", 
    "field": "visit.stool_soft", 
    "full": "visit.stool_soft", 
    "type": "integer"
}
gql_map['visit_surgery'] = {
    "description": "Has patient undergone surgery? If YES, provide details (e.g. I had a cold on 01/02/2012 and recovered on 01/07/2012; I received a heart surgery on 02/12/2012).", 
    "doc_type": "cases", 
    "field": "visit.surgery", 
    "full": "visit.surgery", 
    "type": "string"
}
gql_map['visit_dyspnea'] = {
    "description": "Is patient currently suffering from dyspnea (difficult or labored breathing)?", 
    "doc_type": "cases", 
    "field": "visit.dyspnea", 
    "full": "visit.dyspnea", 
    "type": "string"
}
gql_map['visit_claudication'] = {
    "description": "Is patient currently suffering from claudication (cramping pain in leg)?", 
    "doc_type": "cases", 
    "field": "visit.claudication", 
    "full": "visit.claudication", 
    "type": "string"
}
gql_map['visit_preg_plans'] = {
    "description": "Does patient plan to become pregnant?", 
    "doc_type": "cases", 
    "field": "visit.preg_plans", 
    "full": "visit.preg_plans", 
    "type": "string"
}
gql_map['visit_chronic_dis'] = {
    "description": "Has patient suffered from a chronic disease? If YES, provide details (e.g. I had a cold on 01/02/2012 and recovered on 01/07/2012; I received a heart surgery on 02/12/2012).", 
    "doc_type": "cases", 
    "field": "visit.chronic_dis", 
    "full": "visit.chronic_dis", 
    "type": "string"
}
gql_map['visit_diarrhea'] = {
    "description": "In past two weeks, has patient experienced diarrhea?", 
    "doc_type": "cases", 
    "field": "visit.diarrhea", 
    "full": "visit.diarrhea", 
    "type": "string"
}
gql_map['visit_rash'] = {
    "description": "Is patient currently experiencing a rash?", 
    "doc_type": "cases", 
    "field": "visit.rash", 
    "full": "visit.rash", 
    "type": "string"
}
gql_map['visit_bowel_night'] = {
    "description": "Patient's night time bowel frequency.", 
    "doc_type": "cases", 
    "field": "visit.bowel_night", 
    "full": "visit.bowel_night", 
    "type": "integer"
}
gql_map['visit_self_assess'] = {
    "description": "Does patient feel that they can be described as healthy at this time?", 
    "doc_type": "cases", 
    "field": "visit.self_assess", 
    "full": "visit.self_assess", 
    "type": "string"
}
gql_map['visit_abdominal_pain'] = {
    "description": "Is patient currently suffering from abdominal pain?", 
    "doc_type": "cases", 
    "field": "visit.abdominal_pain", 
    "full": "visit.abdominal_pain", 
    "type": "string"
}
gql_map['visit_leg_edema'] = {
    "description": "Is patient currently suffering from leg edema (swelling)?", 
    "doc_type": "cases", 
    "field": "visit.leg_edema", 
    "full": "visit.leg_edema", 
    "type": "string"
}
gql_map['visit_fever'] = {
    "description": "Has patient suffered from fever? If YES, provide details (e.g. I had a cold on 01/02/2012 and recovered on 01/07/2012; I received a heart surgery on 02/12/2012).", 
    "doc_type": "cases", 
    "field": "visit.fever", 
    "full": "visit.fever", 
    "type": "string"
}
gql_map['visit_cancer_mtc'] = {
    "description": "Has patient been diagnosed with Medullary Thyroid Cancer, or Multiple Endocrine Neoplasia Type 2 (Men2)?", 
    "doc_type": "cases", 
    "field": "visit.cancer_mtc", 
    "full": "visit.cancer_mtc", 
    "type": "string"
}
gql_map['visit_urgency_def'] = {
    "description": "Patient's urgency of defecation", 
    "doc_type": "cases", 
    "field": "visit.urgency_def", 
    "full": "visit.urgency_def", 
    "type": "string"
}
gql_map['visit_diag_other'] = {
    "description": "Has patient been diagnosed with some other disorder? If YES, provide details (e.g. I had a cold on 01/02/2012 and recovered on 01/07/2012; I received a heart surgery on 02/12/2012).", 
    "doc_type": "cases", 
    "field": "visit.diag_other", 
    "full": "visit.diag_other", 
    "type": "string"
}
gql_map['visit_bowel_day'] = {
    "description": "Patient's day time bowel frequency.", 
    "doc_type": "cases", 
    "field": "visit.bowel_day", 
    "full": "visit.bowel_day", 
    "type": "integer"
}
gql_map['visit_self_condition'] = {
    "description": "If patient answered NO to healthy self assessment question, describe the medical conditions they are under now.", 
    "doc_type": "cases", 
    "field": "visit.self_condition", 
    "full": "visit.self_condition", 
    "type": "string"
}
gql_map['visit_weight_change'] = {
    "description": "Has patient suffered from weight gain or loss? If YES, provide details (e.g. I had a cold on 01/02/2012 and recovered on 01/07/2012; I received a heart surgery on 02/12/2012).", 
    "doc_type": "cases", 
    "field": "visit.weight_change", 
    "full": "visit.weight_change", 
    "type": "string"
}
gql_map['visit_acute_dis'] = {
    "description": "Has patient suffered from an acute disease? If YES, provide details (e.g. I had a cold on 01/02/2012 and recovered on 01/07/2012; I received a heart surgery on 02/12/2012).", 
    "doc_type": "cases", 
    "field": "visit.acute_dis", 
    "full": "visit.acute_dis", 
    "type": "string"
}
gql_map['visit_work_missed'] = {
    "description": "If patient has been physically ill, how many days of work were missed?", 
    "doc_type": "cases", 
    "field": "visit.work_missed", 
    "full": "visit.work_missed", 
    "type": "integer"
}
gql_map['visit_pregnant'] = {
    "description": "Is patient currently pregnant?", 
    "doc_type": "cases", 
    "field": "visit.pregnant", 
    "full": "visit.pregnant", 
    "type": "string"
}
gql_map['visit_arthralgia'] = {
    "description": "In the past 24 hours, has patient experienced arthralgia (joint pain)?", 
    "doc_type": "cases", 
    "field": "visit.arthralgia", 
    "full": "visit.arthralgia", 
    "type": "string"
}
gql_map['visit_stool_blood'] = {
    "description": "Does patient currently have blood in their stool.", 
    "doc_type": "cases", 
    "field": "visit.stool_blood", 
    "full": "visit.stool_blood", 
    "type": "string"
}
gql_map['visit_chest_pain'] = {
    "description": "Is patient currently suffering from chest pain?", 
    "doc_type": "cases", 
    "field": "visit.chest_pain", 
    "full": "visit.chest_pain", 
    "type": "string"
}
gql_map['visit_uveitis'] = {
    "description": "In the past 24 hours, has patient experienced uveitis (a form of eye inflammation)?", 
    "doc_type": "cases", 
    "field": "visit.uveitis", 
    "full": "visit.uveitis", 
    "type": "string"
}
gql_map['visit_neurologic'] = {
    "description": "Has a neurological exam been performed?", 
    "doc_type": "cases", 
    "field": "visit.neurologic", 
    "full": "visit.neurologic", 
    "type": "string"
}
gql_map['visit_ery_nodosum'] = {
    "description": "In the past 24 hours, has patient experienced erythema nodosum (a specific type of skin inflammation)?", 
    "doc_type": "cases", 
    "field": "visit.ery_nodosum", 
    "full": "visit.ery_nodosum", 
    "type": "string"
}
gql_map['visit_pyo_gangrenosum'] = {
    "description": "In the past 24 hours, has patient experienced pyoderma gangrenosum related ulcers?", 
    "doc_type": "cases", 
    "field": "visit.pyo_gangrenosum", 
    "full": "visit.pyo_gangrenosum", 
    "type": "string"
}
gql_map['visit_current'] = {
    "description": "Is the patient currently undergoing hormone replacement therapy?", 
    "doc_type": "cases", 
    "field": "visit.current", 
    "full": "visit.current", 
    "type": "string"
}
gql_map['visit_prior'] = {
    "description": "Has the patient had hormone replacement therapy in the past?", 
    "doc_type": "cases", 
    "field": "visit.prior", 
    "full": "visit.prior", 
    "type": "string"
}
gql_map['visit_duration'] = {
    "description": "Total duration of hormone replacement therapy", 
    "doc_type": "cases", 
    "field": "visit.duration", 
    "full": "visit.duration", 
    "type": "string"
}
gql_map['visit_new_meds'] = {
    "description": "Has patient started any new medications since last visit?", 
    "doc_type": "cases", 
    "field": "visit.new_meds", 
    "full": "visit.new_meds", 
    "type": "string"
}
gql_map['visit_abx'] = {
    "description": "In past two weeks, has patient received antibiotics?", 
    "doc_type": "cases", 
    "field": "visit.abx", 
    "full": "visit.abx", 
    "type": "string"
}
gql_map['visit_immunosupp'] = {
    "description": "In past two weeks, has patient received immunosuppressants (e.g. oral corticosteroids)?", 
    "doc_type": "cases", 
    "field": "visit.immunosupp", 
    "full": "visit.immunosupp", 
    "type": "string"
}
gql_map['visit_stopped_meds'] = {
    "description": "Has patient stoped any previous medications since last visit?", 
    "doc_type": "cases", 
    "field": "visit.stopped_meds", 
    "full": "visit.stopped_meds", 
    "type": "string"
}
gql_map['visit_chemo'] = {
    "description": "In past two weeks, has patient undergone chemotherapy?", 
    "doc_type": "cases", 
    "field": "visit.chemo", 
    "full": "visit.chemo", 
    "type": "string"
}
gql_map['visit_control'] = {
    "description": "In the past month, how often has patient felt  unable to control the important things in their life?", 
    "doc_type": "cases", 
    "field": "visit.control", 
    "full": "visit.control", 
    "type": "integer"
}
gql_map['visit_stress'] = {
    "description": "In the past month, how often has patient felt nervous and 'stressed'?", 
    "doc_type": "cases", 
    "field": "visit.stress", 
    "full": "visit.stress", 
    "type": "integer"
}
gql_map['visit_on_top'] = {
    "description": "In the past month, how often has patient felt that they were on top of things?", 
    "doc_type": "cases", 
    "field": "visit.on_top", 
    "full": "visit.on_top", 
    "type": "integer"
}
gql_map['visit_coping'] = {
    "description": "In the past month, how often has patient found that they could not cope with all the things that they had to do?", 
    "doc_type": "cases", 
    "field": "visit.coping", 
    "full": "visit.coping", 
    "type": "integer"
}
gql_map['visit_upset'] = {
    "description": "In the past month, how often has patient been upset because of something that happened unexpectedly?", 
    "doc_type": "cases", 
    "field": "visit.upset", 
    "full": "visit.upset", 
    "type": "integer"
}
gql_map['visit_psychiatric'] = {
    "description": "Has a psychiatric exam been performed?", 
    "doc_type": "cases", 
    "field": "visit.psychiatric", 
    "full": "visit.psychiatric", 
    "type": "string"
}
gql_map['visit_confident'] = {
    "description": "In the past month, how often has patient felt confident about ability to handle personal problems?", 
    "doc_type": "cases", 
    "field": "visit.confident", 
    "full": "visit.confident", 
    "type": "integer"
}
gql_map['visit_difficulties'] = {
    "description": "In the past month, how often has patient felt difficulties were piling up so high that they could not overcome them?", 
    "doc_type": "cases", 
    "field": "visit.difficulties", 
    "full": "visit.difficulties", 
    "type": "integer"
}
gql_map['visit_irritation'] = {
    "description": "In the past month, how often has patient been able to control irritations in their life?", 
    "doc_type": "cases", 
    "field": "visit.irritation", 
    "full": "visit.irritation", 
    "type": "integer"
}
gql_map['visit_anger'] = {
    "description": "In the past month, how often has patient been angered because of things that were outside of their control?", 
    "doc_type": "cases", 
    "field": "visit.anger", 
    "full": "visit.anger", 
    "type": "integer"
}
gql_map['visit_stress_def'] = {
    "description": "In the past month, what types of stress has patient encountered?", 
    "doc_type": "cases", 
    "field": "visit.stress_def", 
    "full": "visit.stress_def", 
    "type": "string"
}
gql_map['visit_going_your_way'] = {
    "description": "In the past month, how often has patient felt that things were going their way?", 
    "doc_type": "cases", 
    "field": "visit.going_your_way", 
    "full": "visit.going_your_way", 
    "type": "integer"
}
gql_map['visit_oral_contrast'] = {
    "description": "In past two weeks, has patient used an oral contrast?", 
    "doc_type": "cases", 
    "field": "visit.oral_contrast", 
    "full": "visit.oral_contrast", 
    "type": "string"
}
gql_map['visit_colonoscopy'] = {
    "description": "In past two weeks, has patient undergone a colonoscopy or other procedure?", 
    "doc_type": "cases", 
    "field": "visit.colonoscopy", 
    "full": "visit.colonoscopy", 
    "type": "string"
}

# Sample props. Note that this contains data within mixs nested JSON of OSDF.
gql_map['sample_id'] = {
    "description": "The iHMP ID of the sample", 
    "doc_type": "cases", 
    "field": "sample.id", 
    "full": "sample.id", 
    "type": "string"
    }
gql_map['sample_biome'] = {
    "description": "Biomes are defined based on factors such as plant structures, leaf types, plant spacing, and other factors like climate", 
    "doc_type": "cases", 
    "field": "sample.biome", 
    "full": "sample.biome", 
    "type": "string"
    }
gql_map['sample_body_product'] = {
    "description": "Substance produced by the body, e.g. stool, mucus, where the sample was obtained from", 
    "doc_type": "cases", 
    "field": "sample.body_product", 
    "full": "sample.body_product", 
    "type": "string"
    }
gql_map['sample_collection_date'] = {
    "description": "The time of sampling, either as an instance (single point in time) or interval", 
    "doc_type": "cases", 
    "field": "sample.collection_date", 
    "full": "sample.collection_date", 
    "type": "string"
    }
gql_map['sample_env_package'] = {
    "description": "Controlled vocabulary of MIGS/MIMS environmental packages", 
    "doc_type": "cases", 
    "field": "sample.env_package", 
    "full": "sample.env_package", 
    "type": "string"
    }
gql_map['sample_feature'] = {
    "description": "Environmental feature level includes geographic environmental features", 
    "doc_type": "cases", 
    "field": "sample.feature", 
    "full": "sample.feature", 
    "type": "string"
    }
gql_map['sample_body_site'] = {
    "description": "Body site from which the sample was obtained using the FMA ontology", 
    "doc_type": "cases", 
    "field": "sample.body_site", 
    "full": "sample.body_site", 
    "type": "string"
    }
gql_map['sample_geo_loc_name'] = {
    "description": "The geographical origin of the sample as defined by the country or sea name followed by specific region name", 
    "doc_type": "cases", 
    "field": "sample.geo_loc_name", 
    "full": "sample.geo_loc_name", 
    "type": "string"
    }
gql_map['sample_lat_lon'] = {
    "description": "Latitude/longitude in WGS 84 coordinates", 
    "doc_type": "cases", 
    "field": "sample.lat_lon", 
    "full": "sample.lat_lon", 
    "type": "string"
    }
gql_map['sample_material'] = {
    "description": "Matter that was displaced by the sample, before the sampling event", 
    "doc_type": "cases", 
    "field": "sample.material", 
    "full": "sample.material", 
    "type": "string"
    }
gql_map['sample_project_name'] = {
    "description": "Name of the project within which the sequencing was organized", 
    "doc_type": "cases", 
    "field": "sample.project_name", 
    "full": "sample.project_name", 
    "type": "string"
    }
gql_map['sample_rel_to_oxygen'] = {
    "description": "Whether the organism is an aerobe or anaerobe", 
    "doc_type": "cases", 
    "field": "sample.rel_to_oxygen", 
    "full": "sample.rel_to_oxygen", 
    "type": "string"
    }
gql_map['sample_samp_collect_device'] = {
    "description": "The method or device employed for collecting the sample", 
    "doc_type": "cases", 
    "field": "sample.samp_collect_device", 
    "full": "sample.samp_collect_device", 
    "type": "string"
    }
gql_map['sample_samp_mat_process'] = {
    "description": "Any processing applied to the sample during or after retrieving the sample from environment", 
    "doc_type": "cases", 
    "field": "sample.mat_process", 
    "full": "sample.mat_process", 
    "type": "string"
    }
gql_map['sample_size'] = {
    "description": "Amount or size of sample (volume, mass or area) that was collected", 
    "doc_type": "cases", 
    "field": "sample.samp_size", 
    "full": "sample.samp_size", 
    "type": "string"
    }
gql_map['sample_subtype'] = {
    "description": "The subtype of the sample", 
    "doc_type": "cases", 
    "field": "sample.subtype", 
    "full": "sample.subtype", 
    "type": "string"
    }
gql_map['sample_supersite'] = {
    "description": "Body supersite from which the sample was obtained", 
    "doc_type": "cases", 
    "field": "sample.supersite", 
    "full": "sample.supersite", 
    "type": "string"
    }
gql_map['sample_fecalcal'] = {
    "description": "FecalCal result, exists if measured for the sample", 
    "doc_type": "cases", 
    "field": "sample.FecalCal", 
    "full": "sample.fecalcal", 
    "type": "integer"
    }

# File props (includes everything below Sample node in OSDF schema)
gql_map['file_id'] = {
    "description": "The iHMP ID of the file", 
    "doc_type": "files", 
    "field": "file.id", 
    "full": "file.id", 
    "type": "string"
    }
gql_map['file_format'] = {
    "description": "The format of the file", 
    "doc_type": "files", 
    "field": "file.format", 
    "full": "file.format", 
    "type": "string"
    }
gql_map['file_type'] = {
    "description": "The node type of the file", 
    "doc_type": "files", 
    "field": "file.type", 
    "full": "file.type", 
    "type": "string"
    }
gql_map['file_annotation_pipeline'] = {
    "description": "The annotation pipeline used to generate the file", 
    "doc_type": "files", 
    "field": "file.annotation_pipeline", 
    "full": "file.annotation_pipeline", 
    "type": "string"
    }
gql_map['file_matrix_type'] = {
    "description": "The type of data used to generate the abundance matrix", 
    "doc_type": "files", 
    "field": "file.matrix_type", 
    "full": "file.matrix_type", 
    "type": "string"
    }

gql_map['tag'] = {
    "description": "Tag word attached to the file", 
    "doc_type": "cases", 
    "field": "tag", 
    "full": "tag.term", 
    "type": "string"
    }
