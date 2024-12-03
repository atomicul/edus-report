# Edus report

 Simple CLI tool to scrape some info not otherwise easily accessible on [edus](https://app.edus.ro/)

## Unmaintained

Since the creation of this tool, the platform has improved a lot, making the script less and less useful. Because of this reason, and because of the frequency of these small changes, I have decided that I won't update this repo anymore.

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
