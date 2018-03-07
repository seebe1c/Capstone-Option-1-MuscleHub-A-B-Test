
# coding: utf-8

# In[77]:


# Use a special Codecademy library that lets you type SQL queries directly into this Jupyter notebook.
from codecademySQL import sql_query
import pandas as pd
from matplotlib import pyplot as plt
from scipy.stats import chi2_contingency


# In[34]:


# Examine visits here
sql_query('''
SELECT *
FROM visits
LIMIT 5
''')


# In[38]:


# Examine applications here
sql_query('''
SELECT *
FROM applications
LIMIT 5
''')


# In[37]:


# Examine fitness tests here
sql_query('''
SELECT *
FROM fitness_tests
LIMIT 5
''')


# In[39]:


# Examine purchases here
sql_query('''
SELECT *
FROM purchases
LIMIT 5
''')


# In[66]:


# Combine databases and save to dataframe
df = sql_query('''
SELECT visits.first_name,
       visits.last_name,
       visits.visit_date,
       fitness_tests.fitness_test_date,
       applications.application_date,
       purchases.purchase_date
FROM visits
LEFT JOIN fitness_tests
    ON fitness_tests.first_name = visits.first_name
    AND fitness_tests.last_name = visits.last_name
    AND fitness_tests.email = visits.email
LEFT JOIN applications
    ON applications.first_name = visits.first_name
    AND applications.last_name = visits.last_name
    AND applications.email = visits.email
LEFT JOIN purchases
    ON purchases.first_name = visits.first_name
    AND purchases.last_name = visits.last_name
    AND purchases.email = visits.email
WHERE visits.visit_date >= '7-1-17'
''')
df.head(20)


# In[78]:


# sanity check that Janet split her visitors such that about half are in A and half are in B
df['ab_test_group'] = df.apply(lambda row: 'A' if
                               pd.notnull(row['fitness_test_date'])
                               else 'B', axis=1)

df.head(20)


# In[68]:


# use groupby to sort into A and B in 2 lines
ab_counts = df.groupby('ab_test_group').first_name.count().reset_index()
ab_counts


# In[108]:


# create a pie chart

colors = ['#c2c2f0', '#2d2db9']

plt.pie(ab_counts.first_name.values, labels=['A', 'B'], autopct='%0.2f%%', colors = colors)
plt.axis('equal')
plt.title('Check visitor split')
plt.show()
plt.savefig('ab_test_pie_chart.png')


# In[69]:


# Who picks up an application?
# Recall that the sign-up process for MuscleHub has several steps:

# Take a fitness test with a personal trainer (only Group A)
# Fill out an application for the gym
# Send in their payment for their first month's membership
# Let's examine how many people make it to Step 2, filling out an application.

# Start by creating a new column in df called is_application which is Application if application_date is not None 
# and No Application, otherwise.
df['is_application'] = df.apply(lambda row: 'Application' if
                                pd.notnull(row['application_date'])
                                else 'No Application', axis=1)


# In[70]:


# Now, using groupby, we count how many people from Group A and Group B either do or don't pick up an application. 
# We group by ab_test_group and is_application. Saved this new DataFrame as app_counts
app_counts = df.groupby(['ab_test_group', 'is_application'])               .first_name.count().reset_index()
app_counts.head()


# In[49]:


# We want to calculate the percent of people in each group who complete an application. 
# It's going to be much easier to do this if we pivot app_counts such that:

# The index is ab_test_group
# The columns are is_application. We'll save it to the variable: app_pivot.

app_pivot = app_counts.pivot(columns='is_application',
                            index='ab_test_group',
                            values='first_name')\
            .reset_index()
app_pivot


# In[106]:


# Pie chart for group A who applied 

colors = ['#c2c2f0', '#2d2db9']

plt.pie(app_counts[app_counts.ab_test_group == 'A'].first_name,
        labels=['Application', 'No Application'],
        autopct='%0.2f%%',
        colors = colors)
plt.axis('equal')
plt.savefig('a_test_has_app_pie_chart.png')
plt.title('A Group - With Application')
plt.show()


# In[105]:


# Pie chart for group B who applied 

colors = ['#c2c2f0', '#2d2db9']

plt.pie(app_counts[app_counts.ab_test_group == 'B'].first_name,
        labels=['Application', 'No Application'],
        autopct='%0.2f%%',
        colors = colors)
plt.axis('equal')
plt.savefig('b_test_has_app_pie_chart.png')
plt.title('B Group - With Application')
plt.show()


# In[79]:


# Define a new column called Total, which is the sum of Application and No Application

app_pivot['Total'] = app_pivot.Application + app_pivot['No Application']


# In[80]:


# Calculate another column called Percent with Application, which is equal to Application divided by Total

app_pivot['Percent with Application'] = app_pivot.Application / app_pivot.Total
app_pivot


# In[85]:


# We need to know if this difference, where B group seems higher, is statistically significant.

contingency = [[250, 2254],
                [325, 2175]]
               
chi2, pval, dof, expected = chi2_contingency(contingency)
print (pval)


# In[86]:


# Of those who picked up an application, how many purchased a membership?

df['is_member'] = df.apply(lambda row: 'Member' if 
                           pd.notnull(row['purchase_date'])
                           else 'Not Member', axis=1)
df.head()


# In[59]:


# We group by only those that took out an application

just_apps = df[df.is_application == 'Application']


# In[60]:


# Now we perform the groupby using the same procedure as before

