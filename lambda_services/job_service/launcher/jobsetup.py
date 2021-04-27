from urllib3.util import parse_url, url

class JobSetup:
    def __init__(self, job_id: str, job_date: str) -> None:
        self.job_id = job_id
        self.job_date = job_date
        self.input_files = []
        self.output_files = []

    def add_input_file(self, file_name: str):
        if self.is_url(file_name):
            self.input_files.append(file_name)
        else:
            self.input_files.append(
                f"{self.job_date}/{self.job_id}/{file_name}"
            )
            
    def is_url(self, file_string: str):
        url_obj = parse_url(file_string)
        if url_obj.scheme is None:
            return False
        else:
            return True
