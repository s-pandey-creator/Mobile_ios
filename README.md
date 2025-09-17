# Mobile Automation Assignment

##  Overview
Automated tests for a sample mobile application using **Python, Appium, and pytest** on **BrowserStack**.

**Test coverage**
- Login: valid login, invalid login, logout  
- Product catalog: open catalog, view product details, verify name/price  
- Cart: add product, verify it appears  
- Sorting: apply sorting and verify order

##  Tech Stack
- Python 3
- appium-python-client
- pytest
- Allure reporting
- BrowserStack

##  Project Structure
mobile-assignment/
│── pages/
│── tests/
│── conftest.py
│── requirements.txt
│── README.md
│── allure-report/ # (generated after running tests)

##  Setup
 Clone the repo:
```bash
git clone https://github.com/s-pandey-creator/mobile-assignment.git
cd mobile-assignment

Install dependencies:

pip install -r requirements.txt

Set BrowserStack credentials:

setx BROWSERSTACK_USERNAME "sandeeppandey_3z5YkG"
setx BROWSERSTACK_ACCESS_KEY "7aU6Ny4pQdqVnJa8XxUw"

Generate Allure report:

allure generate allure-results -o allure-report --clean