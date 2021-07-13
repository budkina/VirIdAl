import argparse
from subprocess import call
import sys
import os

parser = argparse.ArgumentParser()

parser.add_argument('--db_dir',
    help='Full path to blast database folder, default: "/database/" for docker image',
    default='/database/')

parser.add_argument('--num_threads',
    help='Number of threads',
    default="1")

args = parser.parse_args()

print('Note: The default databases pack requres at least 200 GB!')

os.chdir(args.db_dir)

print('Download and build virus_nucl')

if call(f"wget -O viral.1.1.genomic.fna.gz https://ftp.ncbi.nlm.nih.gov/refseq/release/viral/viral.1.1.genomic.fna.gz && gunzip -f viral.1.1.genomic.fna.gz", shell=True)!=0:
    sys.exit(f"wget viral.1.1.genomic.fna.gz failed")

if call(f"wget -O viral.2.1.genomic.fna.gz https://ftp.ncbi.nlm.nih.gov/refseq/release/viral/viral.2.1.genomic.fna.gz && gunzip -f viral.2.1.genomic.fna.gz", shell=True)!=0:
    sys.exit(f"wget viral.2.1.genomic.fna.gz failed")

if call(f"wget -O viral.3.1.genomic.fna.gz https://ftp.ncbi.nlm.nih.gov/refseq/release/viral/viral.3.1.genomic.fna.gz && gunzip -f viral.3.1.genomic.fna.gz", shell=True)!=0:
    sys.exit(f"wget viral.3.1.genomic.fna.gz failed")

if call(f"cat viral.1.1.genomic.fna viral.2.1.genomic.fna viral.3.1.genomic.fna > viral.genomic.fna", shell=True)!=0:
    sys.exit(f"cat to viral.genomic.fna failed")

if call(f"makeblastdb -in viral.genomic.fna -out virus_nucl -dbtype nucl", shell=True)!=0:
    sys.exit(f"makeblastdb virus_nucl failed")

for file in ['viral.1.1.genomic.fna', 'viral.2.1.genomic.fna', 'viral.3.1.genomic.fna', 'viral.genomic.fna']:
    os.remove(file)

print('Download and build virus_prot_diamond')

if call(f"wget -O viral.1.protein.faa.gz https://ftp.ncbi.nlm.nih.gov/refseq/release/viral/viral.1.protein.faa.gz && gunzip -f viral.1.protein.faa.gz", shell=True)!=0:
    sys.exit(f"wget viral.1.protein.faa.gz failed")

if call(f"wget -O viral.2.protein.faa.gz https://ftp.ncbi.nlm.nih.gov/refseq/release/viral/viral.2.protein.faa.gz && gunzip -f viral.2.protein.faa.gz", shell=True)!=0:
    sys.exit(f"wget viral.2.protein.faa.gz failed")

if call(f"wget -O viral.3.protein.faa.gz https://ftp.ncbi.nlm.nih.gov/refseq/release/viral/viral.3.protein.faa.gz && gunzip -f viral.3.protein.faa.gz", shell=True)!=0:
    sys.exit(f"wget viral.3.protein.faa.gz failed")

if call(f"cat viral.1.protein.faa viral.2.protein.faa viral.3.protein.faa > viral.protein.faa", shell=True)!=0:
    sys.exit(f"cat to viral.protein.faa failed")

if call(f"diamond makedb --in viral.protein.faa -d virus_prot_diamond --threads {args.num_threads}", shell=True)!=0:
    sys.exit(f"diamond makedb virus_prot_diamond failed")

for file in ['viral.1.protein.faa', 'viral.2.protein.faa', 'viral.3.protein.faa', 'viral.protein.faa']:
    os.remove(file)

print('Download nt and taxdb')

if call(f"update_blastdb.pl --num_threads {args.num_threads} --decompress nt", shell=True)!=0:
    sys.exit(f"update_blastdb.pl nt failed")

if call(f"wget -O taxdb.tar.gz https://ftp.ncbi.nlm.nih.gov/blast/db/taxdb.tar.gz && tar -zxvf taxdb.tar.gz", shell=True)!=0:
    sys.exit(f"wget taxdb.tar.gz failed")

print('Download and build nr_diamond')

if call(f"wget -O prot.accession2taxid.FULL.gz https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/prot.accession2taxid.FULL.gz && gunzip -f prot.accession2taxid.FULL.gz", shell=True)!=0:
    sys.exit(f"wget prot.accession2taxid.FULL.gz failed")

if call(f"wget -O taxdump.tar.gz https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz && tar -zxvf taxdump.tar.gz", shell=True)!=0:
    sys.exit(f"wget taxdump.tar.gz failed")

if call(f"wget -O nr.gz https://ftp.ncbi.nlm.nih.gov/blast/db/FASTA/nr.gz", shell=True)!=0:
    sys.exit(f"wget nr.gz failed")

if call(f"diamond makedb --in nr.gz -d nr_diamond --taxonmap prot.accession2taxid.FULL --taxonnodes nodes.dmp --taxonnames names.dmp --threads {args.num_threads}", shell=True)!=0:
    sys.exit(f"diamond makedb nr_diamond failed")

for file in ['citations.dmp', 'delnodes.dmp', 'division.dmp', 'gencode.dmp', 'merged.dmp', 'names.dmp', 'nodes.dmp', 'gc.prt', 'readme.txt', 'prot.accession2taxid.FULL', 'nr.gz']:
    os.remove(file)

print('Download and build GRCh38 index')

if call(f"wget -O GRCh38_latest_genomic.fna.gz https://ftp.ncbi.nlm.nih.gov/refseq/H_sapiens/annotation/GRCh38_latest/refseq_identifiers/GRCh38_latest_genomic.fna.gz", shell=True)!=0:
    sys.exit(f"wget GRCh38_latest_genomic.fna.gz failed")

if call(f"bowtie2-build GRCh38_latest_genomic.fna.gz GRCh38", shell=True)!=0:
    sys.exit(f"bowtie2-build GRCh38 failed")
