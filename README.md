# Redmine Billing Assistant - RedRep 
This is a base script to automagically pull redmine
reports down to .csv files and convert them to pdf files.
If no entries are found, the project is ignored.

## Examples Using Podman (Recommended)
Make sure to mount the reports dir as a volume to see reports.

### Build Image
    podman build . -t redrep

### Get all projects from config for March in 2023
    podman run -v ./reports:/app/reports:Z redrep -m 3 -y 2023

### Get reports for client1 for March
    podman run -v ./reports:/app/reports:Z redrep -m 3 -p client1

### List All Available projects
    podman run redrep -l

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

