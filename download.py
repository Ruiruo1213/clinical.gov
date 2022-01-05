import psycopg2
import pandas as pd
import numpy as np
import Functions
from fuzzywuzzy import process
import read_file
#from Config import params
import Config
# from Config import query


def connect_func(params, query):
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    cur.execute(query)
    tupples = cur.fetchall()
    cur.close()
    # We just need to turn it into a pandas dataframe
    df = pd.DataFrame(tupples)

## process
df= connect_func(params, query)


## US

def select_country(df, params_country):
    df_countries = df[['nct_id', 'country']].drop_duplicates()
    df_countries = df_countries.groupby(['nct_id'])['country'].apply('|'.join).reset_index()
    df_countries['location'] = df_countries['countries'].map(params_country)

    df_ct_us = df.drop(country, axis=1).merge(df_countries, on='nct_id', how='left').drop_duplicates()
    df_ct_us = df[df['location'].isin(['US only', 'US and other countries'])].drop(countries, axis=1).drop_duplicates()
    return df_ct_us

def create_view(df_ct_us):
    sponsor_view = df_ct_us.groupby(sponsor).agg('nct_id':'nunique').reset_index()
    sponsor_view.columns=['sponsor','n_trials']

    condition_view = df_ct_us.groupby(condition).agg('nct_id':'nunique').reset_index()
    condition_view.columns = ['condition', 'n_trials']

    sponsor_condition_view = df_ct_us.groupby(['condition', 'sponsor']).agg('nct_id':'nunique').reset_index()
    sponsor_condition_view.columns = ['condition', 'sponsor', 'n_trials']

    return sponsor_view, condition_view, sponsor_condition_view


 # sponsor list
def create_sponsors(df_ct_us):
    sponsors = df_ct_us['sponsor'].drop_duplicates()
    return sponsors

# Refine the name of sponsors for Category A
def refine_sponsor_name(sponsors, params_sponsor, category_a):
    sponsors['sponsor_polished'] = sponsors['sponsor'].map(params_sponsor)
    sponsors['sponsor_category'] = np.where(sponsors['sponsor_polished'].isin(category_a),'Category A', 'New Partner Opportunities')
    sponsors['sponsor_tier'] = np.where(sponsors['sponsor_polished'].isin(tier_1), 'Tier 1',
                                        (sponsors['sponsor_polished'].isin(tier_2), 'Tier 2',
                                         (sponsors['sponsor_polished'].isin(tier_3), 'Tier 3',
                                          (sponsors['sponsor_polished'].isin(tier_4), 'Tier 4',
                                           (sponsors['sponsor_polished'].isin(tier_additional), 'Additional Tier','No Tier'
                                         )))))

    sponsors['sponsor_engagement_step'] = np.where(sponsors['sponsor_polished'].isin(step_1), 'Step 1',
                                                   (sponsors['sponsor_polished'].isin(step_2), 'Step 2',
                                                    (sponsors['sponsor_polished'].isin(step_3), 'Step 3',
                                                     (sponsors['sponsor_polished'].isin(Category A), 'Other Step','No Step')
                                                    )))
    return sponsors


def create_condition(df_ct_us, condition_map, vaccine_params):
    conditions = df_ct_us['condition'][!df_ct_us['condition'].isna()].drop_duplicates()
    conditions['therapeutic_area'] = conditions['condition'].map(condition_map)
    conditions['vaccine_condition'] = np.where(conditions['condition'].isin(vaccine_params),1,0)
    return conditions

def create_interventions(df_ct_us, vaccine_params):
    interventions_name= df_ct_us['intervention_name'][!df_ct_us['intervention_name'].isna()].drop_duplicates()
    interventions_desc = df_ct_us['intervention_desc'][!df_ct_us['intervention_desc'].isna()].drop_duplicates()
    keywords = df_ct_us['keywords'][!df_ct_us['keyword'].isna()].drop_duplicates()

    interventions_name['vaccine_intervention_name'] = np.where(interventions_name['intervention_name'].isin(vaccine_params), 1, 0)
    interventions_desc['vaccine_intervention_desc'] = np.where(interventions_desc['intervention_desc'].isin(vaccine_params), 1, 0)
    keywords['vaccine_keywords'] = np.where(keywords['keyword'].isin(vaccine_params), 1, 0)

    return interventions_name, interventions_desc, keywords

