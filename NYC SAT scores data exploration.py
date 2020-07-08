#!/usr/bin/env python
# coding: utf-8

# In[17]:


import pandas as pd
import numpy as np
files = ["ap_2010.csv", "class_size.csv", "demographics.csv", "graduation.csv", "hs_directory.csv", "math_test_results.csv", "sat_results.csv"]
NYCSchools_data = {}
for f in files:
    d = pd.read_csv("schools/{0}".format(f))
    NYCSchools_data[f.replace(".csv", "")] = d


# In[18]:


for k,v in NYCSchools_data.items():
    print("\n" + k + "\n")
    print(v.head())


# In[19]:


NYCSchools_data["demographics"]["DBN"].head()


# In[20]:


NYCSchools_data["class_size"].head()


# In[21]:


NYCSchools_data["hs_directory"].head()


# In[22]:


NYCSchools_data["class_size"]["DBN"] = NYCSchools_data["class_size"].apply(lambda x: "{0:02d}{1}".format(x["CSD"], x["SCHOOL CODE"]), axis=1)
NYCSchools_data["hs_directory"]["DBN"] = NYCSchools_data["hs_directory"]["dbn"]


# In[23]:


NYCSchools_survey1 = pd.read_csv("schools/survey_all.txt", delimiter="\t", encoding='windows-1252')
NYCSchools_survey2 = pd.read_csv("schools/survey_d75.txt", delimiter="\t", encoding='windows-1252')
NYCSchools_survey1["d75"] = False
NYCSchools_survey2["d75"] = True
NYCSchools_survey = pd.concat([NYCSchools_survey1, NYCSchools_survey2], axis=0)


# In[24]:


NYCSchools_survey.head()


# In[25]:


NYCSchools_survey["DBN"] = NYCSchools_survey["dbn"]
survey_fields = ["DBN", "rr_s", "rr_t", "rr_p", "N_s", "N_t", "N_p", "saf_p_11", "com_p_11", "eng_p_11", "aca_p_11", "saf_t_11", "com_t_11", "eng_t_10", "aca_t_11", "saf_s_11", "com_s_11", "eng_s_11", "aca_s_11", "saf_tot_11", "com_tot_11", "eng_tot_11", "aca_tot_11",]
NYCSchools_survey = NYCSchools_survey.reindex(columns=survey_fields)
NYCSchools_data["survey"] = NYCSchools_survey
NYCSchools_survey.shape


# In[26]:


NYCSchools_data["class_size"].head()


# In[27]:


NYCSchools_data["sat_results"].head()


# In[47]:


NYCSchools_class_size = NYCSchools_data["class_size"]
NYCSchools_class_size.head()

#class_size = class_size[class_size["GRADE"] == '09-12']
#class_size = class_size[class_size["PROGRAM TYPE"] == "GEN ED"]
NYCSchools_class_size = NYCSchools_class_size.groupby("DBN").agg(np.mean)
NYCSchools_class_size.reset_index(inplace=True)
NYCSchools_data["class_size"] = NYCSchools_class_size
NYCSchools_data["class_size"].head()


# In[31]:


NYCSchools_demographics = NYCSchools_data["demographics"]
NYCSchools_demographics = NYCSchools_demographics[NYCSchools_demographics["schoolyear"] == 20112012]
NYCSchools_data["demographics"] = NYCSchools_demographics
#NYCSchools_data["demographics"].head()


# In[32]:


NYCSchools_data["math_test_results"] = NYCSchools_data["math_test_results"][NYCSchools_data["math_test_results"]["Year"] == 2011]
NYCSchools_data["math_test_results"] = NYCSchools_data["math_test_results"][NYCSchools_data["math_test_results"]["Grade"] == '8']


# In[33]:


NYCSchools_data["graduation"] = NYCSchools_data["graduation"][NYCSchools_data["graduation"]["Cohort"] == "2006"]
NYCSchools_data["graduation"] = NYCSchools_data["graduation"][NYCSchools_data["graduation"]["Demographic"] == "Total Cohort"]


# In[34]:


cols = ['SAT Math Avg. Score', 'SAT Critical Reading Avg. Score', 'SAT Writing Avg. Score']
for c in cols:
    NYCSchools_data['sat_results'][c] = NYCSchools_data['sat_results'][c].apply(pd.to_numeric, errors='coerce')


# In[35]:


