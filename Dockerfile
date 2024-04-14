# Use the official Python 3.12 image as a base image
FROM python:3.12

# Set the working directory to /app
WORKDIR /app

# Copy the project files into the container at /app
COPY . .

# Install pipx and Poetry globally
RUN pip install pipx \
    && pipx install poetry

# Use Poetry to install the dependencies
RUN /root/.local/bin/poetry install 

# Expose the port the app runs on
EXPOSE 2000

ENV MET_CLIENT_ID='55806232-27fb-499f-b251-000042793c6f'
ENV MET_CLIENT_SECRET='80fa55ba-20d6-475c-bcdc-94f5501609d'

# Command to run on container start, adjust the module path as needed
CMD ["/root/.local/bin/poetry", "run", "uvicorn", "src.frcm.logic.bus_logic:app", "--host", "0.0.0.0", "--port", "2000"]
