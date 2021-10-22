# VirIdAl

VirIdAl is a pipeline for the identification of virus sequences in NGS data. It allows you to perform a qualitative analysis on a metagenomic sample and extract a list of virus sequences and sequences from an unidentified source for further research.

## Workflow

VirIdAl workflow consists of the validation, quality trimming, filtering, clustering, virus search and additional search stages.

![Alt text](search.png?raw=true "Title")

The virus search stage is used to identify known viral sequences precisely. It is divided into two steps: first, the input sequences are searched in nucleotide and protein virus databases, and then the sequences detected are aligned to nt and nr databases. A high search sensitivity in the first step allows you to pick sequences similar to viral and reduce the number of sequences aligned to the nt and nr bases in the next step, increasing the search speed significantly.

On the additional search stage, the sequences that were filtered on the virus search stage can be rescanned.
It enables you to obtain sequences from unknown sources that were not assigned to any organism during the previous stages of the search and identify additional viral sequences that were filtered out during the virus search stage. 

## Getting Started
The script depends entirely on the packages available from conda. It is recommended to run it in a Docker container.

1. Building docker container

```
docker build /path/to/directory/VirIdAl -t viridal
```

2. Building databases

Specify a full path for a folder that will store BLAST and Diamond databases and reference genomes: /path/to/database/directory. Map /path/to/database/directory to /database/ folder while running docker container. The databases requre at least 200 GB free disk space.

```
docker run -v /path/to/database/directory:/database viridal python download_databases.py --num_threads 4
```

Scripts can be executed outside the docker container if all dependencies are installed and paths to input, output and database folders are provided using --input_dir, --output_dir and --db_dir options. To install the required conda packages:

```
conda config --add channels bioconda
conda config --add channels conda-forge
conda config --add channels omnia
conda config --add channels plotly
conda install pandas samtools bedtools fastq_utils bowtie2 vsearch seqkit openmp diamond fastp termcolor plotly blast=2.11.0
```

## Usage

Paths to input, output and database folders should be defined. These folders should be mapped to docker container filesystem folders: /input, /output and /database, respectively.

Example:
```
docker run -v /path/to/input/directory:/input \
-v /path/to/output/directory:/output \
-v /path/to/database/directory:/database \
viridal python main.py --num_threads 4 --ref_names GRCh38 --unpaired fastq_file

```
The same command can be launched from docker_run.py script:

```
python docker_run.py --name viridal --input /path/to/input/directory --output /path/to/output/directory --database /path/to/database/directory --command "python main.py --num_threads 4 --ref_names GRCh38 --unpaired fastq_file"
```

Input directory /path/to/input/directory should contain:

- input fastq files (single or paired end)
- file with adapters for fastp trimming adapters.fa (optionally)
- json file with configuration config.json (optionally). 

The output folder /path/to/input/ directory will contain the result report files.

The pipeline preferences can be set via configuration file config.json. The settings from the configuration override command-line options. All options in config.json coincide with command-line options names.

Example of configuration file usage:
```
docker run -v /path/to/input/directory:/input \
-v /path/to/output/directory:/output \
-v /path/to/database/directory:/database \
viridal python main.py --load_config 
```

or

```
python docker_run.py --name viridal --input  /path/to/input/directory --output /path/to/output/directory --database /path/to/database/directory --command "python main.py --load_config"
```

## Output files

- filename.viruses.csv - identified viruses
- filename.viruses_report.html - pie charts showing the identified viruses 
- filename.virus_search.csv - BLAST and Diamond results on sequences that were scanned as potential viruses
- filename.virus_search.notfound.csv - sequences that were not identified on the virus search stage
- filename.virus_search.notfound.fasta - fasta file with sequences that were not identified on the virus search stage
- filename.additional_search.csv - BLAST and Diamond results on sequences that were scanned on additional search stage
- filename.additional_search.notfound.csv - sequences that were not identified on the additional search stage
- filename.additional_search.notfound.fasta - fasta file with sequences that were not identified on the additional search stage

Intermediate and temporary files are cleaned up by default. This can be changed by specifying --keep_temp option.

## Command line options

