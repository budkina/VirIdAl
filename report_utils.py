import os
import sys
from subprocess import call
import pandas as pd
from termcolor import colored

class Report:

    def __init__(self,
        filename_gen,
        original_fasta,
        nt_report,
        nr_report,
        result_report,
        virus_report,
        notfound_report,
        notfound_fasta,
        threads,
        append_to_existing = False):
        self.filename_gen = filename_gen
        self.original_fasta = original_fasta
        self.nt_report = nt_report
        self.nr_report = nr_report
        self.result_report = result_report
        self.virus_report = virus_report
        self.notfound_report = notfound_report
        self.notfound_fasta = notfound_fasta
        self.threads = threads
        self.append_to_existing = append_to_existing
        self.merged = None

    def generate_reports(self):
        self.merge_nt_nr_reports()
        self.extract_virus_reports()
        self.get_notfound()

    def merge_nt_nr_reports(self):
        """Merge nt and nr search reports and select best hits"""
        try:
            nt_hits = pd.read_csv(self.nt_report, sep='\t',header=None)
            nt_hits.columns = ['nt_qaccver', 'nt_saccver', 'nt_sskingdom', 'nt_ssciname', 'nt_salltitles', 'nt_pident', 'nt_evalue']
            nt_hits =nt_hits.sort_values(by=['nt_evalue'], ascending=True).drop_duplicates(['nt_qaccver'])
            nt_hits.set_index('nt_qaccver', inplace=True)
        except:
            nt_hits=pd.DataFrame()
        try:
            nr_hits = pd.read_csv(self.nr_report, sep='\t',header=None)
            nr_hits.columns = ['nr_qaccver', 'nr_saccver', 'nr_sskingdom', 'nr_ssciname', 'nr_salltitles', 'nr_pident', 'nr_evalue'] 
            nr_hits = nr_hits.sort_values(by=['nr_evalue'], ascending=True).drop_duplicates(['nr_qaccver'])
            nr_hits.set_index('nr_qaccver', inplace=True)
        except:
            nr_hits=pd.DataFrame()

        self.merged = pd.concat([nt_hits,nr_hits], axis=1)
        self.merged.to_csv(self.result_report, header=True, index=True, sep='\t')
        print(colored(f"nt/nr search report is in {self.result_report}","green"))

    def extract_virus_reports(self):
        viruses = self.merged.loc[(self.merged['nt_sskingdom'] == 'Viruses') | (self.merged['nr_sskingdom'] == 'Viruses')]

        if self.append_to_existing:
            viruses.to_csv(self.virus_report, mode='a', header=True, index=True, sep='\t')
        else:
            viruses.to_csv(self.virus_report, header=True, index=True, sep='\t')

        viruses.to_csv(self.virus_report, header=True, index=True, sep='\t')
        print(colored(f"Virus hits are in {self.virus_report}","green"))

    def get_notfound(self):
        # Get sequence id list for fasta file
        all_entries_list = self.filename_gen.compose_filename("all_entries.list", True)
        if call(f'grep ">" {self.original_fasta}  | cut -c2- > {all_entries_list}', shell=True)!=0:
            sys.exit("Failed to grep IDs from " + self.original_fasta)

        # Save all sequences that were not found
        all_entries=pd.read_csv(all_entries_list,header=None)
        all_entries.set_index(0, inplace=True)
        notfound = all_entries.index.difference(self.merged.index).to_series()
        notfound.to_csv(self.notfound_report, index=False,header=False)

        if os.path.getsize(self.notfound_report) != 0:
            if call(f'seqkit grep -j {self.threads} -f {self.notfound_report} {self.original_fasta} > {self.notfound_fasta}', shell=True)!=0:
                sys.exit(f"Seqkit -f {self.notfound_report} {self.original_fasta} > {self.notfound_fasta} grep failed")

            print(colored(f"not found entries are in {self.notfound_report} and {self.notfound_fasta}","green"))