# Set the base image
FROM python:3.14 as build

# Copy the current directory contents into the container
COPY . /usr/src/app

# Setup .env file to load environment variables
COPY .env /usr/src/app/.env

# Set the working directory
WORKDIR /usr/src/app

# Install dependencies
RUN pip install -r requirements.txt

FROM python:3.14
COPY --from=build /usr/src/app /usr/src/app

# Run the Django server
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

# For actual production & deployment, use separate databases and create another docker container where the database is more scalable and
# host it in a separate place than the actual web-app itself. Using database software like MySQL or Postgress

# Also, make things more secure before deployment making sure the settings.py and .env files are secure and mentioned in .gitignore

# Then run Docker-Compose which lets us run multiple different services together, where the web-app is in one container, the database
# is in another, but they need to interact with each other.