from subprocess import call
import sys
import os

class QC:
    """Quality control class"""
    def __init__(self,
        filename_gen,
        adapters,
        average_qual,
        min_len,
        complexity_threshold,
        cut_mean_quality,
        cut_front,
        cut_tail,
        cut_right,
        cut_window_size,
        threads):
        self.filename_gen = filename_gen
        self.adapters = adapters
        self.average_qual = average_qual
        self.min_len = min_len
        self.complexity_threshold = complexity_threshold
        self.cut_mean_quality = cut_mean_quality
        self.cut_front = cut_front
        self.cut_tail = cut_tail
        self.cut_right = cut_right
        self.cut_window_size = cut_window_size
        self.threads = threads

    def do_qc(self, fastq):
        """Trim reads"""
        self.fastq = fastq
        self.trim()
        return self.fastq

    def trim(self):
        """Adapters removal, sequence trimming, filtering based on quality and length"""
        trimmed = self.filename_gen.compose_filename('trimmed',True)
        fastp_json = self.filename_gen.compose_filename('fastp.json')
        fastp_html = self.filename_gen.compose_filename('fastp.html')

        trim_command = f"""fastp --in1 {self.fastq} --length_required  {self.min_len} --low_complexity_filter \
        --complexity_threshold {self.complexity_threshold }  --average_qual {self.average_qual} \
        --out1 {trimmed} -j {fastp_json} -h {fastp_html} --thread {self.threads}"""

        if os.path.isfile(self.adapters):
            trim_command += f' --adapter_fasta {self.adapters} '

        if self.cut_front:
            trim_command += f' --cut_front --cut_mean_quality {self.cut_mean_quality} --cut_window_size {self.cut_window_size}'

        if self.cut_tail:
            trim_command += f' --cut_tail --cut_mean_quality {self.cut_mean_quality}  --cut_window_size {self.cut_window_size}'

        if self.cut_right:
            trim_command += f' --cut_right --cut_mean_quality {self.cut_mean_quality}  --cut_window_size {self.cut_window_size}'

        if call(trim_command, shell=True)!=0:
            sys.exit("Trim failed")

        self.fastq = trimmed
        