import os
import subprocess
from data_preprocess import build_result_json, read_json_files
from gen_results.a_proxy_mul_ping_gen_results import export_images
from crontab import CronTab

def create_cron_job(minute, hour, day_of_week):
    cron_command = f"python3 /path/to/test_speed.py {subscription_url} {proxy_name} {output_dir}"
    cron_time = f"{minute} {hour} * * {day_of_week}"
    cron_job = f"{cron_time} {cron_command}\n"
    
    # Get current crontab
    current_crontab = subprocess.run("crontab -l", shell=True, capture_output=True, text=True).stdout
    
    # Add new cron job
    with open("temp_cron", "w") as f:
        f.write(current_crontab)
        f.write(cron_job)
    
    # Install the cron job
    subprocess.run("crontab temp_cron", shell=True)
    os.remove("temp_cron")
    print("Cron job has been set.")

def main():
    cron = CronTab(user=True)

    command = input("请输入要执行的命令: ")
    comment = input("请为此任务添加一个注释: ")

    job = cron.new(command=command, comment=comment)

    schedule = input("请设置任务的时间表 (如 '* * * * *' 表示每分钟): ")
    job.setall(schedule)

    cron.write()

if (__name__ == "__main__"):
    folder_path = './'
    build_result_json(folder_path)
    export_images(folder_path)




    