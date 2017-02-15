# This module contains all the information needed for populating the 
# auto-complete field. Namely, the description, the doc_type, the
# field, the full name, and the type of data.

gql_map = {}

# Project props
gql_map['project_name'] = {"description": "The name of the project within which the sequencing was organized", "doc_type": "cases", "field": "Project_name", "full": "sample.Project_name", "type": "string"}
gql_map['project_subtype'] = {"description": "The subtype of the project: healthy_human, ihmp, or demo", "doc_type": "cases", "field": "Project_subtype", "full": "sample.Project_subtype", "type": "string"}

# Study props
gql_map['study_center'] = {"description": "The study's sequencing center", "doc_type": "cases", "field": "Study_center", "full": "sample.Study_center", "type": "string"}
gql_map['study_contact'] = {"description": "The study's primary contact at the sequencing center", "doc_type": "cases", "field": "Study_contact", "full": "sample.Study_contact", "type": "string"}
gql_map['study_description'] = {"description": "A longer description of the study", "doc_type": "cases", "field": "Study_description", "full": "sample.Study_description", "type": "string"}
gql_map['study_name'] = {"description": "The name of the study", "doc_type": "cases", "field": "Study_name", "full": "sample.Study_name", "type": "string"}
gql_map['study_srp_id'] = {"description": "NCBI Sequence Read Archive (SRA) project ID", "doc_type": "cases", "field": "Study_srp_id", "full": "sample.Study_srp_id", "type": "string"}
gql_map['study_subtype'] = {"description": "The subtype of the study", "doc_type": "cases", "field": "Study_subtype", "full": "sample.Study_subtype", "type": "string"}

# Subject props
gql_map['subject_gender'] = {"description": "The subject's sex", "doc_type": "cases", "field": "Subject_gender", "full": "sample.Subject_gender", "type": "string"}
gql_map['subject_race'] = {"description": "The subject's race/ethnicity", "doc_type": "cases", "field": "Subject_race", "full": "sample.Subject_race", "type": "string"}
gql_map['subject_subtype'] = {"description": "The subtype of the subject", "doc_type": "cases", "field": "Subject_subtype", "full": "sample.Subject_subtype", "type": "string"}

