# What is this project about
Analyze L1 (first-year) students learning Python using the Thonny editor (with a custom plugin tracking their actions).

- Data: Traces (xAPI format) capture programming behaviors (e.g., running tests, editing code, console interactions) and metadata (timestamps, student pairs, session IDs).

- Verbe : The name of each trace (we put a label for each action of trace, so it is easier to classify them)

## Focus:

- Understand how students use tools like L1test (unit testing plugin).

- Compare beginners vs. students with prior Python experience (e.g., from high school NSI courses).

- Correlate testing practices with code quality/academic results.

- Define behavioral profiles (e.g., "novice" vs. "experienced") and track their evolution.

- Methods: Use pandas for analysis, create visualizations (e.g., timelines of actions), and derive metrics to improve teaching.

# How does it work
# What are the mistakes
# what are the parts that need to imrpove

# my questions
- Should I write my code in script with the format .py or .ipynb
- Why can't we write the codes in .ipynb ? if you know
- the main data that we work, is in the file named tp? we want to analyze the data of each TP, am I right?
- should I start from the part "Piste d'amélioration" ? to better understand what should I do as the first step? remove the for loop? because I understood the general code somehow with the document in the Read.me file that Thomas wrote it, and I saw this part : Piste d'amélioration which has the For llop too


# To Do
- Start from the anynomizing the data, seperate the data that students didn't want to share their data from the students they who want to share their data.

- When the data is seperated; start with the nettoyage_fichier_2425 which Thomas worked on it but it uses For, so it takes lot's of time; replace the for by dataframe and pandas (make the code better). 

- One the two files above are done, try the visualisation part for the clean data, from the previous proccess.

**The whole idea until now is working on the same code of Thomas just make it better (remove the for) and more understandable**

# What is folder New src
To optimize the code of Thomas, it should replace the for loop by the pandas operations which makes it much faster. I copied all the file one by one and make them more efficient, the whole concept and logic are the same.