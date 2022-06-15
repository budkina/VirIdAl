import os
from collections import namedtuple
import report_utils
import database_search

SearchFile = namedtuple("SearchFile", "database report fields fasta evalue max_target_seqs")

class AdditionalSearch:
    """Scan sequences that were not identified on the virus search step"""
    def __init__(self,
        filename_gen,
        input_fasta,
        additional_search_evalue_nt,
        additional_search_evalue_nr,
        max_target_seqs,
        database_directory,
        nucl_db_name,
        prot_db_name,
        threads):
        """Initialize AdditionalSearch class"""
        self.filename_gen = filename_gen
        self.input_fasta = input_fasta
        self.additional_search_evalue_nt = additional_search_evalue_nt
        self.additional_search_evalue_nr = additional_search_evalue_nr
        self.max_target_seqs = max_target_seqs
        self.database_directory = database_directory
        self.nucl_db_name = nucl_db_name
        self.prot_db_name = prot_db_name
        self.threads=threads

        # search report names
        self.additional_search_report_nt = self.filename_gen.compose_filename("additional_search.reportN",True)
        self.additional_search_report_nr = self.filename_gen.compose_filename("additional_search.reportX",True)

        # result file names
        self.viruses_res = self.filename_gen.compose_filename('viruses.csv')
        self.additional_search_res = self.filename_gen.compose_filename('additional_search.csv')
        self.additional_search_notfound = self.filename_gen.compose_filename('additional_search.notfound.csv')

        # fasta files names
        self.additional_search_search_input_fasta = self.filename_gen.compose_filename('additional_search_input.fasta',True)
        self.additional_search_notfound_fasta = self.filename_gen.compose_filename('additional_search.notfound.fasta')

    def do_search(self):
        """Process sequences"""
        search_file_blastn = SearchFile(database = self.nucl_db_name,
            report = self.additional_search_report_nt,
            fields = "qaccver saccver sskingdom ssciname salltitles pident evalue",
            fasta = self.input_fasta,
            evalue = self.additional_search_evalue_nt,
            max_target_seqs = self.max_target_seqs)

        search_file_diamond = SearchFile(database = os.path.join(self.database_directory,self.prot_db_name),
            report = self.additional_search_report_nr,
            fields = "qseqid sseqid sskingdoms sscinames salltitles pident evalue", 
            fasta = self.input_fasta,
            evalue = self.additional_search_evalue_nr,
            max_target_seqs = self.max_target_seqs)

        search_obj = database_search.DatabaseSearch(search_file_blastn,
            search_file_diamond,
            "megablast",
            "fast",
            self.threads)

        search_obj.search()

        report = report_utils.Report(self.filename_gen,
            self.input_fasta,
            self.additional_search_report_nt,
            self.additional_search_report_nr,
            self.additional_search_res,
            self.viruses_res,
            self.additional_search_notfound,
            self.additional_search_notfound_fasta,
            self.threads,
            append_to_existing = True)

        report.generate_reports()
        return self.additional_search_notfound_fasta