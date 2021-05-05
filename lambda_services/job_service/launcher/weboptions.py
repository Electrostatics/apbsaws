import re
from io import StringIO


def sanitize_fileName(file_name):
    # TODO: 2020/06/30, Elvis - log that sanitization is happening if
    #                           pattern is seen
    file_name = re.split(r"[/\\]", file_name)[-1]
    file_name = file_name.replace(" ", "_")
    # fileName = fileName.replace('-', '_')
    return file_name


class WebOptionsError(Exception):
    def __init__(self, message, bad_key=None):
        super().__init__(message)
        self.bad_weboption = bad_key


class WebOptions:
    """Helper class for gathering and querying options selected by the user"""

    def __init__(self, form):
        """
        Gleans all information about the user selected options and uploaded
        files.
        Also validates the user input. Raises WebOptionsError if there is any
        problems.
        """
        # TODO: set second parameter of WebOptionError calls to specify bad key

        # options to pass to runPDB2PQR
        self.runoptions = {}
        self.otheroptions = {}

        self.runoptions["debump"] = "DEBUMP" in form
        self.runoptions["opt"] = "OPT" in form

        if "FF" in form:
            self.ff = form["FF"].lower()
        else:
            raise WebOptionsError("Force field type missing from form.")

        if "PDBID" in form and form["PDBID"] and form["PDBSOURCE"] == "ID":
            # TODO: 2021/02/23, Elvis - Use PDBID to get URL/set flag for PDB
            #                           file download
            # self.pdbfile = utilities.getPDBFile(form["PDBID"])
            # self.pdbfile = getPDBFile(form["PDBID"])
            self.user_did_upload = False
            # if self.pdbfile is None:
            #     raise WebOptionsError('The pdb ID provided is invalid.')
            # self.pdbfilestring = self.pdbfile.read()
            # self.pdbfile = StringIO(self.pdbfilestring)
            self.pdbfilename = form["PDBID"]

        elif form["PDBSOURCE"] == "UPLOAD" and form["PDBFILE"] != "":
            # self.pdbfilestring = files["PDB"].stream.read()
            self.user_did_upload = True
            # self.pdbfile = StringIO(self.pdbfilestring)
            # self.pdbfilename = sanitizeFileName(files["PDB"].filename)
            # pass filename through client
            self.pdbfilename = sanitize_fileName(
                form["PDBFILE"]
            )  # pass filename through client
            # print("filename: "+self.pdbfilename)
        else:
            raise WebOptionsError(
                "You need to specify a pdb ID or upload a pdb file."
            )

        if "PKACALCMETHOD" in form and form["PKACALCMETHOD"] != "none":
            if "PH" not in form:
                raise WebOptionsError("Please provide a pH value.")

            ph_help = "Please choose a pH between 0.0 and 14.0."
            try:
                ph = float(form["PH"])
            except ValueError:
                raise WebOptionsError(
                    "The pH value provided must be a number!  " + ph_help
                )
            if ph < 0.0 or ph > 14.0:
                text = "The entered pH of %.2f is invalid!  " % ph
                text += ph_help
                raise WebOptionsError(text)
            self.runoptions["ph"] = ph
            # build propka and pdb2pka options
            if form["PKACALCMETHOD"] == "propka":
                self.runoptions["ph_calc_method"] = "propka"
            if form["PKACALCMETHOD"] == "pdb2pka":
                self.runoptions["ph_calc_method"] = "pdb2pka"
                self.runoptions["ph_calc_options"] = {
                    "output_dir": "pdb2pka_output",
                    "clean_output": True,
                    "pdie": 8,
                    "sdie": 80,
                    "pairene": 1.0,
                }

        self.otheroptions["apbs"] = "INPUT" in form
        self.otheroptions["whitespace"] = "WHITESPACE" in form

        if self.ff == "user":
            # if "USERFF") and form["USERFF"].filename:
            # self.userfffilename = sanitizeFileName(form["USERFF"].filename)
            if "USERFFFILE" in form and form["USERFFFILE"] != "":
                self.userfffilename = sanitize_fileName(form["USERFFFILE"])
                # self.userffstring = form["USERFF"]
                self.runoptions["userff"] = StringIO(form["USERFFFILE"])
            else:
                text = (
                    "A force field file must be provided if using a user "
                    "created force field."
                )
                raise WebOptionsError(text)

            # if form.has_key("USERNAMES") and form["USERNAMES"].filename:
            if "NAMESFILE" in form and form["NAMESFILE"] != "":
                self.usernamesfilename = sanitize_fileName(form["NAMESFILE"])
                # self.usernamesstring = form["USERNAMES"]
                self.runoptions["usernames"] = StringIO(form["NAMESFILE"])
            else:
                text = (
                    "A names file must be provided if using a user "
                    "created force field."
                )
                raise WebOptionsError(text)

        if "FFOUT" in form and form["FFOUT"] != "internal":
            self.runoptions["ffout"] = form["FFOUT"]

        self.runoptions["chain"] = "CHAIN" in form
        self.runoptions["typemap"] = "TYPEMAP" in form
        self.runoptions["neutraln"] = "NEUTRALN" in form
        self.runoptions["neutralc"] = "NEUTRALC" in form
        self.runoptions["drop_water"] = "DROPWATER" in form

        if self.runoptions["neutraln"] and self.ff != "parse":
            raise WebOptionsError(
                "Neutral N-terminus and C-terminus require the "
                "PARSE forcefield."
            )

        # if form.has_key("LIGAND") and form['LIGAND'].filename:
        # self.ligandfilename=sanitizeFileName(form["LIGAND"].filename)
        if "LIGANDFILE" in form and form["LIGANDFILE"] != "":
            self.ligandfilename = sanitize_fileName(form["LIGANDFILE"])
            # ligandfilestring = form["LIGAND"]
            # for Windows and Mac style newline compatibility for pdb2pka
            # ligandfilestring = ligandfilestring.replace('\r\n', '\n')
            # self.ligandfilestring = ligandfilestring.replace('\r', '\n')

            # self.runoptions['ligand'] = StringIO(self.ligandfilestring)
            self.runoptions["ligand"] = StringIO(form["LIGANDFILE"])

        if self.pdbfilename[-4:] == ".pdb":
            self.pqrfilename = f"{self.pdbfilename[:-4]}.pqr"
        else:
            self.pqrfilename = f"{self.pdbfilename}.pqr"

        # Always turn on summary and verbose.
        self.runoptions["verbose"] = True
        self.runoptions["selectedExtensions"] = ["summary"]

    def get_logging_list(self):
        """Returns a list of options the user has turned on.
        Used for logging jobs later in usage.txt"""
        return [key for key in self if self[key]]

    def get_run_arguments(self):
        """Returns argument suitable for runPDB2PQR"""
        return self.runoptions.copy()

    def get_options(self) -> dict:
        """Returns all options for reporting to Google analytics"""
        options = self.runoptions.copy()
        options.update(self.otheroptions)

        options["ff"] = self.ff

        options["pdb"] = self.pdbfilename

        # propkaOptions is redundant.
        if "ph_calc_options" in options:
            del options["ph_calc_options"]

        if "ligand" in options:
            options["ligand"] = self.ligandfilename

        if "userff" in options:
            options["userff"] = self.userfffilename

        if "usernames" in options:
            options["usernames"] = self.usernamesfilename

        return options

    def get_command_line(self) -> str:
        command_line = []

        if not self.runoptions["debump"]:
            command_line.append("--nodebump")

        if not self.runoptions["opt"]:
            command_line.append("--noopt")

        if "ph" in self.runoptions:
            command_line.append(f"--with-ph={self.runoptions['ph']}")

        if "ph_calc_method" in self.runoptions:
            command_line.append(
                f"--ph-calc-method={self.runoptions['ph_calc_method']}"
            )

        if self.runoptions["drop_water"]:
            command_line.append("--drop-water")

        if self.otheroptions["apbs"]:
            command_line.append("--apbs-input")

        if self.otheroptions["whitespace"]:
            command_line.append("--whitespace")

        if "userff" in self.runoptions and self.ff == "user":
            command_line.append(f"--userff={self.userfffilename}")
            command_line.append(f"--usernames={self.usernamesfilename}")
        else:
            command_line.append(f"--ff={self.ff}")

        if "ffout" in self.runoptions:
            command_line.append(f"--ffout={self.runoptions['ffout']}")

        for o in ("chain", "typemap", "neutraln", "neutralc", "verbose"):
            if self.runoptions[o]:
                command_line.append("--" + o)

        if "ligand" in self.runoptions:
            command_line.append(f"--ligand={self.ligandfilename}")

        for ext in self.runoptions.get("selectedExtensions", []):
            command_line.append(f"--{ext}")

        command_line.append(self.pdbfilename)

        command_line.append(self.pqrfilename)

        return " ".join(command_line)

    def __contains__(self, item):
        """Helper for checking for the presence of an option"""
        return item in self.runoptions or item in self.otheroptions

    def has_key(self, item):
        """Helper for checking for the presence of an option"""
        return item in self.runoptions or item in self.otheroptions

    def __iter__(self):
        yield from self.runoptions
        yield from self.otheroptions

    def __getitem__(self, key):
        return (
            self.runoptions[key]
            if key in self.runoptions
            else self.otheroptions[key]
        )
