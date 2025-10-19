# Web Application Exercise

A little exercise to build a web application following an agile development process. See the [instructions](instructions.md) for more detail.

## Product vision statement

Our vision is to enhance the way people share and discover travel experiences by combining personal reflection with social connection. We aim to build a platform where travelers can rank, record, and relive their journeys while inspiring others to explore the world through authentic, community-driven insights. 

## User stories

[Link to User Stories as Issues](https://github.com/swe-students-fall2025/2-web-app-team-gals/issues)

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
### 3. Install Python dependencies
```
pipenv install -r requirements.txt
```
### 4. Create a .env file
Create a .env file in the root of the project and add your MongoDB credentials:
```
MONGO_URI=your_mongodb_uri_here
DB_NAME=your_database_name_here
```
### 5. Run the Flask application
```
cd travel-rankings
python app.py
```

### Demo Login
Email: test1@mail.com  
Password: test
