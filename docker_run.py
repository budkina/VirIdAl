import argparse
import sys
from subprocess import call

parser = argparse.ArgumentParser(prog='docker_run.py')
parser.add_argument('--name', help='Container name')
parser.add_argument('--input', help='Full path to input directory with input fastq files and, optionally, config.json and adapters.fa')
parser.add_argument('--output', help='Full path to output directory for results')
parser.add_argument('--database', help='Full path to database directory with reference genomes and databases for megablast and diamond')
parser.add_argument('--command', help='Command line for docker container in quotes, default: "python main.py --help"', default='"python main.py --help"')

args = parser.parse_args()

if call(f'docker run -v {args.input}:/input -v {args.output}:/output -v {args.database}:/database {args.name} {args.command}', shell=True)!=0:
    sys.exit(f"docker run {args.name} failed")
