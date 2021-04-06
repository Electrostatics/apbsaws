"""Main program to process jobs on AWS."""

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from contextlib import ExitStack
from dataclasses import dataclass, field
from datetime import datetime
from logging import getLogger, ERROR, INFO
from io import TextIOWrapper
from os import path as ospath
from os import listdir
from subprocess import check_call, CalledProcessError
from sys import exit
from time import sleep, time
from rclone import Rclone

_LOGGER = getLogger(__name__)
PID = 0


@dataclass
class job_group:
    filename: str
    fh: TextIOWrapper = None
    jobs: list = field(default_factory=list)
    count: int = 0

    def append(self, element):
        self.jobs.append(element)


def handler(signal_received, frame):
    global PID

    kill_cmd = f"kill -9 {PID}"

    try:
        _LOGGER.critical("\n" + " " * 20 + f" {time.strftime('%H:%M:%S')}")
        check_call(kill_cmd, shell=True)
    except CalledProcessError as cpe:
        _LOGGER.critical("ERROR: %s", cpe)
        exit(0)


def get_job_type(file_list):
    apbs_job_type = False
    pdb2pqr_job_type = False
    for filename in file_list:
        if filename.endswith(".dx") or filename in "apbs_end_time":
            apbs_job_type = True
        if filename.endswith(".propka") or filename in "pdb2pqr_end_time":
            pdb2pqr_job_type = True
    if apbs_job_type and pdb2pqr_job_type:
        return "combined"
    if apbs_job_type:
        return "apbs"
    if pdb2pqr_job_type:
        return "pdb2pqr"
    return "unknown"


def get_jobs_from_cache(jobid_cache, job_filelist_cache):
    jobs = []
    jobs_done = []
    if ospath.exists(job_filelist_cache) and ospath.isfile(job_filelist_cache):
        with open(job_filelist_cache, "r") as fh:
            for curline in fh:
                jobs_done.append(curline.strip("\n"))
    if ospath.exists(jobid_cache) and ospath.isfile(jobid_cache):
        with open(jobid_cache, "r") as fh:
            for curline in fh:
                curline = curline.strip("\n")
                if curline not in jobs_done:
                    jobs.append(curline)
    else:
        raise FileNotFoundError()
    return jobs


def get_job_ids_from_cache(cache_file):
    jobs = []
    if ospath.exists(cache_file) and ospath.isfile(cache_file):
        with open(cache_file, "r") as fh:
            for curline in fh:
                job_id = curline.strip("\n").split(" ")[0].strip("/")
                if job_id is not None:
                    jobs.append(job_id)
    return jobs


def build_parser():
    """Build argument parser.

    :return:  argument parser
    :rtype:  ArgumentParser
    """
    desc = f"\n\tProcess jobs on AWS"

    parser = ArgumentParser(
        description=desc,
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print out verbose output",
    )
    parser.add_argument(
        "--cachejoblist",
        type=str,
        default="cache_meta/AZURE_CACHE.txt",
        help=("Local file to hold job ids"),
    )
    parser.add_argument(
        "--cachejobfilelist",
        type=str,
        default="cache_meta/AZURE_FILELIST_CACHE.txt",
        help=("Local download file to cache list of files for job ids"),
    )
    parser.add_argument(
        "--apitoken",
        type=str,
        default="https://pcycrb4wrf.execute-api.us-west-2.amazonaws.com/test/jobid",
        help=("AWS API Endpoint to get S3 tokens"),
    )
    parser.add_argument(
        "--jobid",
        type=str,
        default=None,
        help=("Jobid"),
    )
    parser.add_argument(
        "--rcloneconfig",
        type=str,
        default="S3",
        help=("rclone config to use (rclone listremotes)"),
    )
    parser.add_argument(
        "--rcloneremotepath",
        type=str,
        default="apbs-azure-migration",
        help=("rclone remote path for config"),
    )
    parser.add_argument(
        "--rclonemountpath",
        type=str,
        # TODO: This could be os.environ($HOME)/RCLONE_MOUNT or something
        default=None,
        required=True,
        help=("rclone directory to mount remote path"),
    )
    parser.add_argument(
        "--maxjobs",
        type=int,
        default=None,
        help=("The maximum number of jobs to process"),
    )
    # Add CACHE FILLENAME
    return parser.parse_args()


def main() -> None:
    """
    :return:  None
    """

    args = build_parser()
    rclone = Rclone(args.rcloneconfig)

    _LOGGER.setLevel(ERROR)
    if args.verbose:
        _LOGGER.setLevel(INFO)

    # TODO: Make this a command line argument
    # jobs = get_jobs_from_cache(args.cachejoblist, args.cachejobfilelist)
    job_types = {"apbs": 0, "pdb2pqr": 0, "combined": 0, "unknown": 0}
    firsttime = datetime.now()
    lasttime = firsttime
    filenames = [
        "cache_meta/cache_apbs.txt",
        "cache_meta/cache_pdb2pqr.txt",
        "cache_meta/cache_combined.txt",
        "cache_meta/cache_unknown.txt",
    ]
    job_caches = {
        "apbs": job_group(filename="cache_meta/cache_apbs.txt"),
        "pdb2pqr": job_group(filename="cache_meta/cache_pdb2pqr.txt"),
        "combined": job_group(filename="cache_meta/cache_combined.txt"),
    }

    with ExitStack() as stack:
        for key, target in job_caches.items():
            fname = target.filename
            file_handle = stack.enter_context(open(fname))
            job_list = get_job_ids_from_cache(fname)
            target.fh = file_handle
            target.jobs = job_list
            target.count = len(job_list)
            print(f"THING: {key} {target.count}")

    key = "apbs"
    for idx, job in enumerate(job_caches[key].jobs, start=1):
        if idx % 50 == 0:
            interval_time = datetime.now()
            print(
                f"IDX: {idx} {str(interval_time - lasttime)} {str(interval_time - firsttime)}"
            )
            lasttime = interval_time
        if args.maxjobs is not None and idx > args.maxjobs:
            break
        if args.jobid is not None and args.jobid not in job:
            continue
        print(f"MOUNTPATH: {args.rclonemountpath}")
        rclone.mount(args.rcloneremotepath + f"/{job}", args.rclonemountpath)
        file_list = []
        attempts = 0
        max_attempts = 20
        while not file_list and attempts < max_attempts:
            file_list = listdir(args.rclonemountpath)
            print(f"ATTEMPT: {attempts}, LIST: {file_list}")
            attempts += 1
            sleep(1)
        print(f"FILES: {file_list}")
        job_type = get_job_type(file_list)
        print(f"JOBTYPE: {job} = {job_type}")
        job_types[job_type] += 1

    _LOGGER.info("DONE: %s", str(datetime.now() - lasttime))
    print(f"{job_types}")


if __name__ == "__main__":
    main()