def create df_ct_us(df_ct_us, conditions,interventions_name, interventions_desc, keywords):
    df_ct_us = df_ct_us.merge(conditions, on='condition', how='left').\
        merge(interventions_name, on='intervention_name', how='left').\
        merge(interventions_desc, on='intervention_desc', how='left').\
        merge(keywords, on='keyword', how='left')

    df_ct_us['vaccine'] = np.where((!is.na(df_ct_us['vaccine_condition']) & (df_ct_us['vaccine_condition'] == 1)) |
                          ((!is.na(df_ct_us['vaccine_intervention_name'])) & (df_ct_us['vaccine_intervention_name'] == 1)) |
                          ((!is.na(df_ct_us['vaccine_intervention_desc'])) & (df_ct_us['vaccine_intervention_desc'] == 1)) |
                          ((!is.na(df_ct_us['vaccine_keyword'])) & (df_ct_us['vaccine_keyword'] == 1)), 1, 0)

    df_ct_us['therapeutic_area'] = np.where(df_ct_us['vaccine'] == 1, 'Vaccine', df_ct_us['therapeutic_area'])
    df_ct_us = df_ct_us.drop(['intervention_type', 'intervention_name', 'intervention_desc', 'keyword'], axis=1).drop_duplicates()
    return df_ct_us

def create_unmatched_conditions(df_ct_us):
    unmatched_conditions = df_ct_us[df_ct_us['therapeutic_area'].isna()]['condition']
    unmatched_conditions['condition_polished '] = unmatched_conditions['condition_polished '].str.replace('[^a-zA-Z]', '')
    unmatched_conditions = unmatched_conditions[unmatched_conditions['condition_polished']!=''].drop_duplicates()
    return  unmatched_conditions

def fuzzy_match(unmatched_conditions, read_file.icd):
    unmatched_conditions =  process.extract(unmatched_conditions, icd)
    unmatched_conditions = unmatched_conditions.merge(icd, left_on ='match', right_on='description').\
                                                merge(icd_2_ta, on='code')
    unmatched_conditions = unmatched_conditions[['condition', 'therapeutic_area']]
    unmatched_conditions.columns = ['condition', 'therapeutic_area_unmatched']
    return unmatched_conditions

def create df_ct_us_1 (df_ct_us,unmatched_conditions, path_data):
    df_ct_us = df_ct_us.merge(unmatched_conditions, on='condition')
    df_ct_us['therapeutic_area'] = np.where(df_ct_us['therapeutic_area'].isna(),
                                            df_ct_us['therapeutic_area_unmatched'],df_ct_us['therapeutic_area'])
    df_ct_us = df_ct_us.drop(['therapeutic_area_unmatched'], axis=1)
    df_ct_us['start_date'] = pd.to_datetime(df_ct_us['start_date'], format= "%m/%d/%Y")
    df_ct_us['verification_date'] = pd.to_datetime(df_ct_us['verification_date'], format= "%m/%d/%Y")
    df_ct_us['completion_date'] = pd.to_datetime(df_ct_us['completion_date'], format= "%m/%d/%Y")

    df_ct_us['start_date_yearmonth'] = df_ct_us['start_date'].str[:7]
    df_ct_us['verification_date_yearmonth'] = df_ct_us['verification_date'].str[:7]
    df_ct_us['completion_date_yearmonth'] = df_ct_us['completion_date'].str[:7]
    df_ct_us['duration_years'] = np.where(!df_ct_us['start_date'].isna(),
                                           (pd.to_datetime('today') - df_ct_us['start_date']).days/365, '')
    ## skip the age

    ## phase
    df_ct_us['phase'] = np.where(df_ct_us['phase']=='N/A','No Phases',df_ct_us['phase'])
    df_ct_us['study_url'] = 'https://clinicaltrials.gov/ct2/show/'+ df_ct_us['nct_id'].str
    df_ct_us['bad_data_quality'] = np.where(!df_ct_us['start_date_yearmonth'].isna() |\
                                             df_ct_us['start_date'].str[:4] > '2030' | \
                                             !df_ct_us['enrollment'].isna(), 1, 0)

    df_ct_us = df_ct_us[['nct_id', 'start_date', 'verification_date', 'completion_date', 'start_date_yearmonth',
                        'verification_date_yearmonth', 'completion_date_yearmonth', 'duration_years',
                        'study_type', 'brief_title', 'overall_status', 'phase', 'enrollment', 'location',
                        'sponsor', 'lead_or_collaborator', 'sponsor_type', 'sponsor_category', 'sponsor_tier',
                        'sponsor_engagement_step', 'gender', 'min_age_years', 'max_age_years', 'age_range',
                         'age_span','healthy_volunteers', 'condition', 'therapeutic_area',
                         'study_url', 'bad_data_quality']].drop_duplicates()

    df_ct_us.to_csv(path_data + 'clinical_trials_full_new.csv')

    df_ct_us_active = df_ct_us[df_ct_us['overall_status'].\
        isin(['Not yet recruiting', 'Recruiting', 'Enrolling by invitation',
        'Active, not recruiting', 'Suspended', 'Unknown status'])]

    df_ct_us_active.to_csv(path_data + 'clinical_trials_active_new.csv')
    return df_ct_us_active

