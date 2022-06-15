from subprocess import call
import os
import sys
import logging
from collections import namedtuple
import report_utils
import database_search

SearchFile = namedtuple("SearchFile", "database report fields fasta evalue max_target_seqs")

class VirusSearch:
    def __init__(self,
        filename_gen,
        input_fasta,
        virus_search_s1_evalue_n,
        virus_search_s1_evalue_p,
        virus_search_s2_evalue_n,
        virus_search_s2_evalue_p,
        max_target_seqs,
        database_directory,
        virus_nucl_db_name,
        virus_prot_db_name,
        nucl_db_name,
        prot_db_name,
        threads):
        """Initialize VirusSearch class"""
        self.filename_gen = filename_gen
        self.input_fasta = input_fasta
        self.virus_search_s1_evalue_n=virus_search_s1_evalue_n
        self.virus_search_s1_evalue_p=virus_search_s1_evalue_p
        self.virus_search_s2_evalue_n=virus_search_s2_evalue_n
        self.virus_search_s2_evalue_p=virus_search_s2_evalue_p
        self.max_target_seqs = max_target_seqs
        self.database_directory=database_directory
        self.virus_nucl_db_name = virus_nucl_db_name
        self.virus_prot_db_name = virus_prot_db_name
        self.nucl_db_name = nucl_db_name
        self.prot_db_name = prot_db_name
        self.threads=threads

        # search report names
        self.virus_search_report_s1_nt = self.filename_gen.compose_filename("virus_search_s1.reportN",True)
        self.virus_search_report_s1_nr = self.filename_gen.compose_filename("virus_search_s1.reportX",True)
        self.virus_search_s1_found = self.filename_gen.compose_filename('virusdb.found',True)
        self.virus_search_report_s2_nt = self.filename_gen.compose_filename("virus_search_s2.reportN",True)
        self.virus_search_report_s2_nr = self.filename_gen.compose_filename("virus_search_s2.reportX",True)

        # result file names
        self.virus_search_res = self.filename_gen.compose_filename('virus_search.csv')
        self.viruses_res = self.filename_gen.compose_filename('viruses.csv')
        self.virus_search_notfound = self.filename_gen.compose_filename('virus_search.notfound.csv')

        # fasta files names
        self.virus_found_fasta = self.filename_gen.compose_filename("virusdb.found.fasta",True)
        self.virus_notfound_fasta = self.filename_gen.compose_filename("virusdb.notfound.fasta",True)
        self.virus_search_notfound_fasta = self.filename_gen.compose_filename('virus_search.notfound.fasta')
        self.additional_search_input_fasta = self.filename_gen.compose_filename('additional_search_input.fasta',True)

    def do_search(self):
        # BLAST + Diamond search in virus database
        self.filter_virus_db()

        # BLAST + Diamond search in nt/nr database for potential virus sequences
        if os.path.isfile(self.virus_found_fasta) and os.path.getsize(self.virus_found_fasta) > 0:
            self.process_potential_viruses()
        else:
            logging.info("Nothing was found in virus database")
            return self.additional_search_input_fasta

        # combine sequnces that were not found
        if not os.path.isfile(self.virus_notfound_fasta) or os.path.getsize(self.virus_notfound_fasta) == 0:
            logging.error("All sequences were found in potential virus search")
            sys.exit()

        if call('cat ' +
            self.virus_search_notfound_fasta + ' ' +
            self.virus_notfound_fasta + ' '
            ' > ' + self.additional_search_input_fasta, shell=True)!=0:
            logging.error("Failed to cat files")
            sys.exit()

        return self.additional_search_input_fasta

    def filter_virus_db(self):
        """Filter out sequences that were not found in virus database"""

        # Blast and diamond search in virus database
        logging.info("Searching in virus db")
        self.virus_search()

        # Split fasta file into found and notfound in virus database parts
        if os.path.getsize(self.virus_search_s1_found) != 0:
            if call(f'seqkit grep -j {self.threads} -f {self.virus_search_s1_found} {self.input_fasta} > {self.virus_found_fasta}', shell=True)!=0:
                logging.error("Seqkit grep known failed")
                sys.exit()

            if call(f'seqkit grep -j {self.threads} -v -f {self.virus_search_s1_found} {self.input_fasta} > {self.virus_notfound_fasta}', shell=True)!=0:
                logging.error("Seqkit grep unknown failed")
                sys.exit()
        else:
            if call(f'cp {self.input_fasta} {self.virus_notfound_fasta}', shell=True)!=0:
                logging.error("Copy file failed")
                sys.exit()

            if call(f'touch {self.virus_found_fasta}', shell=True)!=0:
                logging.error("Create empty file failed")
                sys.exit()

    def process_potential_viruses(self):
        """BLAST + Diamond search in nt/nr database of sequences identified as viruses on the previous step"""

        search_file_blastn = SearchFile(database = self.nucl_db_name,
            report = self.virus_search_report_s2_nt,
            fields = "qaccver saccver sskingdom ssciname salltitles pident evalue",
            fasta = self.virus_found_fasta,
            evalue = self.virus_search_s2_evalue_n,
            max_target_seqs = self.max_target_seqs)

        search_file_diamond = SearchFile(database = os.path.join(self.database_directory,self.prot_db_name),
            report = self.virus_search_report_s2_nr,
            fields = "qseqid sseqid sskingdoms sscinames salltitles pident evalue",
            fasta = self.virus_found_fasta,
            evalue = self.virus_search_s2_evalue_p,
            max_target_seqs = self.max_target_seqs)

        search_obj = database_search.DatabaseSearch(search_file_blastn,
            search_file_diamond,
            "megablast",
            "fast",
            self.threads)

        search_obj.search()

        # Merge reports into 1 result file
        report = report_utils.Report(
            self.filename_gen,
            self.virus_found_fasta,
            self.virus_search_report_s2_nt,
            self.virus_search_report_s2_nr,
            self.virus_search_res,
            self.viruses_res,
            self.virus_search_notfound,
            self.virus_search_notfound_fasta,
            self.threads,
            False)

        report.generate_reports()

        logging.info("Potential virus sequences processing complete")

    def virus_search(self):
        """Search sequences in virus databases"""

        search_file_blastn = SearchFile(database = self.virus_nucl_db_name,
            report = self.virus_search_report_s1_nt,
            fields = "qseqid",
            fasta = self.input_fasta,
            evalue = self.virus_search_s1_evalue_n,
            max_target_seqs = self.max_target_seqs)

        search_file_diamond = SearchFile(database = os.path.join(self.database_directory,self.virus_prot_db_name),
            report = self.virus_search_report_s1_nr,
            fields = "qseqid",
            fasta = self.input_fasta,
            evalue = self.virus_search_s1_evalue_p,
            max_target_seqs = self.max_target_seqs)

        search_obj = database_search.DatabaseSearch(search_file_blastn,
            search_file_diamond,
            "megablast",
            "sensitive",
            self.threads)

        search_obj.search()

        if call(f'cat {self.virus_search_report_s1_nt} {self.virus_search_report_s1_nr} > {self.virus_search_s1_found}', shell=True)!=0:
            logging.error("Failed to cat virus reports")
            sys.exit()
