import os
import sys
from subprocess import call
from termcolor import colored
import qc
import merge
import filtering
import clustering
import virus_search
import additional_search
import temp_files
from parse_arguments import get_arguments
from visualization import virus_pie_charts_report

def validate_fastq(fastq):
    """Check fastq validity"""
    print(colored(f"Checking {fastq} validity","green"))

    if call(f'fastq_info {fastq}', shell=True)!=0:
        sys.exit(f"Fastq file {fastq} is invalid")

######### MAIN #########

if __name__ == "__main__":

    args = get_arguments()

    # Check if input/output directories exist
    dirs = ['input_dir','output_dir']
    for d in dirs:
        if not os.path.isdir(args[d]):
            sys.exit(f" {d} folder: {args[d]} does not exist")

    # Check input files
    fastq_files = []
    paired_end = False
    base_filename = ""

    # if single-end
    if args['unpaired']:
        fastq_unpaired = os.path.join(args['input_dir'],args['unpaired'])
        validate_fastq(fastq_unpaired)
        fastq_files.append(fastq_unpaired)
        base_filename = os.path.basename(args['unpaired'])

    # if paired-end
    elif args['forward'] and args['reverse']:
        paired_end = True
        fastq_forward = os.path.join(args['input_dir'],args['forward'])
        fastq_reverse = os.path.join(args['input_dir'],args['reverse'])
        validate_fastq(fastq_forward)
        fastq_files.append(fastq_forward)
        validate_fastq(fastq_reverse)
        fastq_files.append(fastq_reverse)
        base_filename = os.path.basename(args['forward'])
    else:
        sys.exit("Input fastq files are not defined")

    # Create temp files class
    filename_gen = temp_files.TempFiles(base_filename)

    # Switch to output directory
    os.chdir(args['output_dir'])

    # Merge paired-end files
    if paired_end:
        merge_step = merge.Merge(filename_gen,
            args['num_threads'])

        fastq = merge_step.do_merge(fastq_files)
    else:
        fastq = fastq_files[0]

    # Quality control step
    if 'qc' in args['steps'] or 'all' in args['steps']:
        qc_step = qc.QC(filename_gen,
            args['adapters'],
            args['average_qual'],
            args['min_len'],
            args['complexity_threshold'],
            args['cut_mean_quality'],
            args['cut_front'],
            args['cut_tail'],
            args['cut_right'],
            args['cut_window_size'],
            args['num_threads'])

        fastq = qc_step.do_qc(fastq)

    # Filter step
    if 'filter' in args['steps'] or 'all' in args['steps']:
        filter_step = filtering.Filter(filename_gen,
            args['db_dir'],
            args['ref_names'],
            args['num_threads'])

        fastq = filter_step.do_filter(fastq)

    # Convert fastq to fasta
    fasta = filename_gen.compose_filename("fasta", True)

    if call(f"sed -n '1~4s/^@/>/p;2~4p' {fastq}  > {fasta}", shell=True)!=0:
        sys.exit("Failed to convert to fasta")

    if 'cluster' in args['steps'] or 'all' in args['steps']:
        cluster_step = clustering.Cluster(filename_gen,
            args['identity'],
            args['num_threads'])

        fasta = cluster_step.do_cluster(fasta)

    # Set blast database folder environment variable
    if not os.path.isdir(args['db_dir']):
        sys.exit(f"Folder {args['db_dir']} does not exist")

    os.environ['BLASTDB'] = args['db_dir']


    # Search for virus sequences
    search = virus_search.VirusSearch(filename_gen,
        fasta,
        args['virus_search_s1_evalue_n'],
        args['virus_search_s1_evalue_p'],
        args['virus_search_s2_evalue_n'],
        args['virus_search_s2_evalue_p'],
        args['db_dir'],
        args['virus_nucl_db_name'],
        args['virus_prot_db_name'],
        args['nucl_db_name'],
        args['prot_db_name'],
        args['num_threads'])

    notfound = search.do_search()

    # Process unidentified sequences
    if 'additional_search' in args['steps'] or 'all' in args['steps']:
        search = additional_search.AdditionalSearch(
            filename_gen,
            notfound,
            args['additional_search_evalue_n'],
            args['additional_search_evalue_p'],
            args['db_dir'],
            args['nucl_db_name'],
            args['prot_db_name'],
            args['num_threads'])

        search.do_search()

    # Create html report for found viruses
    if os.path.isfile(search.viruses_res) and os.path.getsize(search.viruses_res) > 0:
        virus_pie_charts_report(filename_gen, search.viruses_res)

    # Delete temporary files
    if not args['keep_temp']:
        filename_gen.delete_temp_files()
