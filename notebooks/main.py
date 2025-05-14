# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.3'
#       jupytext_version: 0.8.6
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# ## Main function has the entire process of 
# - Reading
# - data_cleaning
# - Anonymazing

# ### Library

import sys
sys.path.append('../') # these two lines allow the notebook to find the path to the source code contained in 'src'
import pandas as pd
import io_utils, data_cleaning, data_anonymization
from tests import test_preprocessing, test_anonymization
from src.data.constants import INTERIM_DATA_DIR

# ### Reading dataframe
# Use functions in file **io_utils.py.py**

df = io_utils.reading_dataframe(dir= INTERIM_DATA_DIR, file_name='traces250102_clean.csv')

df[['session.id', 'timestamp.$date', 'time_delta', 'session.duration']]

# ### Print 5 rows and columns of dataframe

io_utils.column_and_head(df)

# +
df['actor'].unique()

# Examples of not matching : 'abaly.oura.etu@univ-lille.fr/' , 'ibrahima.diallo8.etu@/', 'nebut/', 'kilian.graye.etu/luc', 'kade-bhoye.wann.etu/MI1304', 'kade-bhoye.wann.etu/MI1301'
# -

# ### Clean dataframe
# - Change time format
# - Clean actor column

# #### Change time format

df[['session.id', 'timestamp.$date', 'time_delta', 'session.duration']]

df = data_cleaning.clean_time(df)

df[['session.id', 'timestamp.$date', 'time_delta', 'session.duration']]

# #### Clean actor column 

df[['actor', 'binom']] = df['actor'].apply(data_cleaning.clean_actor)

df[['actor', 'binom']] 

# +
# Examples of not matching : 'abaly.oura.etu@univ-lille.fr/' , 'ibrahima.diallo8.etu@/', 'nebut/', 'kilian.graye.etu/luc', 'kade-bhoye.wann.etu/MI1304', 'kade-bhoye.wann.etu/MI1301'
# -

df['actor'].unique()

df['binom'].unique()

not_matching, index_not_matching = test_preprocessing.test_on_actor(df,'actor')

not_matching

index_not_matching

#

### Save dataframe in csv file
io_utils.write_csv(df = df, dir = INTERIM_DATA_DIR)

#

# #### Anonymization
# Create a new dataframe with three columns : 'actor', 'binom' , 'anonymized_actor'

anonymized_df = df[['actor', 'binom']].copy() 
anonymized_df['anonymized_actor'] = df.apply(data_anonymization.anonymize_actor, axis=1)

# Replace column actor and binom by anonymized_actor

df[['actor', 'binom']] = df.apply(data_anonymization.anonymize_actor)

#