# Subject attribute props
gql_map['subject_attr_aerobics'] = {"description": "What is patient's baseline aerobic exercise level; type, minutes/week", "doc_type": "cases", "field": "SubjectAttr_aerobics", "full": "sample.SubjectAttr_aerobics", "type": "string"}
gql_map['subject_attr_alcohol'] = {"description": "What is patient's baseline alcohol consumption; type, drinks/week", "doc_type": "cases", "field": "SubjectAttr_alcohol", "full": "sample.SubjectAttr_alcohol", "type": "string"}
gql_map['subject_attr_allergies'] = {"description": "Does patient have allergies?", "doc_type": "cases", "field": "SubjectAttr_allergies", "full": "sample.SubjectAttr_allergies", "type": "string"}
gql_map['subject_attr_asthma'] = {"description": "Does patient have asthma? Yes/No, duration", "doc_type": "cases", "field": "SubjectAttr_asthma", "full": "sample.SubjectAttr_asthma", "type": "string"}
gql_map['subject_attr_cad'] = {"description": "Does patient have coronary artery disease/myocardial infarction? Yes/No, duration", "doc_type": "cases", "field": "SubjectAttr_cad", "full": "sample.SubjectAttr_cad", "type": "string"}
gql_map['subject_attr_chf'] = {"description": "Does patient have chronic heart failure? Yes/No, duration", "doc_type": "cases", "field": "SubjectAttr_chf", "full": "sample.SubjectAttr_chf", "type": "string"}
gql_map['subject_attr_comment'] = {"description": "Free-text comment", "doc_type": "cases", "field": "SubjectAttr_comment", "full": "sample.SubjectAttr_comment", "type": "string"}
gql_map['subject_attr_contact'] = {"description": "Does patient agree to be contacted in the future?", "doc_type": "cases", "field": "SubjectAttr_contact", "full": "sample.SubjectAttr_contact", "type": "string"}
gql_map['subject_attr_diabetes'] = {"description": "Does patient have diabetes (including gestational)? Yes/No, duration", "doc_type": "cases", "field": "SubjectAttr_diabetes", "full": "sample.SubjectAttr_diabetes", "type": "string"}
gql_map['subject_attr_education'] = {"description": "Subject's highest level of educatio", "doc_type": "cases", "field": "SubjectAttr_education", "full": "sample.SubjectAttr_education", "type": "string"}
gql_map['subject_attr_family_history'] = {"description": "Family history of hereditary diseases or physiological conditions", "doc_type": "cases", "field": "SubjectAttr_family_history", "full": "sample.SubjectAttr_family_history", "type": "string"}
gql_map['subject_attr_gallbladder'] = {"description": "Does patient have gallbladder disease? Yes/No, duration, clarification", "doc_type": "cases", "field": "SubjectAttr_gallbladder", "full": "sample.SubjectAttr_gallbladder", "type": "string"}
gql_map['subject_attr_hyperlipidemia'] = {"description": "Does patient have hyperlipidemia? Yes/No, duration", "doc_type": "cases", "field": "SubjectAttr_hyperlipidemia", "full": "sample.SubjectAttr_hyperlipidemia", "type": "string"}
gql_map['subject_attr_hypertension'] = {"description": "Does patient have hypertension? Yes/No, duration", "doc_type": "cases", "field": "SubjectAttr_hypertension", "full": "sample.SubjectAttr_hypertension", "type": "string"}
gql_map['subject_attr_illicit_drug'] = {"description": "What is patient's baseline illicit drug history?", "doc_type": "cases", "field": "SubjectAttr_ilicit_drug", "full": "sample.SubjectAttr_ilicit_drug", "type": "string"}
gql_map['subject_attr_kidney'] = {"description": "Does patient have kidney disease? Yes/No, duration", "doc_type": "cases", "field": "SubjectAttr_kidney", "full": "sample.SubjectAttr_kidney", "type": "string"}
gql_map['subject_attr_liver'] = {"description": "Does patient have liver disease? Yes/No, duration, clarification", "doc_type": "cases", "field": "SubjectAttr_liver", "full": "sample.SubjectAttr_liver", "type": "string"}
gql_map['subject_attr_lmp'] = {"description": "When was patient's last menstrual period, if applicable", "doc_type": "cases", "field": "SubjectAttr_lmp", "full": "sample.SubjectAttr_lmp", "type": "string"}
gql_map['subject_attr_occupation'] = {"description": "Subject's occupation", "doc_type": "cases", "field": "SubjectAttr_occupation", "full": "sample.SubjectAttr_occupation", "type": "string"}
gql_map['subject_attr_osa'] = {"description": "Does patient have obstructive sleep apnea? Yes/No, duration", "doc_type": "cases", "field": "SubjectAttr_osa", "full": "sample.SubjectAttr_osa", "type": "string"}
gql_map['subject_attr_pancreatitis'] = {"description": "Does patient have pancreatitis? Yes/No, duration", "doc_type": "cases", "field": "SubjectAttr_pancreatitis", "full": "sample.SubjectAttr_pancreatitis", "type": "string"}
gql_map['subject_attr_postmenopausal'] = {"description": "Is patient postmenopausal? Yes/No, duration", "doc_type": "cases", "field": "SubjectAttr_postmenopausal", "full": "sample.SubjectAttr_postmenopausal", "type": "string"}
gql_map['subject_attr_pvd'] = {"description": "Does patient have peripheral vascular disease? Yes/No, duration", "doc_type": "cases", "field": "SubjectAttr_pvd", "full": "sample.SubjectAttr_pvd", "type": "string"}
gql_map['subject_attr_rx'] = {"description": "List all prescriptions and over the counter medication patient is taking at start of study", "doc_type": "cases", "field": "SubjectAttr_rx", "full": "sample.SubjectAttr_rx", "type": "string"}
gql_map['subject_attr_subtype'] = {"description": "The subtype of the Visit Attribute", "doc_type": "cases", "field": "SubjectAttr_subtype", "full": "sample.SubjectAttr_subtype", "type": "string"}
gql_map['subject_attr_survey_id'] = {"description": "Center specific survey identifier", "doc_type": "cases", "field": "SubjectAttr_survey_id", "full": "sample.SubjectAttr_survey_id", "type": "string"}
gql_map['subject_attr_tobacco'] = {"description": "What is patient's baseline tobacco use, measured as number of packs per day x years smoked", "doc_type": "cases", "field": "SubjectAttr_tobacco", "full": "sample.SubjectAttr_tobacco", "type": "string"}

