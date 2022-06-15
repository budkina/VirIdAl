FROM ubuntu
ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
RUN apt-get update
RUN apt-get install -y build-essential
RUN apt-get install -y git

RUN apt-get install -y wget && rm -rf /var/lib/apt/lists/*

RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh 
RUN conda --version

RUN conda init
RUN conda update conda
RUN conda create -n python3_env python=3.7
RUN conda config --add channels bioconda
RUN conda config --add channels plotly
RUN conda config --set channel_priority flexible
RUN conda install -n python3_env -c bioconda deepacvir
RUN conda install -n python3_env pandas 
RUN conda install -n python3_env samtools
RUN conda install -n python3_env bedtools
RUN conda install -n python3_env fastq_utils
RUN conda install -n python3_env bowtie2
RUN conda install -n python3_env vsearch
RUN conda install -n python3_env seqkit
RUN conda install -n python3_env -c conda-forge openmp
#RUN conda install -n python3_env diamond
RUN conda install -n python3_env plotly
RUN conda install -n python3_env blast=2.11.0
RUN conda install -n python3_env -c conda-forge numpy==1.19.5


RUN wget http://opengene.org/fastp/fastp
RUN chmod a+x fastp
RUN cp fastp /usr/bin/

RUN wget http://github.com/bbuchfink/diamond/releases/download/v2.0.9/diamond-linux64.tar.gz #2.0.14
RUN tar xzf diamond-linux64.tar.gz
RUN cp diamond /usr/bin/

RUN echo "conda activate python3_env" >> ~/.bashrc
RUN conda create -n python2_env python=2.7
RUN conda install -n python2_env scikit-learn
RUN conda install -n python2_env biopython
RUN conda install -n python2_env pandas
RUN conda install -n python2_env -c anaconda enum34
RUN conda install -n python2_env -c conda-forge keras=2.2.5

RUN conda install -n python3_env -c conda-forge tbb 

ARG CACHEBUST=1

RUN git clone https://github.com/NeuroCSUT/ViraMiner.git
ADD . .
WORKDIR "/ViraMiner"
RUN git apply /viraminer.diff
WORKDIR "/"
