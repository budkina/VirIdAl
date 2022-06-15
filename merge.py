from subprocess import call
import sys
import logging

class Merge:
    """Merge class"""
    def __init__(self,
        filename_gen,
        threads):
        self.filename_gen = filename_gen
        self.threads = threads

    def do_merge(self, fastq_files, do_not_save_unmerged):
        """Merge overlapped paired-end reads"""
        merged = self.filename_gen.compose_filename('merged',True)
        fastp_json = self.filename_gen.compose_filename('fastp.merging.json')
        fastp_html = self.filename_gen.compose_filename('fastp.merging.html')
        merge_command = f'fastp --merge --merged_out {merged} --thread {self.threads} -j {fastp_json} -h {fastp_html} --in1 {fastq_files[0]} --in2 {fastq_files[1]}'
        if not do_not_save_unmerged:
            merge_command += f' --include_unmerged'

        if call(merge_command, shell=True)!=0:
            logging.error("fastp merge paired-end files failed")
            sys.exit()
            
        return merged
