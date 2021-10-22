from subprocess import call
import sys

class Merge:
    """Merge class"""
    def __init__(self,
        filename_gen,
        threads):
        self.filename_gen = filename_gen
        self.threads = threads

    def do_merge(self, fastq_files, save_unmerged):
        """Merge overlapped paired-end reads"""
        merged = self.filename_gen.compose_filename('merged',True)
        fastp_json = self.filename_gen.compose_filename('fastp.merging.json')
        fastp_html = self.filename_gen.compose_filename('fastp.merging.html')
        merge_command = f'fastp --merge --merged_out {merged} --thread {self.threads} -j {fastp_json} -h {fastp_html} --in1 {fastq_files[0]} --in2 {fastq_files[1]}'
        if save_unmerged:
            merge_command += f' --include_unmerged'

        if call(merge_command, shell=True)!=0:
            sys.exit("fastp merge paired-end files failed")

        return merged