member_count = just_apps.groupby(['ab_test_group', 'is_member'])                 .first_name.count().reset_index()
member_pivot = member_count.pivot(columns='is_member',
                                  index='ab_test_group',
                                  values='first_name')\
                           .reset_index()

member_pivot['Total'] = member_pivot.Member + member_pivot['Not Member']
member_pivot['Percent Purchase'] = member_pivot.Member / member_pivot.Total
member_pivot


# In[104]:


# Pie for A Group - Made Purchase After Application

colors = ['#c2c2f0', '#2d2db9']

plt.pie(member_count[member_count.ab_test_group == 'A'].first_name,
        labels=['Member', 'Not Member'],
        autopct='%0.2f%%',
        colors = colors)
plt.axis('equal')
plt.savefig('a_test_purchases_from_app_pie_chart.png')
plt.title('A Group - Made Purchase After Application')
plt.show()


# In[103]:


# Pie for B Group - Made Purchase After Application

colors = ['#c2c2f0', '#2d2db9']

plt.pie(member_count[member_count.ab_test_group == 'B'].first_name,
        labels=['Member', 'Not Member'],
        autopct='%0.2f%%',
        colors = colors)
plt.axis('equal')
plt.savefig('b_test_purchases_from_app_pie_chart.png')
plt.title('B Group - Made Purchase After Application')
plt.show()


# In[93]:


# It looks like people who took the fitness test were more likely to purchase a membership if they picked 
# up an application. We need to know if this difference is statistically significant.

contingency = [[200, 50],
                [250, 75]]
               
chi2, pval, dof, expected = chi2_contingency(contingency)
print (pval)


# In[62]:


# We have looked at what percent of people who picked up applications purchased memberships. 
# What we really care about is what percentage of all visitors purchased memberships.

final_member_count = df.groupby(['ab_test_group', 'is_member'])                 .first_name.count().reset_index()
final_member_pivot = final_member_count.pivot(columns='is_member',
                                  index='ab_test_group',
                                  values='first_name')\
                           .reset_index()

final_member_pivot['Total'] = final_member_pivot.Member + final_member_pivot['Not Member']
final_member_pivot['Percent Purchase'] = final_member_pivot.Member / final_member_pivot.Total
final_member_pivot


# In[102]:


# Pie for A Group - Made Purchase After Visit

colors = ['#c2c2f0', '#2d2db9']

plt.pie(final_member_count[final_member_count.ab_test_group == 'A'].
        first_name,
        labels=['Member', 'Not Member'],
        autopct='%0.2f%%',
        colors = colors)
plt.axis('equal')
plt.savefig('a_test_purchases_from_visit_pie_chart.png')
plt.title('A Group - Made Purchase After Visit')
plt.show()


# In[101]:


# Pie for B Group - Made Purchase After Visit

colors = ['#c2c2f0', '#2d2db9']

plt.pie(final_member_count[final_member_count.ab_test_group == 'B'].
        first_name,
        labels=['Member', 'Not Member'],
        autopct='%0.2f%%',
        colors = colors)
plt.axis('equal')
plt.savefig('b_test_purchases_from_visit_pie_chart.png')
plt.title('B Group - Made Purchase After Visit')
plt.show()


# In[87]:


# We need to know if this difference is statistically significant.

contingency = [[200, 2304], [250, 2250]]
               
chi2, pval, dof, expected = chi2_contingency(contingency)
print (pval)


# In[30]:


# Percent of visitors who apply
plt.figure(figsize=(10, 4))
ax = plt.subplot()
plt.bar(range(len(app_pivot['Percent with Application'])),
        app_pivot['Percent with Application'], color=['#c2c2f0', '#2d2db9'])
ax.set_xticks(range(len(app_pivot['Percent with Application'])))
ax.set_xticklabels(['Fitness Test', 'No Fitness Test'])
vals = ax.get_yticks()
ax.set_yticklabels(['{:3.0f}%'.format(x*100) for x in vals])
ax.set_ylabel('Percent with Application')
plt.title('Percent of visitors who apply')
plt.show()


# In[31]:


# Percent of applicants who purchase a membership
plt.figure(figsize=(10, 4))
ax = plt.subplot()
plt.bar(range(len(member_pivot['Percent Purchase'])),
        member_pivot['Percent Purchase'], color=['#c2c2f0', '#2d2db9'])
ax.set_xticks(range(len(member_pivot['Percent Purchase'])))
ax.set_xticklabels(['Fitness Test', 'No Fitness Test'])
vals = ax.get_yticks()
ax.set_yticklabels(['{:3.0f}%'.format(x*100) for x in vals])
ax.set_ylabel('Percent who Purchase')
plt.title('Percent of applicants who purchase a membership')
plt.show()


# In[32]:


# Percent of visitors who purchase a membership
plt.figure(figsize=(10, 4))
ax = plt.subplot()
plt.bar(range(len(final_member_pivot['Percent Purchase'])),
        final_member_pivot['Percent Purchase'], color=['#c2c2f0', '#2d2db9'])
ax.set_xticks(range(len(final_member_pivot['Percent Purchase'])))
ax.set_xticklabels(['Fitness Test', 'No Fitness Test'])
vals = ax.get_yticks()
ax.set_yticklabels(['{:3.0f}%'.format(x*100) for x in vals])
ax.set_ylabel('Percent who Purchase')
plt.title('Percent of visitors who purchase a membership')
plt.show()

