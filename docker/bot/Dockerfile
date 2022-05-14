FROM python:3
USER root

RUN apt update
RUN apt -y install locales && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
RUN apt install libffi-dev
RUN apt install ffmpeg -y
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9
ENV TERM xterm

WORKDIR /code
ADD . .

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install mysql-connector-python
RUN python -m pip install --pre py-cord
RUN python -m pip install python-dotenv
CMD ["python", "main.py"]