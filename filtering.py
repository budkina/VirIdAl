from subprocess import call
import os
import sys
from termcolor import colored

class Filter:
    """Filter fastq by aligning to reference genomes"""
    def __init__(self,
        filename_gen,
        ref_dir,
        ref_names,
        threads):
        self.filename_gen = filename_gen
        self.ref_dir = ref_dir
        self.ref_names = ref_names
        self.threads = threads

    def do_filter(self, fastq):
        """Filter reads by aligning on a set of reference genomes"""
        if not os.path.isdir(self.ref_dir):
            sys.exit(f"Folder {self.ref_dir} does not exist")

        if not self.ref_names:
            print("Reference genome names are not defined!")
            return fastq

        for ref_name in self.ref_names:
            print(colored(f"Mapping to {ref_name}","green"))
            reference = os.path.join(self.ref_dir, ref_name)
            sam=self.filename_gen.compose_filename('sam', True)
            unaligned_fastq=self.filename_gen.compose_filename(ref_name + '.unaligned', True)
            if call(f'bowtie2 --un {unaligned_fastq} -p {self.threads} -x {reference} -U {fastq} -S {sam}', shell=True)!=0:
                sys.exit("Genome mapping failed")

        return unaligned_fastq