```
usage: main.py [-h] [--unpaired UNPAIRED] [--forward FORWARD]
               [--reverse REVERSE] [--input_dir INPUT_DIR] [--load_config]
               [--config CONFIG] [--steps STEPS [STEPS ...]]
               [--output_dir OUTPUT_DIR] [--num_threads NUM_THREADS]
               [--keep_temp] [--save_unmerged] [--adapters ADAPTERS]
               [--average_qual AVERAGE_QUAL] [--min_len MIN_LEN]
               [--complexity_threshold COMPLEXITY_THRESHOLD] [--cut_front]
               [--cut_tail] [--cut_right] [--cut_window_size CUT_WINDOW_SIZE]
               [--cut_mean_quality CUT_MEAN_QUALITY]
               [--ref_names REF_NAMES [REF_NAMES ...]] [--identity IDENTITY]
               [--virus_search_s1_evalue_n VIRUS_SEARCH_S1_EVALUE_N]
               [--virus_search_s1_evalue_p VIRUS_SEARCH_S1_EVALUE_P]
               [--virus_search_s2_evalue_n VIRUS_SEARCH_S2_EVALUE_N]
               [--virus_search_s2_evalue_p VIRUS_SEARCH_S2_EVALUE_P]
               [--additional_search_evalue_n ADDITIONAL_SEARCH_EVALUE_N]
               [--additional_search_evalue_p ADDITIONAL_SEARCH_EVALUE_P]
               [--virus_nucl_db_name VIRUS_NUCL_DB_NAME]
               [--virus_prot_db_name VIRUS_PROT_DB_NAME]
               [--nucl_db_name NUCL_DB_NAME] [--prot_db_name PROT_DB_NAME]
               [--db_dir DB_DIR]

optional arguments:
  -h, --help            show this help message and exit

General:
  --unpaired UNPAIRED   Input fastq name (unpaired)
  --forward FORWARD     Input fastq name (paired-end, forward)
  --reverse REVERSE     Input fastq name (paired-end, reverse)
  --input_dir INPUT_DIR
                        Path to input folder, default: "/input/" for docker image
  --load_config         Use JSON file for configuration (overwrites command line parameters)
  --config CONFIG       JSON config file path, default: "/input/config.json" for docker image
  --steps STEPS [STEPS ...]
                        Set of steps to perform in analysis (default: merging qc filter cluster virus_search):
                        	merging: Paired-end reads merging using fastp, always performed
                        	qc: Quality filtering using fastp
                        	filter: Filter fastq by mapping reads on the reference genomes using bowtie2
                        	cluster: Fasta file clusterization using vsearch
                        	virus_search: Search for virus sequences, always performed
                        	additional_search: Search for sequences that were not identified at virus_search step
                        	all: Perform all steps
  --output_dir OUTPUT_DIR
                        Path to output folder, default: "/output/" for docker image
  --num_threads NUM_THREADS
                        Number of threads
  --keep_temp           Keep temporary files in output folder, default: false

Merging (fastp):
  --save_unmerged       Save unmerged reads for processing, default disabled

Quality control (fastp):
  --adapters ADAPTERS   Path to the file with the adapter sequences for fastp, default: /input/adapters.fa for docker image
  --average_qual AVERAGE_QUAL
                        Quality score mean threshold for filtering with fastp, default: 20
  --min_len MIN_LEN     Filter sequences shorter than min_len, default 36
  --complexity_threshold COMPLEXITY_THRESHOLD
                        The threshold value (between 0 and 100) for filtering low complexity sequence reads, default: 30
  --cut_front           Move a sliding window from 5' to 3', drop the bases in the window if its mean quality is below cut_mean_quality, default disabled
  --cut_tail            Move a sliding window from 3' to 5', drop the bases in the window if its mean quality is below cut_mean_quality, default disabled
  --cut_right           move a sliding window from 5' to 3', if meet one window with mean quality < threshold, drop the bases in the window and the right part, default disabled
  --cut_window_size CUT_WINDOW_SIZE
                        The window size option, default 4
  --cut_mean_quality CUT_MEAN_QUALITY
                        The mean quality requirement option by cut_front, cut_tail, and cut_right, default 20

Filtering:
  --ref_names REF_NAMES [REF_NAMES ...]
                        Reference genomes for filtering from database folder, default=[]

Clustering:
  --identity IDENTITY   Sequence identity threshold for clustering using vsearch, default: 0.9

Search:
  --virus_search_s1_evalue_n VIRUS_SEARCH_S1_EVALUE_N
                        Megablast search evalue threshold for virus search step 1, default = 1e-3
  --virus_search_s1_evalue_p VIRUS_SEARCH_S1_EVALUE_P
                        Diamond search evalue threshold for virus search step 1, default = 1e-3
  --virus_search_s2_evalue_n VIRUS_SEARCH_S2_EVALUE_N
                        Megablast search evalue threshold for virus search step 2, default = 1e-10
  --virus_search_s2_evalue_p VIRUS_SEARCH_S2_EVALUE_P
                        Diamond search evalue threshold for virus search step 2, default = 1e-10
  --additional_search_evalue_n ADDITIONAL_SEARCH_EVALUE_N
                        Megablast evalue threshold for additional search stage, default = 1e-10
  --additional_search_evalue_p ADDITIONAL_SEARCH_EVALUE_P
                        Diamond evalue threshold for additional search stage, default = 1e-10
  --virus_nucl_db_name VIRUS_NUCL_DB_NAME
                        Nucleotide database with virus sequences, default: virus_nucl
  --virus_prot_db_name VIRUS_PROT_DB_NAME
                        Protein database with virus sequences, default: virus_prot_diamond
  --nucl_db_name NUCL_DB_NAME
                        Nucleotide database with various sequences for search, default: nt
  --prot_db_name PROT_DB_NAME
                        Protein database with various sequences for search, default: nr_diamond
  --db_dir DB_DIR       Full path to database folder, default: "/database/" for docker image

  ```
  
