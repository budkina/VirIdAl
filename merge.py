from subprocess import call
import sys

class Merge:
    """Merge class"""
    def __init__(self,
        temp,
        threads):
        self.temp = temp
        self.threads = threads

    def do_merge(self, fastq_files):
        """Merge overlapped paired-end reads"""
        merged = self.temp.compose_filename('merged',True)
        fastp_json = self.filename_gen.compose_filename('fastp.merging.json')
        fastp_html = self.filename_gen.compose_filename('fastp.merging.html')
        if call(f'fastp --merge --merged_out {merged} --thread {self.threads} -j {fastp_json} -h {fastp_html} --in1 {fastq_files[0]} --in2 {fastq_files[1]}', shell=True)!=0:
            sys.exit("fastp merge paired-end files failed")

        return merged
