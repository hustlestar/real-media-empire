import subprocess

import os
import shutil
import click
import datetime

CRYPTO_SRC = "G:\\OLD_DISK_D_LOL\\Projects\\ZZZenno"


@click.command()
@click.option("--bat_file", required=True)
@click.option("--excel_file", required=False)
def main(bat_file, excel_file):
    if excel_file:
        new_excel_file = excel_file.replace("input_", "")
        rename_existing_excel_file(new_excel_file)
        shutil.copy2(excel_file, new_excel_file)
        click.echo(f"Created a copy of '{excel_file}' as '{new_excel_file}'")

    process = subprocess.Popen(bat_file, shell=True, cwd=CRYPTO_SRC, text=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout, _ = process.communicate(timeout=600)
    click.echo("\nSTDOUT:\n" + stdout)


def rename_existing_excel_file(excel_file):
    if os.path.exists(excel_file):
        current_date = datetime.datetime.now().strftime("%Y%m%d%H%M")
        basename = os.path.basename(excel_file)
        new_name = excel_file.replace(basename, f"{current_date}_{basename}")
        os.rename(excel_file, new_name)
        click.echo(f"Renamed existing '{excel_file}' to '{new_name}'")


if __name__ == "__main__":
    main()
