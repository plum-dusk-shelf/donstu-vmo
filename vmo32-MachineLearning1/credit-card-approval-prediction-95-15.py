#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Getting dataset

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))


# In[2]:


# Import Required Libraries or methods

# get_ipython().run_line_magic('matplotlib', 'inline')
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split,RandomizedSearchCV,GridSearchCV
from sklearn.metrics import confusion_matrix,RocCurveDisplay,classification_report
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import FunctionTransformer

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression


# In[3]:


# Loading dataset into data

data = pd.read_csv('./Credit_card.csv')
y = pd.read_csv('./Credit_card_label.csv')


# In[4]:


y.head(2)


# In[5]:


# merging both datasets into one

label = y.drop('Ind_ID',axis=1)
data['target'] = label
data.head(3)


# In[6]:




# In[7]:


data.isna().sum()


# In[8]:


print(data.shape)
print(data['GENDER'].unique())
data.GENDER.value_counts()


# In[9]:


# As there is only 7 empty fields of gender, so it's better to drop the rows containg Gender = Nan

data.dropna(subset='GENDER',inplace=True)
print(data.shape)


# In[10]:


print(data['GENDER'].unique())
data.GENDER.value_counts()


# In[11]:


# Creating a new feature 'age' from Birthday_count

age = data['Birthday_count']
print(age.isna().sum())
print(np.mean(age))

age.fillna(np.mean(age),inplace=True)
print(age.isna().sum())

age = np.abs(age/365).round().astype(int)
age


# In[12]:


# Removing Birthday_count

data.drop('Birthday_count',axis=1,inplace=True)


# In[13]:


data.shape


# In[14]:


data['age'] = age
data.shape


# In[15]:


# Absoluting the values (removing minus sign)

# data['Employed_days'] = np.abs(data['Employed_days'])


# In[16]:


data.tail(2)


# In[17]:


data['Type_Occupation'].value_counts(dropna=False)


# In[18]:


print(data.isna().sum())
data.columns


# In[19]:


# creatig X variable

X = data.drop(['Ind_ID','target'],axis=1)
print(X.shape)
X.head(2)


# In[20]:


# creatig y variable

y = data['target']
print(y.shape)
y.head(2)


# In[21]:


# splitting the data into 80:20 with 20 random states
'''
the reason why i chose 20, coz it splits the target (1,0): 
y training ( 12.41% , 87.59% )
y test ( 12.36% , 87.64% )
'''

X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2,random_state=20)
X_train.shape , y_train.shape , X_test.shape , y_test.shape


# In[22]:


# verifying datatypes for numerical values columns

data.dtypes


# In[23]:


# function to map 1 ,0 for yes/no or male/female in transformers

def map_custom(val):
    mapping = {'n': 0, 'f': 0, 'y': 1, 'm': 1}
    return np.vectorize(lambda x: mapping.get(str(x).lower(), x))(val)


# In[24]:


# separating the features according to it's nature for simplicity & pipeline

categorical_features = ['Type_Income','EDUCATION','Marital_status','Housing_type','Type_Occupation']
numeric_features = ['Annual_income','Employed_days','age']
binary_features = ['GENDER','Car_Owner','Propert_Owner']
num_categ_features = ['CHILDREN','Family_Members']
other_features = ['Mobile_phone','Work_Phone','Phone','EMAIL_ID']


# In[25]:


# Transformers for pipeline

numeric_transformer = Pipeline(steps=[
    ('imputer',SimpleImputer(strategy = 'mean'))
])

categorical_transformer = Pipeline(steps=[
    ('imputer',SimpleImputer(strategy='constant',fill_value='missing')),
    ('onehot',OneHotEncoder(handle_unknown='ignore'))
])

binary_transformer = Pipeline(steps=[
    ('imputer',SimpleImputer(strategy='most_frequent')),
    ('mapYNMF',FunctionTransformer(map_custom,validate=False))
])


# In[26]:


# creating pipeline for the model

preprocessor = ColumnTransformer(
    transformers=[
        ('num',numeric_transformer,numeric_features),
        ('cat',categorical_transformer,categorical_features),
        ('bin',binary_transformer,binary_features),
        ('num_cat','passthrough',num_categ_features),
        ('other_cat','passthrough',other_features)
    ]
)


# **RANDOM FOREST CLASSIFIER MODEL****

# In[27]:


# RandomForest Classifier Model

modelRFC = Pipeline(steps=[
    ('preprocessor',preprocessor),
    ('classifier',RandomForestClassifier())
])


