# Edus report

 Simple CLI tool to scrape some info not otherwise easily accessible on [edus](https://app.edus.ro/)

## Unmaintained

Since the creation of this tool, the platform has improved a lot, making the script less and less useful.
Because of this reason, and because of the frequency of these small changes to the website,
I have decided that I won't update this repo anymore.

## Instructions to run on debian:

- Install [google chrome](https://www.google.com/chrome/)

- Install python (version >= 3.12)

  ```bash
  sudo apt update && sudo apt install python3.12 -y
  ```

- Clone the repository

  ```bash
  git clone https://github.com/atomicul/edus-report && cd edus-report
  ```

- (optional) Create a virtual environment

  ```bash
  python3.12 -m venv .venv && source ./.venv/bin/activate
  ```

- Install pip dependencies

  ```bash
  python3.12 -m pip install -r requirements.txt
  ```

- Run the program

  ```bash
  python3.12 main.py
  ```

## Help screen

```bash
./main.py --help
```

```
usage: ./main.py [-h] [-s STUDENT] [-a {aggregates,absences,grades,report}]
                 [-f {csv,txt}] [-o OUTPUT] [--shush]

CLI tool to exctract data from the edus.ro platform.

options:
  -h, --help            show this help message and exit
  -s, --student STUDENT
                        a substring to be searched in the student name, in the
                        case of a parent account
  -a, --action {aggregates,absences,grades,report}
                        lookup action to perform on the student
  -f, --format {csv,txt}
                        the format of the result table
  -o, --output OUTPUT   file to write the result table in
  --shush               turn off all non mandatory logging to stdout

Environment variables:
  USERNAME      email or phone number used for auth
  PASSWORD      password to be used for auth
  AUTH_COOKIE   'catalogsessionid' cookie on the website
In order to skip the authentication prompt, provide either the `AUTH_COOKIE` or the both of `USERNAME` and `PASSWORD`
```
