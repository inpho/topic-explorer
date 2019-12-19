FROM continuumio/miniconda3:4.3.14

# VOLUME /tmp

# Add gcc for vsm compilation
# This should really be removed since we should be testing that the builds on pypi are working...
RUN apt-get update
RUN apt-get install build-essential -y

# Set up Anaconda environment
RUN conda config --set always_yes yes --set changeps1 no
RUN conda install -q --yes pip numpy matplotlib scipy scikit-learn nltk unidecode wget decorator chardet ujson requests cython notebook pandas

#RUN conda update setuptools
#RUN pip install -U pip setuptools
#RUN pip install wget

#RUN pip install topicexplorer[htrc]
#RUN python -m nltk.downloader punkt stopwords wordnet

# ADD topicexplorer /opt/inpho/topicexplorer
# ADD topics.zip /opt/inpho/
# ADD setup.py /opt/inpho/
# ADD setup.cfg /opt/inpho/
# ADD requirements.txt /opt/inpho/

ADD . /topicexplorer/
WORKDIR /topicexplorer/
RUN pip install -r requirements.txt .

#ADD vsm /opt/inpho/vsm
#WORKDIR /opt/inpho/vsm
#RUN python setup.py develop

# RUN pip install --src . -e git+https://github.com/inpho/topic-explorer#egg=topicexplorer
# RUN rm -r topicexplorer/*


WORKDIR /var/inpho/

EXPOSE 5000
EXPOSE 8888
EXPOSE 8000
RUN export PS1="$ "
CMD ["/bin/bash"]
