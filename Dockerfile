# BUILDING: docker build -t <container_name> .
# RUNNING: docker run <container_name> <python_program_path> <config_file_path>
# e.g. docker run --network="host" carouge_watering
FROM ubuntu:20.04
RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev
COPY ./requirements.txt /requirements.txt
WORKDIR /
RUN pip3 install -r requirements.txt
COPY . /
CMD ["python3", "main.py", "-cc", "config_real_data.json", "-cs", "schedule_real_data.json"]
