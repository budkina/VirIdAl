import sys
import subprocess
from collections import namedtuple
import logging

SearchFile = namedtuple("SearchFile", "database report fields fasta evalue")

class DatabaseSearch:
    """blastn/megablast/diamond search class"""
    def __init__(self,
        search_file_nt,
        search_file_nr,
        blastn_mode,
        diamond_mode,
        threads):
        self.search_file_nt = search_file_nt
        self.search_file_nr = search_file_nr
        self.blastn_mode = blastn_mode
        self.diamond_mode = diamond_mode
        self.threads=threads

    def search(self):
        """blastn/megablast/diamond search with search_file parameters"""
        processes = []

        # blastn or megablast search
        logging.info(f"blastn search, database:{self.search_file_nt.database} file:{self.search_file_nt.fasta}")

        blastn_process = subprocess.Popen(f"blastn -db {self.search_file_nt.database} " +
            f" -outfmt '6 delim=\t {self.search_file_nt.fields}' "+
            f" -num_threads {self.threads} "+
            f" -out {self.search_file_nt.report} "+
            f" -query {self.search_file_nt.fasta} "+
            f" -evalue {self.search_file_nt.evalue} "+
            f" -task {self.blastn_mode}", shell=True)

        processes.append(blastn_process)

        # diamond blastx search
        logging.info(f"diamond blastx search, database: {self.search_file_nr.database} file: {self.search_file_nr.fasta}")

        if self.diamond_mode == "sensitive":
            diamond_process = subprocess.Popen(f"diamond blastx --sensitive --db {self.search_file_nr.database}" +
                f" --outfmt 6 {self.search_file_nr.fields}" +
                f" --threads {self.threads}" +
                f" --out {self.search_file_nr.report}" +
                f" --query {self.search_file_nr.fasta}" +
                f" --evalue {self.search_file_nr.evalue}", shell=True)
        else:
            diamond_process = subprocess.Popen(f"diamond blastx --db {self.search_file_nr.database}" +
                f" --outfmt 6 {self.search_file_nr.fields}" +
                f" --threads {self.threads}" +
                f" --out {self.search_file_nr.report}" +
                f" --query {self.search_file_nr.fasta}" +
                f" --evalue {self.search_file_nr.evalue}", shell=True)

        processes.append(diamond_process)

        for process in processes:
            returncode = process.wait()
            if returncode!=0:
                logging.error(f"search failed {process.args}")
                sys.exit()
                