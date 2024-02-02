# Redmine Billing Assistant - RedRep 
This is a base script to automagically pull redmine
reports down to .csv files and convert them to pdf files.
If no entries are found, the project is ignored.

## Examples Using Podman (Recommended)
Make sure to mount the reports dir as a volume to see reports.
Note: When using pod_run.sh, you can export an env var $REDREP_REPORTS_DIR and
the script will mount that dir with the internal app reports dir.

### Build Image
    podman build . -t redrep

### Get all projects from config for March in 2023
    podman run -v ./reports:/app/reports:Z redrep -m 3 -y 2023

### Get reports for client1 for March
    podman run -v ./reports:/app/reports:Z redrep -m 3 -p client1

### List All Available projects
    podman run redrep -l

### Or use the pod_run.sh script

Define a specific project pattern:

    ./pod_run.sh -m 3 -y 2023 -p client1

Use the default patterns from config.yaml:

    ./pod_run.sh -m 1 -y 2024

## How to get API Key from redmine
The API key can be found under 'my account' on the right panel.
    https://redmine.example.com/my/account

## Example Config
The config is read from the location script is ran. Note that regex
is taken as priority and that it will be case insensitive.

### Example with regex
    API_KEY: "12969b491059cc67b7gf81da25f34g823d4df4ef"
    REDMINE_SITE: "https://redmine.example.com"
    RE_WHITELIST: "(client1|hourly)"


### Example with specific projects
    API_KEY: "12969b491059cc67b7gf81da25f34g823d4df4ef"
    REDMINE_SITE: "https://redmine.example.com"
    PROJECTS:
        - client1
        - client2