## Hemophilia
def create_hemo(df_us_active):
    df_ct_us_hemophilia = df_ct_us_active[((df_ct_us_active['condition'].str.lower().contains('hemophilia|haemophilia')) or
                                          (df_ct_us_active['brief_title'].str.lower().contains('hemophilia|haemophilia'))) and
                                          (df_ct_us_active['study_type']== 'Interventional') and
                                          (df_ct_us_active['overall_status '].isin(['Not yet recruiting', 'Recruiting'])) and
                                          (~df_ct_us_active['phase'].isin(["No Phases", "", "Not Applicable")) and
                                          (df_ct_us_active['sponsor_type'] == 'Company') and
                                          (df_ct_us_active['lead_or_collaborator'] == 'lead')
                                          ]
    ## start year
    df_ct_us_hemophilia['year_summary'] = np.where(df_ct_us_hemophilia['start_date'].str[:4]<='2013',
                                                   "Before 2014",df_ct_us_hemophilia['start_date'].str[:4] )
    df_ct_us_hemophilia_1 = df_ct_us_hemophilia.groupby(['year_summary']).agg({'nct_id':'nunique', 'n_patients':'sum'}).reset_index()

    df_ct_us_hemophilia_1.to_csv(path_data + "hemophilia_trials_by_year.csv")

    # inhibitors
    df_ct_us_hemophilia['condition'] = np.where(df_ct_us_active['condition'].str.lower().contains('inhibitor'), "with_inhibitor",
                                                   'without_inhibitor')
    df_ct_us_hemophilia_2 = df_ct_us_hemophilia.groupby(['with_inhibitor']).agg(
        {'nct_id': 'nunique', 'n_patients': 'sum'}).reset_index()

# age group
    df_ct_us_hemophilia_3 = df_ct_us_hemophilia.groupby(['nct_id']).agg({'max_age_years': 'max', 'min_age_years': 'min'}).reset_index()
    df_ct_us_hemophilia_3['age_group'] = np.where(df_ct_us_hemophilia_3['max_age_years'] < 18, "Pediatric",
                                                  (df_ct_us_hemophilia_3['min_age_years'] >= 18, 'Adult','Both'))

    df_ct_us_hemophilia = df_ct_us_hemophilia.merge(df_ct_us_hemophilia_3[['nct_id','age_group']], on ='nct_id')

    df_ct_us_hemophilia_4 = df_ct_us_hemophilia.groupby(['age_group']).agg({'nct_id':'nunique'}).reset_index()
    len_nct_id = len(df_ct_us_hemophilia['nct_id'].unique())
    df_ct_us_hemophilia_4['pct'] = df_ct_us_hemophilia_4['nct_id']/len_nct_id
    df_ct_us_hemophilia_4.columns = ['age_group','count','pct']
    df_ct_us_hemophilia_4.to_csv(path_data +'hemophilia_trials.csv')

def create_oncology(df_ct_us_active):
    df_ct_us_oncology = df_ct_us_active[(df_ct_us_active['therapeutic_area'] == 'Oncology') and
                                        (df_ct_us_active['study_type'] == 'Interventional') and
                                        (df_ct_us_active['overall_status'].isin(['Not yet recruiting', 'Recruiting'])) and
                                        (~df_ct_us_active['phase'].isin(["No Phases", '', "Not Applicable"])) and
                                        (df_ct_us_active['sponsor_type'] == 'Company')
                                        ]



    ######## Oncology numbers ########
    oncology_ids = df_ct_us_oncology['nct_id'].drop_duplicates()
    oncology_ids = oncology_ids['nct_id'].str.','.join()
    #words = ["Here", "I", "want", "to", "concatenate", "words", "using", "pipe", "delimeter"]"|".join
    ## disease type
    df_ct_us_oncology['haematologic'] = np.where(df_ct_us_oncology['condition'].str.lower().\
                                                 contains('leukemia|lymphoma|haematolo|hematolo|marrow|hodgkin|myelo|aml'),
                                                 'Liquid Tumors','Solid Tumors')
    # trial level
    df_ct_us_oncology_1 = df_ct_us_oncology.groupby(['nct_id']).\
                          agg({'haematologic':'nunique', 'metastasis':'nunique'}).reset_index()
    df_ct_us_oncology_1['tumor_type'] = np.where(df_ct_us_oncology_1['haematologic']>1, 'Both',df_ct_us_oncology_1['haematologic'])
    df_ct_us_oncology_1['primary_or_metastasis'] = np.where(df_ct_us_oncology_1['metastasis'] > 1, 'Both',
                                                 df_ct_us_oncology_1['metastasis'])

    df_ct_us_oncology = df_ct_us_oncology.merge(df_ct_us_oncology_1[['nct_id','tumor_type', 'primary_or_metastasis']], on = 'nct_id')
    ## age group
    df_ct_us_oncology_2 = df_ct_us_oncology.groupby(['nct_id']). \
        agg({'max_age_years': 'max'}).reset_index()

    df_ct_us_oncology_2['age_group'] = np.where(df_ct_us_oncology['max_age_years']<18,'pediatric','non-pediatric' )
    df_ct_us_oncology = df_ct_us_oncology.merge(df_ct_us_oncology_2[['nct_id', 'age_group']], on = 'nct_id')

    ## recruiting
    df_ct_us_oncology_3 = df_ct_us_oncology.groupby(['nct_id']).agg({'overall_status':'nunique'}).reset_index()
    df_ct_us_oncology_3['trial_level_status'] = np.where(df_ct_us_oncology_3['overall_status']>1,
                                                         'multiple status', df_ct_us_oncology_3['overall_status'])
    df_ct_us_oncology = df_ct_us_oncology.merge(df_ct_us_oncology_3[['nct_id', 'trial_level_status']], on = 'nct_id')
    df_ct_us_oncology['trial_level_status'] = np.where(df_ct_us_oncology['trial_level_status'] == 'multiple status',
                                                      df_ct_us_oncology['trial_level_status'],
                                                      df_ct_us_oncology['overall_status'])

    ## sponsor
    df_ct_us_oncology_4 = df_ct_us_oncology.groupby(['nct_id']).agg({'sponsor_category': 'nunique'}).reset_index()
    df_ct_us_oncology_4['trial_level_sponsor_category'] = np.where(df_ct_us_oncology_4['sponsor_category'] > 1,
                                                         'multiple sponsors', df_ct_us_oncology_4['sponsor_category'])
    df_ct_us_oncology = df_ct_us_oncology.merge(df_ct_us_oncology_4[['nct_id', 'trial_level_sponsor_category']], on = 'nct_id')
    df_ct_us_oncology['trial_level_sponsor_category'] = np.where(df_ct_us_oncology['trial_level_sponsor_category'] == 'multiple sponsors',
                                                      df_ct_us_oncology['trial_level_sponsor_category'],
                                                      df_ct_us_oncology['sponsor_category'])

    ## phase
    df_ct_us_oncology_5 = df_ct_us_oncology.groupby(['nct_id']).agg({'phase': 'nunique'}).reset_index()
    df_ct_us_oncology_5['trial_level_phase'] = np.where(df_ct_us_oncology_5['phase'] > 1,
                                                                   'multiple phases', df_ct_us_oncology_5['phase'])
    df_ct_us_oncology = df_ct_us_oncology.merge(df_ct_us_oncology_5[['nct_id', 'trial_level_phase']], on = 'nct_id')
    df_ct_us_oncology['trial_level_phase'] = np.where(df_ct_us_oncology['trial_level_phase']== 'multiple phases',
                                                      df_ct_us_oncology['trial_level_phase'], df_ct_us_oncology['phase'])


    ## top 5 sponsors
    df_ct_us_oncology_6 = df_ct_us_oncology.groupby(['nct_id']).agg({'sponsor': 'nunique'}).reset_index()
    df_ct_us_oncology_6['trial_level_sponsors'] = np.where(df_ct_us_oncology_6['sponsor'] > 1,
                                                                   'multiple sponsor', df_ct_us_oncology_6['sponsor'])
    df_ct_us_oncology = df_ct_us_oncology.merge(df_ct_us_oncology_6[['nct_id', 'trial_level_sponsors']], on = 'nct_id')
    df_ct_us_oncology['trial_level_sponsors'] = np.where(df_ct_us_oncology['trial_level_sponsors']== 'multiple sponsor',
                                                      df_ct_us_oncology['trial_level_sponsors'], df_ct_us_oncology['sponsor'])

    ## start year
    df_ct_us_oncology['year_summary'] = np.where(df_ct_us_oncology['start_date'].str[:4]<='2013',
                                                 "Before 2014",df_ct_us_oncology['start_date'].str[:4])

    df_ct_us_oncology.groupby(['year_summary']).agg({'nct_id':'nunique', 'enrollment':'sum'}).\
                             reset_index().rename(columns={'nct_id': 'count', 'enrollment': 'n_patients'}).\
                              to_csv("oncology_trials_by_year.csv")

    df_ct_us_oncology[df_ct_us_oncology['condition'] == 'Cancer'].to_csv("./Data/oncology_outlier.csv")

 ### overall summary table (no active and active)
def create_financial(df_ct_us,non_active_list, non_active_saving):

    # non_active_list = ['Not yet recruiting', 'Recruiting']
    ## active_list = ['Not yet recruiting', 'Recruiting', 'Active, not recruiting']

    df_ct_us_overall = df_ct_us[df_ct_us['overall_status'].isin(non_active_list) and
                                (df_ct_us['start_date']>='2021-01-01') ]
    df_ct_us_overall['phase'] =  df_ct_us_overall['phase'].fillna('Unknown')
    df_ct_us_overall = df_ct_us_overall.groupby(['sponsor_category', 'location', 'phase']).\
                            agg({'nct_id':'nunique','enrollment':'sum'}).reset_index().\
                            rename(columns={'nct_id':'n_trials', 'enrollment':'n_patients'})

    df_ct_us_overall_wide_pat =  df_ct_us_overall.drop(columns=['location','n_trials']).\
                                    pivot_table(index='sponsor_category', columns='phase', values='n_patients').\
                                    reset_index().fillna(0)
    df_ct_us_overall_wide_pat['n_pat']= df_ct_us_overall_wide_pat.iloc[:, 3: len(df_ct_us_overall_wide_pat.columns)].sum(axis=1)
    df_ct_us_overall_wide_pat['n_pat_2_3'] = df_ct_us_overall_wide_pat[["Phase 2", "Phase 2/Phase 3", "Phase 3"]].sum(axis=1)
    df_ct_us_overall_wide_pat = df_ct_us_overall_wide_pat[['location', 'sponsor_category', 'n_pat', 'n_pat_2_3']]

    df_ct_us_overall_wide_trial = df_ct_us_overall.drop(columns=['location', 'n_patients']). \
        pivot_table(index='sponsor_category', columns='phase', values='n_trials'). \
        reset_index().fillna(0)
    df_ct_us_overall_wide_trial['n_trial'] = df_ct_us_overall_wide_trial.iloc[:,
                                         3: len(df_ct_us_overall_wide_trial.columns)].sum(axis=1)
    df_ct_us_overall_wide_trial['n_trial_2_3'] = df_ct_us_overall_wide_trial[["Phase 2", "Phase 2/Phase 3", "Phase 3"]].sum(
        axis=1)
    df_ct_us_overall_wide_trial = df_ct_us_overall_wide_trial[['location', 'sponsor_category', 'n_trial', 'n_trial_2_3']]

    df_ct_us_overall_wide =  df_ct_us_overall_wide_trial.merge(df_ct_us_overall_wide_pat, on= ["location", "sponsor_category"])

    #non_active_saving='overall_2022_revenue_noactive'
    #active_saving = 'overall_2022_revenue_withactive
    df_ct_us_overall_wide.to_csv("./Data/"+ non_active_saving+".csv")


def create_recruiting (df_ct_us):
    df_ct_us['start_date_year'] = df_ct_us['start_date'].year.astype('int')
    df_ct_us['verification_date_year'] = df_ct_us['verification_date'].year.astype('int')
    df_ct_us['completion_date_year'] = df_ct_us['completion_date'].year.astype('int')

    df = df_ct_us[(df_ct_us['overall_status'].isin(['Not yet recruiting', 'Recruiting', 'Active, not recruiting']))  and
                  (df_ct_us['location']=='US only')].groupby('start_date_year').agg({'nct_id':'nunique'}).\
                  reset_index().rename(columns={'nct_id':'n'})

    cat_a = df_ct_us[(df_ct_us['overall_status'].isin(['Not yet recruiting', 'Recruiting', 'Active, not recruiting']))  and
                  (df_ct_us['location']=='US only') and (df_ct_us['sponsor_category'] == "Category A")]. \
                  groupby('start_date_year').agg({'nct_id': 'nunique'}). \
                  reset_index().rename(columns={'nct_id': 'n_cat_a'})

    cat_a_2_3 = df_ct_us[
        (df_ct_us['overall_status'].isin(['Not yet recruiting', 'Recruiting', 'Active, not recruiting'])) and
        (df_ct_us['location'] == 'US only') and (df_ct_us['sponsor_category'] == "Category A") and
         df_ct_us['phase'].isin(["Phase 2", "Phase 3", "Phase 2/Phase 3"])]. \
        groupby('start_date_year').agg({'nct_id': 'nunique'}). \
        reset_index().rename(columns={'nct_id': 'n_cat_a_2_3'})

    cat_a_2_3_pat = df_ct_us[
        (df_ct_us['overall_status'].isin(['Not yet recruiting', 'Recruiting', 'Active, not recruiting'])) and
        (df_ct_us['location'] == 'US only') and (df_ct_us['sponsor_category'] == "Category A") and
        df_ct_us['phase'].isin(["Phase 2", "Phase 3", "Phase 2/Phase 3"])]. \
        groupby('start_date_year').agg({'enrollment': 'sum'}). \
        reset_index().rename(columns={'enrollment': 'n_cat_a_2_3_pat'})


    final_df = df.merge(cat_a, on ='start_date_year'). \
                   merge(cat_a_2_3, on='start_date_year'). \
                   merge(cat_a_2_3_pat, on='start_date_year')
    final_df.columns = ["Start year", "Number of trials", "Number of category A trials",
                         "Number of Phase II/III category A trials",
                         "Number of Phase II/III patient enrollment"]
    final_df.to_csv("./num_trials_by_year_recruiting_active_US_only.csv")

    # want universities and complex trials
    df_ct_us[(df_ct_us['overall_status'].isin(['Not yet recruiting', 'Recruiting', 'Active, not recruiting'])) and
        (df_ct_us['start_date'] >= '2021-01-01') and (df_ct_us['phase'].isin(["Phase 2", "Phase 3", "Phase 2/Phase 3"]))]. \
        groupby(['location', 'sponsor_category', 'sponsor_type']).agg({'nct_id': 'nunique'}).\
        reset_index().rename(columns={'nct_id': 'n'}).to_csv("./Data/ntrials_by_sponsor_type_2022_revenue.csv")

    df_ct_us_1 = df_ct_us[(df_ct_us['overall_status'].isin(['Not yet recruiting', 'Recruiting', 'Active, not recruiting'])) and
             (df_ct_us['start_date'] >= '2021-01-01') and (df_ct_us['phase'].isin(["Phase 2", "Phase 3", "Phase 2/Phase 3"]))]

    df_ct_us_1['complex_area_ind'] = np.where(df_ct_us_1['therapeutic_area'],'Neurology',\
                                              np.where(df_ct_us_1['Oncology'],'Oncology','Others'))

    df_ct_us_1.groupby(['location', 'sponsor_category', 'complex_area_ind']).agg({'nct_id': 'nunique'}). \
        reset_index().rename(columns={'nct_id': 'n'}).to_csv("./Data/ntrials_by_therapeutic_area_2022_revenue.csv")

    df_ct_us[(df_ct_us['overall_status'].isin(['Not yet recruiting', 'Recruiting', 'Active, not recruiting'])) and
             (df_ct_us['start_date'] >= '2021-01-01') and (
                 df_ct_us['phase'].isin(["Phase 2", "Phase 3", "Phase 2/Phase 3"]))]. \
        groupby(['location', 'sponsor_category', 'sponsor_type']).agg({'enrollment': 'sum'}). \
        reset_index().rename(columns={'enrollment': 'n'}).to_csv("./Data/npatients_by_sponsor_type_2022_revenue.csv")

    df_ct_us_1.groupby(['location', 'sponsor_category', 'complex_area_ind']).agg({'enrollment': 'sum'}). \
        reset_index().rename(columns={'enrollment': 'n'}).to_csv("./Data/npatients_by_therapeutic_area_2022_revenue.csv")

    # sponsor_trials
    df_ct_by_sponsor = df_ct_us[(df_ct_us['overall_status'].isin(['Not yet recruiting', 'Recruiting', 'Active, not recruiting'])) and
             (df_ct_us['start_date'] >= '2021-01-01') and ( df_ct_us['sponsor_category']== "Category A")]
    df_ct_by_sponsor['phase'] = df_ct_by_sponsor['phase'].fillna('Unknown')

    df_ct_by_sponsor = df_ct_by_sponsor.groupby(['sponsor', 'phase']).agg({'nct_id':'nunique','enrollment': 'sum'}). \
        reset_index().rename(columns={'nct_id': 'n_trials', 'enrollment':'n_patients'})

# sponsor_trials
    df_ct_by_sponsor_patient_wide = df_ct_by_sponsor.pivot(index='sponsor', columns='phase', values='n_patients').\
        reset_index().fillna(0)

    df_ct_by_sponsor_patient_wide['n_pat'] = df_ct_by_sponsor_patient_wide.iloc[:,2: len(df_ct_by_sponsor_patient_wide.columns)].sum(axis=1)
    df_ct_by_sponsor_patient_wide['n_pat_2_3'] = df_ct_by_sponsor_patient_wide[["Phase 2", "Phase 2/Phase 3", "Phase 3"]].sum(
        axis=1)
    df_ct_by_sponsor_patient_wide = df_ct_by_sponsor_patient_wide[['sponsor', 'n_pat', 'n_pat_2_3']]

    df_ct_by_sponsor_trial_wide = df_ct_by_sponsor.pivot(index='sponsor', columns='phase', values='n_trials'). \
        reset_index().fillna(0)
    df_ct_by_sponsor_trial_wide['n_trial'] = df_ct_by_sponsor_trial_wide.iloc[:,
                                             2: len(df_ct_by_sponsor_trial_wide.columns)].sum(axis=1)
    df_ct_by_sponsor_trial_wide['n_trial_2_3'] = df_ct_by_sponsor_trial_wide[
        ["Phase 2", "Phase 2/Phase 3", "Phase 3"]].sum(
        axis=1)
    df_ct_by_sponsor_trial_wide = df_ct_by_sponsor_trial_wide[['sponsor','n_trial', 'n_trial_2_3']]

    df_ct_by_sponsor_wide = df_ct_by_sponsor_trial_wide.merge(df_ct_by_sponsor_patient_wide, on ='sponsor')
    df_ct_by_sponsor_wide.to_csv("./Data/sponsor_trials_2022_revenue.csv")


########NB. The below part is only needed to produce a list of clinical trials to send to doctors for review #

# Isolate conditions and interventions
def condition_intervention(df_ct):
    df_conditions = df_ct[['nct_id', 'condition']].drop_duplicates()
    df_interventions = df_ct[['nct_id', 'intervention_type', 'intervention_name','intervention_desc']].drop_duplicates()
    df_arms = df_ct[['nct_id', 'arm_title', 'arm_desc']].drop_duplicates()
    df_ct = df_ct.drop(columns=['condition', 'intervention_type', 'intervention_name', \
                                'intervention_desc', 'arm_title', 'arm_desc']).drop_duplicates()
    # Merge conditions, interventions and countries into a single row separated by |
    df_conditions = df_conditions.groupby('nct_id')['conditions'].apply(' | '.join).reset_index()
    df_interventions = df_interventions.groupby('nct_id').agg({'intervention_type':' | '.join,
                                                               'intervention_name':' | '.join,
                                                               'intervention_desc':' | '.join  }).\
                            reset_index().\
                            rename(columns = {'intervention_type':'interventions_type',
                                              'intervention_name':'interventions_name',
                                              'intervention_desc':'interventions_desc'
                                              })
    df_arms = df_arms.groupby('nct_id').agg({'arm_title': ' | '.join, 'arm_desc': ' | '.join}).\
        reset_index().\
        rename(columns={'arm_title': 'arms_title',
                        'arm_desc': 'arms_desc'})

    ### added
    df_countries = df_ct[['nct_id', 'country']].drop_duplicates()
    df_countries = df_countries.groupby(['nct_id'])['country'].apply(' | '.join).reset_index()
    df_countries['location'] = np.where(df_countries['countries']=='United States', 'US only',
                               np.where(df_countries['countries'].contains('United States'),'US and other countries', 'International'))

# Join conditions and interventions to the core data and save in xlsx
    df_final = df_ct.merge(df_conditions, on='nct_id', how='left').\
                     merge(df_interventions, on='nct_id', how='left').\
                     merge(df_arms, on='nct_id', how='left').\
                     merge(df_countries, on='nct_id', how='left')

    df_final['inclusion'] = df_final['inclusion'].str.strip()
    df_final['exclusion'] = df_final['exclusion'].str.strip()
    # Create URL to the clincal trial webpage in clinicaltrials.gov
    df_final['study_url']='https://clinicaltrials.gov/ct2/show/'+ df_final['nct_id'].str
# Polish age columns by assigning NA values
    df_final['minimum_age'] = df_final['minimum_age'].replace('N/A','')
    df_final['maximum_age'] = df_final['maximum_age'].replace('N/A', '')

# Retrieve values and label representing the min and max age
    df_final['min_age_value'] = df_final['minimum_age'].str.split(" ").str[0]
    df_final['max_age_value'] = df_final['maximum_age'].str.split(" ").str[0]

    df_final['min_age_years']= np.where(df_final['min_age_value'].contains('Year'), df_final['min_age_value'] ,
                                        np.where(df_final['min_age_value'].contains('Month'), df_final['min_age_value']/12,
                                                 np.where(df_final['min_age_value'].contains('Week'),
                                                          df_final['min_age_value']/52,
                                                          np.where(df_final['min_age_value'].contains('Day'),
                                                                   df_final['min_age_value']/365,''))))

    df_final['max_age_years'] = np.where(df_final['max_age_value'].contains('Year'), df_final['max_age_value'],
                                         np.where(df_final['max_age_value'].contains('Month'),
                                                  df_final['max_age_value'] / 12,
                                                  np.where(df_final['max_age_value'].contains('Week'),
                                                           df_final['max_age_value'] / 52,
                                                           np.where(df_final['max_age_value'].contains('Day'),
                                                                    df_final['max_age_value'] / 365, ''))))
    # Set minimum and maximum age years to 0 and 100
    df_final['min_age_years'] = np.where(df_final['min_age_years'] < 0 or df_final['max_age_years'].isna(), 0,
                                         round(df_final['min_age_years'],3))
    df_final['max_age_years'] = np.where(df_final['max_age_years']>99 or df_final['max_age_years'].isna(),99,
                                         round(df_final['max_age_years'],3))
    # Add age range variable
    df_final['age_range'] = df_final['min_age_years'].str +'-' + df_final['max_age_years'].str +  'Years'

    df_final = df_final[['nct_id', 'brief_title', 'start_date', 'completion_date', 'study_type', 'overall_status', 'phase', 'enrollment',
                       'sponsor', 'gender', 'age_range','healthy_volunteers', 'inclusion', 'exclusion', 'conditions', 'interventions_type',
                        'interventions_name', 'interventions_desc', 'arms_title', 'arms_desc', 'study_url', 'location']].drop_duplicates()

    df_final.to_excel(path_data + 'moderna_trials.xlsx')
    df_final['rte_admin']=  Functions.classify_rte_admin(df_final)
    df_final.to_excel(path_data + 'oncology_rte_admin.xlsx')





