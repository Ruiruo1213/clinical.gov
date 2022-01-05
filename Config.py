## connection setup
params={'host':"aact-db.ctti-clinicaltrials.org",
        'database':"aact",
        'port':5432,
        'user':"c220274",
        'password':"!@Fernando1"}


query= "select s.nct_id, s.start_date, s.verification_date, s.completion_date, s.study_type, s.brief_title, s.overall_status,\
s.phase, s.enrollment, s.source, c.name country \
from ctgov.studies  s \
left join ctgov.countries  c \
on s.nct_id = c.nct_id \
where s.nct_id ='NCT04424316' "

params_country = {'United States': 'United States',
                  'US only': 'United States',
                  'US and other countries': 'International'}

params_sponsor= {   'Janssen':  'Janssen',
                    'Johnson & Johnson':  'Janssen',
                    'Lilly':  'Eli Lilly and Company',
                    'Pfizer':  'Pfizer',
                    'Merck':  'Merck',
                    'Sanofi':  'Sanofi',
                    'NationalInstitutesofHealth':  'National Institutes of Health (NIH)',
                    'NIH':  'National Institutes of Health (NIH)',
                    'NIAID':  'National Institutes of Health (NIH)',
                    'NHLBI':  'National Institutes of Health (NIH)',
                    'NIDDK':  'National Institutes of Health (NIH)',
                    'NCI':  'National Institutes of Health (NIH)',
                    'NEI':  'National Institutes of Health (NIH)',
                    'NHGRI':  'National Institutes of Health (NIH)',
                    'NIA':  'National Institutes of Health (NIH)',
                    'NIAAA':  'National Institutes of Health (NIH)',
                    'NIAMS':  'National Institutes of Health (NIH)',
                    'NIBIB':  'National Institutes of Health (NIH)',
                    'NIDCD':  'National Institutes of Health (NIH)',
                    'NIDCR':  'National Institutes of Health (NIH)',
                    'NIDA':  'National Institutes of Health (NIH)',
                    'NIEHS':  'National Institutes of Health (NIH)',
                    'NIGMS':  'National Institutes of Health (NIH)',
                    'NIMH':  'National Institutes of Health (NIH)',
                    'NIMHD':  'National Institutes of Health (NIH)',
                    'NINDS':  'National Institutes of Health (NIH)',
                    'NINR':  'National Institutes of Health (NIH)',
                    'NLM':  'National Institutes of Health (NIH)',
                    'NCRR':  'National Institutes of Health (NIH)',
                    'Genentech':  'Genentech',
                    'Roche':  'Genentech',
                    'Gilead':  'Gilead',
                    'AbbVie':  'AbbVie',
                    'Bristol-MyersSquibb':  'BMS',
                    'Bristol-MyersSquibb':  'Bristol-MyersSquibb',
                    'NovoNordisk':  'NovoNordisk',
                    'Amgen':  'Amgen',
                    'Moderna':  'Moderna',
                    'ModernaTX':  'Moderna',
                    'Regeneron':  'Regeneron',
                    'AstraZeneca':  'AstraZeneca',
                    'Glaxo':  'GlaxoSmithKline',
                    'Bayer':  'Bayer',
                    'Biogen':  'Biogen',
                    'Novartis':  'Novartis',
                    'Takeda':  'Takeda',
                    'Teva':  'Teva'
}


category_a = ['Janssen', 'Eli Lilly and Company', 'Pfizer', 'Merck', 'Sanofi', 'National Institutes of Health (NIH)',
                'Genentech', 'Gilead', 'AbbVie', 'Bristol-Myers Squibb', 'Moderna', 'Amgen', 'Regeneron', 'AstraZeneca',
                'GSK', 'Bayer', 'Biogen', 'Novartis', 'Takeda', 'Teva', 'Novo Nordisk']


