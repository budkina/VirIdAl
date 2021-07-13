FROM continuumio/miniconda3

RUN conda config --add channels defaults
RUN conda config --add channels bioconda
RUN conda config --add channels conda-forge
RUN conda config --add channels omnia
RUN conda config --add channels plotly

RUN conda install pandas samtools bedtools fastq_utils bowtie2 vsearch seqkit openmp diamond fastp termcolor plotly blast=2.11.0

ADD . .
