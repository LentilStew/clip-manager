# Use an official Python runtime as the base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the project files to the container
COPY . .

# Expose the port that Streamlit listens on (default is 8501)
EXPOSE 8501

# Set the command to run the Streamlit app
CMD ["streamlit", "run", "main.py"]
