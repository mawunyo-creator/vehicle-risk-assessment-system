Vehicle Risk Assessment System

This web application validates 17-character Vehicle Identification Numbers (VINs), retrieves factory specifications and safety recall data using the National Highway Traffic Safety Administration (NHTSA) open APIs, and calculates an operational risk score. The application is built using Python and the Streamlit web framework.

Deployment Links
- Live Hosted Application: [https://vehicle-risk-assessment-system-xkqcckod4dp6pwpmo3vf3a.streamlit.app/]
- Source Repository: [https://github.com/mawunyo-creator/vehicle-risk-assessment-system.git]

Local Installation Manual
Execute the following commands sequentially within your terminal interface to run the application locally:

1. Clone the repository:
git clone [https://github.com/mawunyo-creator/vehicle-risk-assessment-system.git]

2. Change your directory to the project folder:
cd [vehicle-risk-assessment-system]

3. Install the required package dependencies:
pip install -r requirements.txt

4. Start the Streamlit application:
streamlit run main_app.py

External API Integrations
The application utilizes open web requests to gather official vehicle parameters:
- NHTSA vPIC Endpoint: Decodes the 17-character validation sequence to return data for Car Brand, Model Year, Model, and Assembly Manufacturer.
- NHTSA Recall Records Database: Checks published federal campaign records to find active manufacturing safety alerts matching the car model.

Testing Profiles and Validation Criteria
You can use these three specific strings within the application text input to verify the core validation and calculation features:

- 1G1YY26U0B5100016
This valid format code matches a mock record stored inside our local data folder. It tests how the dashboard calculates and displays historical metrics combined with live API data.

- 1FA6P8CF0LRE00003
This valid format code represents a real-world vehicle. It tests the application's ability to fetch specifications directly from the live web APIs while cleanly alerting the user that no local history profile exists in our file.

- 1FA6P8CF0LRE0O003
This code contains an intentional format error (the illegal character O). It tests the input validation layer, showing how the system catches typos using the official Modulus-11 calculation before running web queries.

Interface Representation
![Dashboard Screen](screenshots/dashboard.png)