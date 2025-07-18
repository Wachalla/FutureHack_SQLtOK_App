# SQLtOK: Your Natural Language to SQL

## Problem Addressed
This project tackles the challenge that not everyone knows how to query databases or write scripts, which limits access to valuable data insights.

## Our Solution
SQLtOK is an AI tool that converts natural language questions into SQL queries or code for data analysis, making data insights accessible to non-coders.

## How to Run Locally

1.  **Clone the repository:** (Once you set up Git, this will be your repo link)
    ```bash
    git clone [https://github.com/your-username/FutureHack_SQLtOK_App.git](https://github.com/your-username/FutureHack_SQLtOK_App.git)
    cd FutureHack_SQLtOK_App # Or whatever your project folder is named
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Install spaCy and download its English model:**
    ```bash
    pip install spacy
    python -m spacy download en_core_web_sm
    ```
5.  **Run the Streamlit app:**
    ```bash
    streamlit run app3.py
    ```
    This will open the application in your web browser.

## Technologies Used
* Python
* Streamlit
* spaCy (for Natural Language Processing)
* Pattern Recognition

## Team Members
*Kofi Otabil Entsie
*Swafaa Salim Said Omar
*Dhaavita Sookun
*Brighton Moronda Moronda
*Samia Islam
* ...

## Future Enhancements
* Support for more complex SQL queries (JOINs, subqueries).
* Integration with live databases.
* Generation of Python code for data visualization (e.g., using Matplotlib/Seaborn).
* Voice to SQL input.