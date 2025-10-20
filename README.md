# Web Application Exercise

A little exercise to build a web application following an agile development process. See the [instructions](instructions.md) for more detail.

## Product vision statement

Our vision is to enhance the way people share and discover travel experiences by combining personal reflection with social connection. We aim to build a platform where travelers can rank, record, and relive their journeys while inspiring others to explore the world through authentic, community-driven insights. 

## User stories

[Link to User Stories as Issues](https://github.com/swe-students-fall2025/2-web-app-team-gals/issues)

All user stories marked as "Won't fix" or "Not Planned" are outdated and not our final user stories (unable to delete). View final user stories on the task boards, and in issues.

## Steps necessary to run the software

See instructions. Delete this line and place instructions to download, configure, and run the software here.

## Task boards

[Task Board Sprint 1](https://github.com/orgs/swe-students-fall2025/projects/27)
[Task Board Sprint 2](https://github.com/orgs/swe-students-fall2025/projects/31)

## Local Setup

### 1. Clone the repository
```
git clone https://github.com/swe-students-fall2025/2-web-app-team-gals.git
cd 2-web-app-team-gals
```
### 2. Create and activate a virtual environment
```
pip install pipenv
pipenv shell
```
### Note:
If you get an error saying  
```
Python version range specifier '>=3.8' is not supported
```
open the **`Pipfile`** and replace  
```
python_version = ">=3.8"
```
with your exact Python version, for example:  
```
python_version = "3.9"
```
or  
```
python_version = "3.10"
```
You can check your Python version by running:
```bash
python3 --version
```

### 3. Install Python dependencies
```
pipenv run pip3 install -r requirements.txt
```
### 4. Create a .env file
Create a .env file in the root of the project and add your MongoDB credentials:
```
MONGO_URI=mongodb+srv://aoh2024_db_user:6yrjkHaTdaJYk4Gu@cluster0.snrovyb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
DB_NAME=travel-rankings
```
### 5. Run the Flask application
```
cd travel-rankings
python app.py
```

### Demo Login
Email: test1@mail.com  
Password: test