# Visit props
gql_map['visit_date'] = {"description": "Date when the visit occurred", "doc_type": "cases", "field": "Visit_date", "full": "sample.Visit_date", "type": "string"}
gql_map['visit_id'] = {"description": "The identifier used by the sequence center to uniquely identify the visit", "doc_type": "cases", "field": "Visit_visit_id", "full": "sample.Visit_visit_id", "type": "long"}
gql_map['visit_interval'] = {"description": "The amount of time since the last visit (in days)", "doc_type": "cases", "field": "Visit_interval", "full": "sample.Visit_interval", "type": "integer"}
gql_map['visit_number'] = {"description": "A sequential number that is assigned as visits occur for that subject", "doc_type": "cases", "field": "Visit_visit_number", "full": "sample.Visit_visit_number", "type": "integer"}
gql_map['visit_subtype'] = {"description": "The subtype of the visit", "doc_type": "cases", "field": "Visit_subtype", "full": "sample.Visit_subtype", "type": "integer"}

# Visit attribute props
gql_map['visit_attr_clinical_patient'] = {"description": "Clinical patient data", "doc_type": "cases", "field": "VisitAttr_clinical_patient", "full": "sample.VisitAttr_clinical_patient", "type": "string"}
gql_map['visit_attr_comment'] = {"description": "Free-text comment", "doc_type": "cases", "field": "VisitAttr_comment", "full": "sample.VisitAttr_comment", "type": "string"}
gql_map['visit_attr_dietary_log'] = {"description": "Dietary log", "doc_type": "cases", "field": "VisitAttr_dietary_log", "full": "sample.VisitAttr_dietary_log", "type": "string"}
gql_map['visit_attr_dietary_log_today'] = {"description": "Dietary log (today)", "doc_type": "cases", "field": "VisitAttr_dietary_log_today", "full": "sample.VisitAttr_dietary_log_today", "type": "string"}
gql_map['visit_attr_disease'] = {"description": "Disease metadata", "doc_type": "cases", "field": "VisitAttr_disease", "full": "sample.VisitAttr_disease", "type": "string"}
gql_map['visit_attr_exercise'] = {"description": "Exercise metadata", "doc_type": "cases", "field": "VisitAttr_exercise", "full": "sample.VisitAttr_exercise", "type": "string"}
gql_map['visit_attr_health_assessment'] = {"description": "Health assessment metadata", "doc_type": "cases", "field": "VisitAttr_health_assessment", "full": "sample.VisitAttr_health_assessment", "type": "string"}
gql_map['visit_attr_hrt'] = {"description": "HRT metadata", "doc_type": "cases", "field": "VisitAttr_hrt", "full": "sample.VisitAttr_hrt", "type": "string"}
gql_map['visit_attr_medications'] = {"description": "Medication metadata", "doc_type": "cases", "field": "VisitAttr_medications", "full": "sample.VisitAttr_medications", "type": "string"}
gql_map['visit_attr_psych'] = {"description": "Psychiatric metadata", "doc_type": "cases", "field": "VisitAttr_psych", "full": "sample.VisitAttr_psych", "type": "string"}
gql_map['visit_attr_subtype'] = {"description": "The subtype of the visit attribute", "doc_type": "cases", "field": "VisitAttr_subtype", "full": "sample.VisitAttr_subtype", "type": "string"}
gql_map['visit_attr_survey_id'] = {"description": "Center specific survey identifier", "doc_type": "cases", "field": "VisitAttr_survey_id", "full": "sample.VisitAttr_survey_id", "type": "string"}
gql_map['visit_attr_tests'] = {"description": "Tests metadata", "doc_type": "cases", "field": "VisitAttr_tests", "full": "sample.VisitAttr_tests", "type": "string"}