## Download and build databases manually

- Download nt database and taxdb:

```
cd /path/to/database/directory
docker run -v /path/to/database/directory:/database -w /database viridal update_blastdb.pl --num_threads {num_threads} --decompress nt
wget https://ftp.ncbi.nlm.nih.gov/blast/db/taxdb.tar.gz && tar -zxvf taxdb.tar.gz
```

- Download nr database and build Diamond database:

```
wget https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/prot.accession2taxid.FULL.gz && gunzip prot.accession2taxid.FULL.gz
wget https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz && tar -zxvf taxdump.tar.gz
wget https://ftp.ncbi.nlm.nih.gov/blast/db/FASTA/nr.gz
docker run -v /path/to/database/directory:/database -w /database viridal diamond makedb --in nr.gz -d nr_diamond --taxonmap prot.accession2taxid.FULL --taxonnodes nodes.dmp --taxonnames names.dmp --threads {num_threads}
```

- Download and build Refseq virus nucleotide database:

```
wget https://ftp.ncbi.nlm.nih.gov/refseq/release/viral/viral.1.1.genomic.fna.gz && gunzip viral.1.1.genomic.fna.gz
wget https://ftp.ncbi.nlm.nih.gov/refseq/release/viral/viral.2.1.genomic.fna.gz && gunzip viral.2.1.genomic.fna.gz
wget https://ftp.ncbi.nlm.nih.gov/refseq/release/viral/viral.3.1.genomic.fna.gz && gunzip viral.3.1.genomic.fna.gz
cat viral.1.1.genomic.fna viral.2.1.genomic.fna viral.3.1.genomic.fna > viral.genomic.fna
docker run -v /path/to/database/directory:/database -w /database viridal makeblastdb -in viral.genomic.fna -out virus_nucl -dbtype nucl
```

- Download and build Refseq virus protein database:

```
wget https://ftp.ncbi.nlm.nih.gov/refseq/release/viral/viral.1.protein.faa.gz && gunzip viral.1.protein.faa.gz
wget https://ftp.ncbi.nlm.nih.gov/refseq/release/viral/viral.2.protein.faa.gz && gunzip viral.2.protein.faa.gz
wget https://ftp.ncbi.nlm.nih.gov/refseq/release/viral/viral.3.protein.faa.gz && gunzip viral.3.protein.faa.gz
cat viral.1.protein.faa viral.2.protein.faa viral.3.protein.faa > viral.protein.faa
docker run -v /path/to/database/directory:/database -w /database viridal diamond makedb --in viral.protein.faa -d virus_prot_diamond --threads {num_threads}
```

- Genomes for the filtering step, for example, human genome:

```
wget https://ftp.ncbi.nlm.nih.gov/refseq/H_sapiens/annotation/GRCh38_latest/refseq_identifiers/GRCh38_latest_genomic.fna.gz
docker run -v /path/to/database/directory:/database -w /database viridal bowtie2-build GRCh38_latest_genomic.fna.gz GRCh38
```
