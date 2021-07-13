from subprocess import call
import os
import sys
from termcolor import colored

class Cluster:
    """FASTA file clusterization"""
    def __init__(self,
        filename_gen,
        identity,
        threads):
        """Init cluster submodel"""
        self.filename_gen = filename_gen
        self.identity = identity
        self.threads = threads

    def do_cluster(self, fasta):
        """Cluster input fasta file"""
        print(colored("Clustering with vsearch","green"))
        clustered_filename = self.filename_gen.compose_filename('clustered.fasta',True)

        if call(f"""vsearch --cluster_fast {fasta} --threads {self.threads} \
            --id {self.identity} --centroids {clustered_filename}""", shell=True)!=0:
            sys.exit("Clustering with vsearch failed")

        if not os.path.isfile(clustered_filename):
            sys.exit("Clustered file does not exist")
        return clustered_filename