NYCSchools_data["hs_directory"]['lat'] = NYCSchools_data["hs_directory"]['Location 1'].apply(lambda x: x.split("\n")[-1].replace("(", "").replace(")", "").split(", ")[0])
NYCSchools_data["hs_directory"]['lon'] = NYCSchools_data["hs_directory"]['Location 1'].apply(lambda x: x.split("\n")[-1].replace("(", "").replace(")", "").split(", ")[1])
for c in ['lat', 'lon']:
    NYCSchools_data["hs_directory"][c] = NYCSchools_data["hs_directory"][c].apply(pd.to_numeric, errors='coerce')


# In[36]:


for k,v in NYCSchools_data.items():
    print(k)
    print(v.head())


# In[37]:


flat_data_names = [k for k,v in NYCSchools_data.items()]
flat_data = [NYCSchools_data[k] for k in flat_data_names]
full = flat_data[0]
for i, f in enumerate(flat_data[1:]):
    name = flat_data_names[i+1]
    print(name)
    print(len(f["DBN"]) - len(f["DBN"].unique()))
    join_type = "inner"
    if name in ["sat_results", "ap_2010", "graduation"]:
        join_type = "outer"
    if name not in ["math_test_results"]:
        full = full.merge(f, on="DBN", how=join_type)

full.shape


# In[38]:


cols = ['AP Test Takers ', 'Total Exams Taken', 'Number of Exams with scores 3 4 or 5']

for col in cols:
    full[col] = full[col].apply(pd.to_numeric, errors='coerce')

full[cols] = full[cols].fillna(value=0)


# In[39]:


full["school_dist"] = full["DBN"].apply(lambda x: x[:2])


# In[40]:


full = full.fillna(full.mean())


# In[41]:


#full.corr()['sat_score']


# In[42]:


import folium
from folium import plugins
from folium.plugins import MarkerCluster

schools_map = folium.Map(location=[full['lat'].mean(), full['lon'].mean()], zoom_start=10)
marker_cluster = MarkerCluster().add_to(schools_map)
for name, row in full.iterrows():
    folium.Marker([row["lat"], row["lon"]], popup="{0}: {1}".format(row["DBN"], row["school_name"])).add_to(marker_cluster)
schools_map.save('NYC_schools.html')
schools_map


# In[46]:


schools_heatmap = folium.Map(location=[full['lat'].mean(), full['lon'].mean()], zoom_start=10)
schools_heatmap.add_child(plugins.HeatMap([[row["lat"], row["lon"]] for name, row in full.iterrows()]))
schools_heatmap.save("NYC_heatmap.html")
schools_heatmap


# In[44]:


district_data = full.groupby("school_dist").agg(np.mean)
district_data.reset_index(inplace=True)
district_data["school_dist"] = district_data["school_dist"].apply(lambda x: str(int(x)))


# In[45]:


def show_district_map(col):
    geo_path = '../input/schools/districts.geojson'
    d = district_data
    map = folium.Map(location=[full['lat'].mean(), full['lon'].mean()], zoom_start=10)
    map.geo_json(geo_path=geo_path, data=d, columns=['school_dist', col], key_on='feature.properties.school_dist', fill_color='YlGn', fill_opacity=0.7, line_opacity=0.2)
    map.create_map(path="districts.html")
    return districts


# In[ ]:


get_ipython().run_line_magic('matplotlib', 'inline')

full.plot.scatter(x='total_enrollment', y='sat_score')


# In[ ]:


full[(full["total_enrollment"] < 1000) & (full["sat_score"] < 1000)]["School Name"]


# In[ ]:


full.plot.scatter(x='ell_percent', y='sat_score')


# In[ ]:


full.corr()["sat_score"][["rr_s", "rr_t", "rr_p", "N_s", "N_t", "N_p", "saf_tot_11", "com_tot_11", "aca_tot_11", "eng_tot_11"]].plot.bar()


# In[ ]:


full.corr()["sat_score"][["white_per", "asian_per", "black_per", "hispanic_per"]].plot.bar()


# In[ ]:


full.corr()["sat_score"][["male_per", "female_per"]].plot.bar()


# In[ ]:


full.plot.scatter(x='female_per', y='sat_score')


# In[ ]:


full[(full["female_per"] > 65) & (full["sat_score"] > 1400)]["School Name"]


# In[ ]:


full["ap_avg"] = full["AP Test Takers "] / full["total_enrollment"]

full.plot.scatter(x='ap_avg', y='sat_score')


# In[ ]:


full[(full["ap_avg"] > .3) & (full["sat_score"] > 1700)]["School Name"]