tier_1 = ['Janssen', 'Eli Lilly and Company', 'Pfizer', 'Merck', 'Sanofi', 'National Institutes of Health (NIH)']
tier_2 = ['Genentech', 'Gilead', 'AbbVie', 'Bristol-Myers Squibb', 'Moderna', 'Amgen']
tier_3 = ['Regeneron', 'AstraZeneca', 'GSK', 'Bayer', 'Biogen']
tier_4 = ['Novartis', 'Takeda', 'Teva', 'Novo Nordisk']
tier_additional =['Boehringer Ingelheim', 'UCB']

# Define sponsor engagement steps
step_1 = ['Janssen', 'Pfizer', 'Merck', 'Sanofi', 'Genentech', 'Regeneron', 'Moderna', 'AstraZeneca']
step_2 = ['National Institutes of Health (NIH)', 'Gilead', 'AbbVie', 'Bristol-Myers Squibb', 'Novo Nordisk', 'Amgen']
step_3 = ['Takeda', 'Teva']


universities =['university', 'college', 'school', 'education', 'research centre', 'research center', 'research institute', 'institute of research',
                  'research and development', 'research foundation', 'clinical research', 'research group', 'research corporation', 'research network',
                  'medical research', 'health research', 'campus', 'consortium']

hospitals = ['hospital', 'hospitals', 'clinic', 'medical centre', 'medical center', 'medical institute', 'national institutes',
             'institute', 'centre', 'center',
               'centres', 'centers', 'cancer center', 'health center', 'health centre',
             'health institute', 'department of health', 'health department', 'medicine',
               'department of health', 'surgery', 'health system', 'healthcare system',
             'healthcare network', 'medical group', 'medical system', 'ospedale']

companies = ['company', 'companies', 'pharma', 'pharmaceutical', 'pharmaceuticals',
             'inc', 'ltd', 'llc', 'limited', 'technology', 'technologies',
               'foundation', 'services', 'corporation', 'corp', 'laboratory',
             'laboratories', 'therapeutics', 'therapeutic', 'bio', 'biopharma']

oncology = ['leukemia', 'myeloma', 'myelofibrosis', 'cancer', 'cancers', 'thrombocytopenia', 'melanoma', 'lymphoma', 'carcinoma', 'tumor', 'tumors', 'sarcoma',
              'myelodysplastic', 'metastasis', 'neoplasm', 'neoplasms', 'non-small-cell', 'non-small', 'non small', 'philadelphia chromosome', 'neuroblastoma',
              'glioblastoma', 'glioma', 'malignant', 'gliosarcoma', 'myeloproliferative ', 'lymphoproliferative ', 'precancerous ', 'AML', 'MF', 'NSCLC', 'HNSCC', 'Ph+ALL',
              'hyperplasia']

hepatology = ['steatohepatitis', 'liver', 'fatty-liver', 'pancreatic', 'sclerosing cholangitis','PSC', 'NASH', 'EPI']

gastroenterology = ['crohn','ulcerative colitis', 'colitis', 'diarrhea', 'bowel', 'proctitis',
                      'clostridium', 'nausea', 'vomiting', 'vomit', 'digestive', 'digestion',
                      'PONV', 'IBD', 'UC', 'CD', 'CDAD', 'intestinal disease','gastrointestinal disease',
                      'intestinal fistula', 'anal fistula', 'abscess', 'fistula']

cardiovascular = ['stroke', 'arteritis', 'artery', 'atrial', 'heart', 'hypertension', 'cardiovascular', 'GCA', 'hypogonadism', 'angina',
                    'dyslipidemia', 'myocardial', 'ischemic', 'cardio', 'cardiac', 'cardiomyopathy', 'hypertrophic', 'hyperlipoproteinemia',
                    'coronary', 'hypercholesterolemia', 'amyloidosis', 'transthyretin', 'CHD', 'TIA', 'ECG', 'TTR']

