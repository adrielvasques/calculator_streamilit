
# FormGridXLSX

InputToXLSX: This project involves capturing form input data, processing it, and then displaying the results in an AgGrid template. The final output is conveniently provided in an XLSX format.


## Video Presentation
[![YouTube Video](https://img.youtube.com/vi/E3LZkOYzpOo/0.jpg)](https://www.youtube.com/watch?v=E3LZkOYzpOo)


## Description

InputToXLSX is a web application designed to simplify data handling. Built with the Streamlit framework, it allows users to enter data into a form, processes this data, and displays it in a clear, sortable table using AgGrid. The application offers the practical feature of exporting data directly to an Excel file (XLSX format), facilitating easy analysis and reporting.

The entered data pertains to BMI (Body Mass Index) calculations. The application provides a count for each BMI category based on the processed data, informing the user of the number of entries within each category. If a category has approximately 30 entries, the application will calculate the 75th percentile for that group. You can view the inputted data in an AgGrid table under the 'Dados Inseridos' tab, where you also have the option to delete an entry if necessary.

## Demo Website
⭐ [https://share.streamlit.io/sven-bo/streamlit-income-expense-tracker/app.py](https://percentilcalculator.streamlit.app/)

## Run the app
```
# vanilla terminal
streamlit run app.py

# quit
ctrl-c
```

## Environment Variables
To run this project, you will need to add the following environment variables
`DETA_KEY`

## Feedback
Got some thoughts or suggestions? Don't hesitate to reach out to me at avs@icomp.ufam.edu.br. I'd love to hear from you! 💡

## Ressources
This project is based on: 