# Sample props. Note that this contains data within mixs nested JSON of OSDF.
gql_map['sample_id'] = {"description": "The iHMP ID of the sample", "doc_type": "cases", "field": "Sample_id", "full": "sample.Sample_id", "type": "string"}
gql_map['sample_biome'] = {"description": "Biomes are defined based on factors such as plant structures, leaf types, plant spacing, and other factors like climate", "doc_type": "cases", "field": "Sample_biome", "full": "sample.Sample_biome", "type": "string"}
gql_map['sample_body_product'] = {"description": "Substance produced by the body, e.g. stool, mucus, where the sample was obtained from", "doc_type": "cases", "field": "Sample_body_product", "full": "sample.Sample_body_product", "type": "string"}
gql_map['sample_collection_date'] = {"description": "The time of sampling, either as an instance (single point in time) or interval", "doc_type": "cases", "field": "Sample_collection_date", "full": "sample.Sample_collection_date", "type": "string"}
gql_map['sample_env_package'] = {"description": "Controlled vocabulary of MIGS/MIMS environmental packages", "doc_type": "cases", "field": "Sample_env_package", "full": "sample.Sample_env_package", "type": "string"}
gql_map['sample_feature'] = {"description": "Environmental feature level includes geographic environmental features", "doc_type": "cases", "field": "Sample_feature", "full": "sample.Sample_feature", "type": "string"}
gql_map['sample_fma_body_site'] = {"description": "Body site from which the sample was obtained using the FMA ontology", "doc_type": "cases", "field": "Sample_fma_body_site", "full": "sample.Sample_fma_body_site", "type": "string"}
gql_map['sample_geo_loc_name'] = {"description": "The geographical origin of the sample as defined by the country or sea name followed by specific region name", "doc_type": "cases", "field": "Sample_geo_loc_name", "full": "sample.Sample_geo_loc_name", "type": "string"}
gql_map['sample_lat_lon'] = {"description": "Latitude/longitude in WGS 84 coordinates", "doc_type": "cases", "field": "Sample_lat_lon", "full": "sample.Sample_lat_lon", "type": "string"}
gql_map['sample_material'] = {"description": "Matter that was displaced by the sample, before the sampling event", "doc_type": "cases", "field": "Sample_material", "full": "sample.Sample_material", "type": "string"}
gql_map['sample_project_name'] = {"description": "Name of the project within which the sequencing was organized", "doc_type": "cases", "field": "Sample_project_name", "full": "sample.Sample_project_name", "type": "string"}
gql_map['sample_rel_to_oxygen'] = {"description": "Whether the organism is an aerobe or anaerobe", "doc_type": "cases", "field": "Sample_rel_to_oxygen", "full": "sample.Sample_rel_to_oxygen", "type": "string"}
gql_map['sample_samp_collect_device'] = {"description": "The method or device employed for collecting the sample", "doc_type": "cases", "field": "Sample_samp_collect_device", "full": "sample.Sample_samp_collect_device", "type": "string"}
gql_map['sample_samp_mat_process'] = {"description": "Any processing applied to the sample during or after retrieving the sample from environment", "doc_type": "cases", "field": "Sample_mat_process", "full": "sample.Sample_mat_process", "type": "string"}
gql_map['sample_size'] = {"description": "Amount or size of sample (volume, mass or area) that was collected", "doc_type": "cases", "field": "Sample_samp_size", "full": "sample.Sample_samp_size", "type": "string"}
gql_map['sample_subtype'] = {"description": "The subtype of the sample", "doc_type": "cases", "field": "Sample_subtype", "full": "sample.Sample_subtype", "type": "string"}
gql_map['sample_supersite'] = {"description": "Body supersite from which the sample was obtained", "doc_type": "cases", "field": "Sample_supersite", "full": "sample.Sample_supersite", "type": "string"}

