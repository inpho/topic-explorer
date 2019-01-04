FROM continuumio/miniconda3:latest

# Add gcc for vsm compilation
# This should really be removed since we should be testing that the builds on pypi are working...
RUN apt-get update
RUN apt-get install build-essential -y

# Set up Anaconda environment
RUN conda config --set always_yes yes --set changeps1 no
RUN conda install -q --yes pip numpy matplotlib scipy scikit-learn nltk unidecode wget decorator chardet ujson requests cython

WORKDIR /opt/inpho/

ADD topicexplorer /opt/inpho/topicexplorer
ADD topics.zip /opt/inpho/
ADD setup.py /opt/inpho/
ADD setup.cfg /opt/inpho/
ADD requirements.txt /opt/inpho/

RUN pip install -r requirements.txt .

