# name

path_date = ''

names = pd.read_csv(path_data + 'names.txt', header = False, names=['name'])
names['name'] = names['name'].str.replace('[^a-zA-Z]', '')
names=names.drop_duplicate()

# Read a dictionary of surnames
surnames = pd.read_csv(path_data + 'surnames.txt', header = False, names = ['surnames'])
surnames['surnames'] = surnames['surnames'].str.replace('[^a-zA-Z]', '')
surnames = surnames.drop_duplicate()

# Load ICD data
icd = pd.read_excel(path_data +'additional_info.xlsx', sheet_name= 3, header=True)
icd_2_ta = pd.read_excel(path_data +'additional_info.xlsx', sheet_name= 4, header=True)

icd = icd[['ICD_code','description_long']].drop_duplicates()
icd.columns= ['code','description']
icd['description'] = icd['description'].str.replace('[^a-zA-Z]', '')
icd = icd.drop_duplicates()
icd = icd.groupby(['description']).agg({'code':'min'}).reset_index()




icd_2_ta =icd_2_ta[['ICD_code','therapeutic_area_renamed']].drop_duplicates()
icd_2_ta.columns = ['code','therapeutic_area']

######## financial planning numbers ########
df_ct_us = pd.read_csv(path_data + 'clinical_trials_active_new.csv')

