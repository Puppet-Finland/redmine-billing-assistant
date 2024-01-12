#!/bin/env python
from redminelib import Redmine
from redminelib.resources import Project
import pandas as pd
from weasyprint import HTML, CSS
import csv
from datetime import datetime
import calendar
import argparse
import os
import yaml
import re

class RedReport:
    # NOTE: datestring = YYYY-MM-DD
    reports_path = "./reports"
    rate_limit = 1500
    def __init__(self, config, year):
        self.year = year
        self.API_KEY = config['API_KEY']
        self.RM_URL = config['REDMINE_SITE']
        self.redmine = Redmine(self.RM_URL, key=self.API_KEY)
        self.projects = []
        if 'RE_WHITELIST' in config:
            _projects = self.redmine.project.all()
            regex = config['RE_WHITELIST']
            for p in _projects:
                if re.search(regex, p.name, re.IGNORECASE):
                    self.projects.append(p)
        elif 'PROJECTS' in config:
            self.projects = config['PROJECTS']

    def _get_last_day(self, month: int) -> (str, str):
        m = "%02d" % int(month)
        lastday = calendar.monthrange(datetime.now().year, int(month))[1]
        return (lastday, m)


    def list_all_projects(self):
        projects = self.redmine.project.all()
        for p in projects:
            print(p)


    def convert_file(self, f: str, month: str, project):
        df = pd.read_csv(f, index_col=False)
        df = df.groupby(["User", "Issue"])['Hours'].sum().to_frame()

        ds = df.groupby(["User"])['Hours'].sum()
        df_totals = df["Hours"].sum()
        df_totals = pd.Series(df_totals).set_axis(["Total"])
        df_totals = pd.concat([ds, df_totals]).to_frame()
        df_totals.reset_index(inplace=True)
        df.reset_index(inplace=True)
        
        # Drop Duplicate users in User column
        df['User'] = df['User'].mask(df['User'].duplicated(), "")

        df_totals.columns = ["User", "Hours"]
        html1 = df.to_html(index=False, na_rep="", table_id="tickets")

        html2 = df_totals.to_html(index=False, table_id="totals")
        html_title = f"<h2><center>{project} - {month.title()} {self.year}</center></h2>" 
        html = html_title + html1 + '<br /><br />' + html2
        # HTML(string=html, encoding="utf-8").write_pdf(f"./reports/{month}-{project}.pdf")
        HTML(string=html, encoding="utf-8").write_pdf(target=f"./reports/{month}-{project.identifier}.pdf", stylesheets=[CSS('bootstrap.css')])


    def get_entries(self, from_date: str, to_date: str, 
                    project_id: str | None = None, user_id: str | None = None):
        return self.redmine.time_entry.filter(
                from_date=from_date,
                to_date=to_date,
                project_id=project_id,
                user_id=user_id,
                limit=self.rate_limit,)


    def print_monthly_all(self, m: int):
        csv_files = {}
        for p in self.projects:
            report = self.print_monthly_report(m, p)
            if report:
                csv_files[p] = report
        for p,f in csv_files.items():
            self.convert_file(f, calendar.month_name[int(m)], p)


    def print_monthly_report(self, m: int, project: Project):
        month_name = calendar.month_name[int(m)]
        p_id = project.identifier
        lastday, month = self._get_last_day(m)
        from_date = f"{self.year}-{month}-01"
        to_date = f"{self.year}-{month}-{lastday}"
        report = f"{month}-{p_id}-report.csv"
        entries = self.get_entries(from_date, to_date, p_id)
        if len(entries) == 0: 
            print(f"No entries for '{project}' in {month_name}")
            return None
        cols = ['issue','comments', 'hours', 'user']
        saved_file = entries.export('csv', savepath='./reports', filename=report, columns=cols)
        print(f"Printing '{project}' report for {month_name}")
        return saved_file
        

    def print_project_time(self, from_date, to_date, project):
        entries = self.redmine.time_entry.filter(
            from_date=from_date, 
            to_date=to_date, 
            project_id=project,)

        total = 0
        with open("times.csv", 'w') as f:
            w = csv.writer(f)
            w.writerow(["date", "comments", "hours"])
            for e in entries:
                total += e.hours
                date = e.created_on.date()
                w.writerow([date, e.comments, e.hours])
            w.writerow(["total", f"{total:.2f}"])

        print(f"Total: {total:.2f}")
    
if __name__ == '__main__':
    reports_dir = './reports'
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

    config = yaml.safe_load(open("./config.yaml"))
    parser = argparse.ArgumentParser(
                    prog='redreport.py',
                    description='Program to pull redmine reports',
                    epilog='This adds the ability to pull custom redmine reports easily.')
    parser.add_argument('-m', '--month', default=datetime.now().month)
    parser.add_argument('-y', '--year', default=datetime.now().year)
    parser.add_argument('-p', '--project')
    parser.add_argument('-l', '--list-projects', action='store_true')

    args = parser.parse_args()

    r = RedReport(config, args.year)

    if args.list_projects:
        r.list_all_projects()
    if args.month and not args.list_projects:
        if args.project:
            p = r.redmine.project.get(args.project)
            f = r.print_monthly_report(args.month, p)
            if f:
                r.convert_file(f, calendar.month_name[int(args.month)], p)
        else:
            r.print_monthly_all(args.month)