# In[28]:


# fitting the Model RFC

modelRFC.fit(X_train,y_train)


# In[29]:


# Check Score of the Model RFC

modelRFC.score(X_test,y_test)


# In[30]:


modelRFC_pred = modelRFC.predict(X_test)
print(y_test[:10])
print(modelRFC.predict_proba(X_test[:10]))
modelRFC_pred[:10]


# In[31]:


fig, ax = plt.subplots()

RocCurveDisplay.from_estimator(
   modelRFC, X_test, y_test, ax = ax)

RocCurveDisplay.from_predictions(y_test,modelRFC_pred,ax=ax,name="RandomForest-Classifer predictions")

plt.show()


# In[32]:


def plot_confusion_matrix(y_test, modelRFC_pred):
    cm = confusion_matrix(y_test, modelRFC_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Pastel2')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.show()


# In[33]:


plot_confusion_matrix(y_test, modelRFC_pred)


# In[34]:


pd.DataFrame(classification_report(y_test, 
                                   modelRFC_pred, 
                                   output_dict=True))


# **LOGISTIC REGRESSION MODEL**

# In[35]:


# Logistic Regression Model

modelLR = Pipeline(steps=[
    ('preprocessor',preprocessor),
    ('classifier',LogisticRegression())
])


# In[36]:


# fitting the Model LR (Logistic Regression)

modelLR.fit(X_train,y_train)


# In[37]:


modelLR.score(X_test,y_test)


# In[38]:


modelLR_pred = modelLR.predict(X_test)

print(y_test[:10])
modelLR_pred[:10]
modelLR.predict_proba(X_test[:5])


# In[39]:


fig, ax = plt.subplots()

RocCurveDisplay.from_estimator(
   modelLR, X_test, y_test, ax = ax)

RocCurveDisplay.from_predictions(y_test,modelLR_pred,ax=ax,name="Logistic Regression predictions")

plt.show()


# In[40]:


plot_confusion_matrix(y_test, modelLR_pred)


# In[41]:


pd.DataFrame(classification_report(y_test, 
                                   modelLR_pred, 
                                   output_dict=True))


# **RANDOMFOREST MODEL WAS BETTER WITH 94% ACCURACY, LET'S TRY TO IMPROVE THE MODEL BY HYPERPARAMTERS TUNING**

# In[42]:


filled_X = preprocessor.fit_transform(X)


# In[43]:


A_train,A_test,b_train,b_test = train_test_split(filled_X,y,test_size=0.2,random_state=20)


# *using Randomized Search CV*

# In[44]:


rs_param_grid = {"n_estimators": [10, 100, 200, 500, 1000, 1200],
                       "max_depth": [None, 5, 10, 20, 30],
                       "max_features": ["sqrt", "log2", None],
                       "min_samples_split": [2, 4, 6, 8],
                       "min_samples_leaf": [1, 2, 4, 8]}


# In[45]:


np.random.seed(5)

rs_modelRFC = RandomizedSearchCV(
    estimator = RandomForestClassifier(),
    param_distributions = rs_param_grid,
    n_iter = 10,
    cv = 5,
    verbose = 2
)  

rs_modelRFC.fit(A_train,b_train)


# In[46]:


rs_modelRFC.best_params_


# In[47]:


rs_modelRFC.score(A_test,b_test)


# In[48]:


plot_confusion_matrix(b_test,rs_modelRFC.predict(A_test))


# In[49]:


pd.DataFrame(classification_report(b_test, 
                                   rs_modelRFC.predict(A_test), 
                                   output_dict=True))


# *Using Grid Search CV*

# In[50]:


gs_param_grid = {'n_estimators': [1000,500],
 'min_samples_split': [2,4,6],
 'min_samples_leaf': [1],
 'max_features': [None],
 'max_depth': [20,30]}


# In[51]:


np.random.seed(42)

gs_modelRFC = GridSearchCV(
    estimator = RandomForestClassifier(),
    param_grid = gs_param_grid,
    cv = 5,
    verbose = 2
) 
gs_modelRFC.fit(A_train,b_train)


# In[52]:


gs_modelRFC.best_params_


# In[53]:


gs_modelRFC.score(A_test,b_test)


# In[54]:


plot_confusion_matrix(b_test,gs_modelRFC.predict(A_test))


# In[55]:


pd.DataFrame(classification_report(b_test, 
                                   gs_modelRFC.predict(A_test), 
                                   output_dict=True))

