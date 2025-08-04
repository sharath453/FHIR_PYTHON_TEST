[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/IbDq3QVj)
# FHIR Assessment Starter Kit

## Objective

1. There are 4 Descriptive type question which you need to answer in your words.

2. Analyze the provided CSV file, identify the corresponding FHIR resource, validate and convert the data to a FHIR Bundle (batch) using POST requests.

3. search query use case to implement to fetch records from fhir server 

4. search query use case to implement to fetch records from fhir server 

## Instructions

Descriptive 1, 2, 3 & 4 
 - Type your answer in the 4 descriptive file which are provided you will get the questions also there.

Prob 1
- Identify the FHIR resource type the CSV represents.
- Validate required fields and remove duplicates.
- Convert valid entries into a FHIR Bundle.
- Log errors for invalid entries as a file to 'output/error_log.csv'
- Save the bundle to `output/patient_bundle.json`.

Prob 2 & Prob 3
- come up with the search query first for the given use case 
- try it on Postman if you think that is good
- write the pyton program around that search query 
- and write the responses to file  

## Submission
- Python script 
    All the 4 descriptive questions answer in your words max 70 words.
    PROB_1_create_bundle.py
    PROB_2_search_query.py
    PROB_3_search_query.py
- Final FHIR Bundle and ouput as expected to outpout folder (`output/patient_bundle.json`)
- Error log (`output/error_log.csv`)
- Short explanation in README on resource mapping ()

## How to Start Guide 

1. create virtual environment 
    python -m venv venv
2. activate the virutal env 
    .\venv\Scripts\activate

    once its activated you will see somthing like (venv)-- which tells you are in virtual env now

3. install the dependencies package  
    pip install -r requirements.txt

4. now you can write the solution as python for both problem 
    descriptive questions under the folder descriptive. 
    one under --- PROB_1_create_bundle.py
    other under ---- PROB_2_searh_query.py
    and last one under ---- PROB_3_search_query.py

5. run the program once you done with writting and see the response if you think responses are good and it has generated the required output files you can move to final setup  

6. final setup to push your changes 
    git add .
    git commit -m "I <yourname> acknowledge that i have Completed the assignment without any cheating"
    git push

Good luck...!!!

Happy Coding :)