neurology = ['schizophrenia', 'sclerosis', 'alzheimer', 'parkinson', 'dementia', 'lyme', 'brain', 'cognitive', 'personality', 'psychotic', 'schizoaffective',
               'autism', 'huntington', 'neuromuscular', 'epilepsy', 'dravet', 'lennox-gastaut', 'restless', 'narcolepsy', 'myasthenia',
               'spinal', 'PD', 'SCI', 'ASD', 'MRI']

mental_health = ['depressive', 'depression', 'bipolar', 'anxiety', 'stress', 'insomnia', 'nervous', 'attention deficit', 'hyperactivity',
                   'obsessive-compulsive', 'obsessive compulsive', 'traumatic', 'mental', 'PTSD', 'ADHD', 'OCD']

dermatology = ['dermatitis', 'skin', 'acne', 'alopecia', 'hidradenitis', 'psoriasis', 'urticaria', 'neurodermatitis', 'atopic', 'eczema',
                 'lichen planus', 'pemphigoid', 'lupus', 'SLE', 'HS']

respiratory = ['asthma', 'COVID', 'COVID-19', 'COVID19', 'coronavirus', 'coronavirus19', 'coronavirus-19', 'SARS',
                 'pulmonary', 'bronchitis', 'cough', 'pneumonia', 'COPD', 'respiratory', 'cystic fibrosis',
                 'lung disease', 'lung diseases', 'aspergillosis', 'pneumococcal', 'bronchiectasis', 'CF', 'IPF']

hematology = c('hemophilia', 'haemophilia', 'anemia', 'sickle cell', 'hypereosinophilic', 'thrombolysis', 'thromboembolism', 'blood', 'factor VIII', 'APDS', 'PASLI')

metabolic = c('overweight', 'obesity', 'obese', 'diabetes', 'diabetic', 'growth hormone', 'dyslipidemia', 'metabolic', 'insulin', 'weight')

rheumatology = c('arthritis', 'rheumatoid', 'osteoarthritis', 'spondylitis', 'spondyloarthritis', 'psoriatic', 'JIA')

musculoskeletal = c('palsy', 'dyskinetic', 'fibromyalgia', 'atrophy', 'osteoporosis')

opthalmology = c('retinopathy', 'glaucoma', 'retinopathy', 'macular degeneration', 'maculopathy', 'retinitis', 'myopia', 'cataract', 'dry eye', 'sjogren', 'AMD')

nephrology = c('kidney', 'hyperparathyroidism', 'CKD', 'SHPT')

urology = c('urinary', 'urinary-tract', 'bladder')

infectious = ['HIV', 'AIDS', 'influenza', 'fever', 'flu', 'hepatitis', 'acquired immune deficiency syndrome',
              'human immunodeficiency virus', 'gonorrhea',
                'infection', 'infections', 'malaria', 'ebola', 'tuberculosis', 'bacterial', 'viral', 'virus',
                'clostridium difficile', 'cytomegalovirus', 'papillomavirus', 'CMV', 'meningococcal', 'gram-negative']

allergy = ['allergy', 'allergies', 'allergic']

pain = ['pain', 'migraine', 'opioid', 'dependency', 'abuse', 'poison', 'poisoning']

healthy = ['healthy']

## conditions
condition_map ={'oncology' :  'Oncology',
                'hepatology' :  'Hepatology',
                'gastroenterology' :  'Gastroenterology',
                'cardiovascular' :  'Cardiovascular',
                'neurology' :  'Neurology',
                'mental_health' :  'Mental Health',
                'dermatology' :  'Dermatology',
                'respiratory' :  'Respiratory',
                'hematology' :  'Hematology',
                'metabolic' :  'Metabolic Diseases',
                'rheumatology' :  'Rheumatology',
                'musculoskeletal' :  'Musculoskeletal',
                'opthalmology' :  'Opthalmology',
                'nephrology' :  'Nephrology',
                'urology' :  'Urology',
                'infectious' :  'Infectious Diseases',
                'allergy' :  'Allergy',
                'pain' :  'Pain Management',
                'healthy' :  'Healthy',
}

vaccine_params = ['vaccine','vaccination', 'vaccines']