# File props (includes everything below Sample node in OSDF schema)
gql_map['file_id'] = {"description": "The iHMP ID of the file", "doc_type": "cases", "field": "File_id", "full": "file.File_id", "type": "string"}
gql_map['file_format'] = {"description": "The format of the file", "doc_type": "cases", "field": "File_format", "full": "file.File_format", "type": "string"}
gql_map['file_node_type'] = {"description": "The node type of the file", "doc_type": "cases", "field": "File_node_type", "full": "file.File_node_type", "type": "string"}
gql_map['file_annotation_pipeline'] = {"description": "The annotation pipeline used to generate the file", "doc_type": "cases", "field": "File_annotation_pipeline", "full": "sample.File_annotation_pipeline", "type": "string"}
gql_map['file_matrix_type'] = {"description": "The type of matrix format present in the file", "doc_type": "cases", "field": "File_matrix_type", "full": "sample.File_matrix_type", "type": "string"}
# MIMARKS
gql_map['mimarks_adapters'] = {"description": "MIMARKS - Adapters provide priming sequences for both amplification and sequencing of the sample-library fragments", "doc_type": "cases", "field": "File_adapters", "full": "file.File_adapters", "type": "string"}
gql_map['mimarks_biome'] = {"description": "MIMARKS - Biomes are defined based on factors such as plant structures, leaf types, plant spacing, and other factors like climate", "doc_type": "cases", "field": "File_biome", "full": "file.File_biome", "type": "string"}
gql_map['mimarks_collection_date'] = {"description": "MIMARKS - The time of sampling, either as an instance (single point in time) or interval", "doc_type": "cases", "field": "File_collection_date", "full": "file.File_collection_date", "type": "string"}
gql_map['mimarks_env_package'] = {"description": "MIMARKS - Controlled vocabulary of MIMARKS environmental packages", "doc_type": "cases", "field": "File_env_package", "full": "file.File_env_package", "type": "string"}
gql_map['mimarks_experimental_factor'] = {"description": "MIMARKS - The variable aspects of an experiment design which can be used to describe an experiment, or set of experiments, in an increasingly detailed manner", "doc_type": "cases", "field": "File_experimental_factor", "full": "file.File_experimental_factor", "type": "string"}
gql_map['mimarks_feature'] = {"description": "MIMARKS - Environmental feature level includes geographic environmental features", "doc_type": "cases", "field": "File_feature", "full": "file.File_feature", "type": "string"}
gql_map['mimarks_findex'] = {"description": "MIMARKS - Forward strand molecular barcode, called Multiplex Identifier (MID), that is used to specifically tag unique samples in a sequencing run", "doc_type": "cases", "field": "File_findex", "full": "file.File_findex", "type": "string"}
gql_map['mimarks_geo_loc_name'] = {"description": "MIMARKS - The geographical origin of the sample as defined by the country or sea name followed by specific region name", "doc_type": "cases", "field": "File_geo_loc_name", "full": "file.File_geo_loc_name", "type": "string"}
gql_map['mimarks_investigation_type'] = {"description": "MIMARKS - This field is either MIMARKS survey or MIMARKS specimen", "doc_type": "cases", "field": "File_investigation_type", "full": "file.File_investigation_type", "type": "string"}
gql_map['mimarks_isol_growth_condt'] = {"description": "MIMARKS - Publication reference in the form of pubmed ID (pmid), digital object identifier (doi) or url for isolation and growth condition specifications of the organism/material", "doc_type": "cases", "field": "File_isol_growth_condt", "full": "file.File_isol_growth_condt", "type": "string"}
gql_map['mimarks_lat_lon'] = {"description": "MIMARKS - Latitude/longitude in WGS 84 coordinates", "doc_type": "cases", "field": "File_lat_lon", "full": "file.File_lat_lon", "type": "string"}
gql_map['mimarks_lib_const_meth'] = {"description": "MIMARKS - Library construction method used for clone libraries", "doc_type": "cases", "field": "File_lib_const_meth", "full": "file.File_lib_const_meth", "type": "string"}
gql_map['mimarks_lib_reads_seqd'] = {"description": "MIMARKS - Total number of clones sequenced from the library", "doc_type": "cases", "field": "File_lib_reads_seqd", "full": "file.File_lib_reads_seqd", "type": "string"}
gql_map['mimarks_lib_size'] = {"description": "MIMARKS - Total number of clones in the library prepared for the project", "doc_type": "cases", "field": "File_lib_size", "full": "file.File_lib_size", "type": "string"}
gql_map['mimarks_lib_vector'] = {"description": "MIMARKS - Cloning vector type(s) used in construction of libraries", "doc_type": "cases", "field": "File_lib_vector", "full": "file.File_lib_vector", "type": "string"}
gql_map['mimarks_material'] = {"description": "MIMARKS - Matter that was displaced by the sample, before the sampling event", "doc_type": "cases", "field": "File_material", "full": "file.File_material", "type": "string"}
gql_map['mimarks_nucl_acid_amp'] = {"description": "MIMARKS - Link to a literature reference, electronic resource or a standard operating procedure (SOP)", "doc_type": "cases", "field": "File_nucl_acid_amp", "full": "file.File_nucl_acid_amp", "type": "string"}
gql_map['mimarks_nucl_acid_ext'] = {"description": "MIMARKS - Link to a literature reference, electronic resource or a standard operating procedure (SOP)", "doc_type": "cases", "field": "File_nucl_acid_ext", "full": "file.File_nucl_acid_ext", "type": "string"}
gql_map['mimarks_pcr_cond'] = {"description": "MIMARKS - PCR condition used to amplify the sequence of the targeted gene, locus or sub-fragment", "doc_type": "cases", "field": "File_pcr_cond", "full": "file.File_pcr_cond", "type": "string"}
gql_map['mimarks_pcr_primers'] = {"description": "MIMARKS - PCR primers that were used to amplify the sequence of the targeted gene, locus or subfragment", "doc_type": "cases", "field": "File_pcr_primers", "full": "file.File_pcr_primers", "type": "string"}
gql_map['mimarks_project_name'] = {"description": "MIMARKS - Name of the project within which the sequencing was organized", "doc_type": "cases", "field": "File_project_name", "full": "file.File_project_name", "type": "string"}
gql_map['mimarks_rel_to_oxygen'] = {"description": "MIMARKS - Whether the organism is an aerobe or anaerobe", "doc_type": "cases", "field": "File_rel_to_oxygen", "full": "file.File_rel_to_oxygen", "type": "string"}
gql_map['mimarks_rindex'] = {"description": "MIMARKS - Reverse strand molecular barcode, called Multiplex Identifier (MID), that is used to specifically tag unique samples in a sequencing run", "doc_type": "cases", "field": "File_rindex", "full": "file.File_rindex", "type": "string"}
gql_map['mimarks_samp_collect_device'] = {"description": "MIMARKS - The method or device employed for collecting the sample", "doc_type": "cases", "field": "File_samp_collect_device", "full": "file.File_samp_collect_device", "type": "string"}
gql_map['mimarks_samp_mat_process'] = {"description": "MIMARKS - Any processing applied to the sample during or after retrieving the sample from environment", "doc_type": "cases", "field": "File_samp_mat_process", "full": "file.File_samp_mat_process", "type": "string"}
gql_map['mimarks_samp_size'] = {"description": "MIMARKS - Amount or size of sample (volume, mass or area) that was collected", "doc_type": "cases", "field": "File_samp_size", "full": "file.File_samp_size", "type": "string"}
gql_map['mimarks_seq_meth'] = {"description": "MIMARKS - Sequencing method used; e.g. Sanger, pyrosequencing, ABI-solid", "doc_type": "cases", "field": "File_seq_meth", "full": "file.File_seq_meth", "type": "string"}
gql_map['mimarks_submitted_to_insdc'] = {"description": "MIMARKS - Depending on the study (large scale, eg: next generation sequencing technology, or small scale) sequences have to submitted to SRA (Sequence Read Archive), DRA (DDBJ Read Archive) or via the classical WEBIN/Sequin systems to GenBank, ENA, and DDBJ", "doc_type": "cases", "field": "File_submitted_to_insdc", "full": "file.File_submitted_to_insdc", "type": "string"}
gql_map['mimarks_target_gene'] = {"description": "MIMARKS - Targeted gene or locus name for marker gene studies", "doc_type": "cases", "field": "File_target_gene", "full": "file.File_target_gene", "type": "string"}
gql_map['mimarks_target_subfragment'] = {"description": "MIMARKS - Name of subfragment of a gene or locus", "doc_type": "cases", "field": "File_target_subfragment", "full": "file.File_target_subfragment", "type": "string"}
# meta
gql_map['meta_comment'] = {"description": "metadata - Free-text comment", "doc_type": "cases", "field": "File_comment", "full": "file.File_comment", "type": "string"}
gql_map['meta_frag_size'] = {"description": "metadata - Target library fragment size after shearing", "doc_type": "cases", "field": "File_frag_size", "full": "file.File_frag_size", "type": "string"}
gql_map['meta_lib_layout'] = {"description": "metadata - Specification of the layout: fragment/paired, and if paired, then nominal insert size and standard deviation", "doc_type": "cases", "field": "File_lib_layout", "full": "file.File_lib_layout", "type": "string"}
gql_map['meta_lib_selection'] = {"description": "metadata - A controlled vocabulary of terms describing selection or reduction method used in library construction", "doc_type": "cases", "field": "File_lib_selection", "full": "file.File_lib_selection", "type": "string"}
gql_map['meta_ncbi_taxon_id'] = {"description": "metadata - NCBI taxon id", "doc_type": "cases", "field": "File_ncbi_taxon_id", "full": "file.File_ncbi_taxon_id", "type": "string"}
gql_map['meta_prep_id'] = {"description": "metadata - Nucleic Acid Prep ID", "doc_type": "cases", "field": "File_prep_id", "full": "file.File_prep_id", "type": "string"}
gql_map['meta_sequencing_center'] = {"description": "metadata - The center responsible for generating the prep", "doc_type": "cases", "field": "File_sequencing_center", "full": "file.File_sequencing_center", "type": "string"}
gql_map['meta_sequencing_contact'] = {"description": "metadata - Name and email of the primary contact at the sequencing center", "doc_type": "cases", "field": "File_sequencing_contact", "full": "file.File_sequencing_contact", "type": "string"}
gql_map['meta_srs_id'] = {"description": "metadata - NCBI Sequence Read Archive sample ID of the form SRS012345", "doc_type": "cases", "field": "File_srs_id", "full": "file.File_srs_id", "type": "string"}
gql_map['meta_storage_duration'] = {"description": "metadata - Duration for which sample was stored in days", "doc_type": "cases", "field": "File_storage_duration", "full": "file.File_storage_duration", "type": "string"}
gql_map['meta_subtype'] = {"description": "metadata - The subtype of the DNA prep", "doc_type": "cases", "field": "File_subtype", "full": "file.File_subtype", "type": "string"}
