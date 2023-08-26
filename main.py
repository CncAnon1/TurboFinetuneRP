import os
import argparse
import datetime

from colorama import just_fix_windows_console, Fore, Back, Style
just_fix_windows_console()

import openai


from modules import format_dataset, data_check, config

def upload_file():
    file = openai.File.create(
        file=open(config.dataset_file, "rb"),
        purpose='fine-tune'
    )
    with open("file_id.txt", "w") as f:
        f.write(file["id"])

def start_finetune():
    job = openai.FineTuningJob.create(
        training_file=open("file_id.txt", "r").read(), 
        model="gpt-3.5-turbo", 
        hyperparameters={"n_epochs": config.n_epochs}
    )
    print(f"Started a fine-tune job with the ID {job['id']}!")
    with open("ft_id.txt", "w") as f:
        f.write(job["id"])

def check_finetune():
    try:
        ft_id = open("ft_id.txt", "r").read()
        if len(ft_id) < 5: raise
    except:
        # Get the newest fine-tune job
        print("Failed getting the fine-tune job ID from the filename, getting the newest one from the API instead.")
        ft_id = openai.FineTuningJob.list(limit=1)["data"][0]["id"]
    state = openai.FineTuningJob.retrieve(ft_id)
    status = state["status"]
    if status == "succeeded":
        print(f"{Fore.GREEN}The fine-tune is done! The created fine-tune model name is {state['fine_tuned_model']}{Style.RESET_ALL}")
    elif status in ["failed", "cancelled"]:
        print(f"The fine-tune job failed or got cancelled, no clue why.")
    else:
        print(f"The fine-tuning job {ft_id} is {status}")
    print("Last 10 events:")
    events = openai.FineTuningJob.list_events(id=ft_id, limit=10)
    sorted_events = sorted(events["data"], key=lambda x: x['created_at'])
    for event in sorted_events:
        date = datetime.datetime.fromtimestamp(event["created_at"])
        print(f"{date} - {event['message']}")

def main():
    parser = argparse.ArgumentParser(description='OpenAI fine-tuning utility.')
    parser.add_argument('action', type=str, help='Action to perform: format, check, upload, start, status')
    args = parser.parse_args()

    if args.action == 'format':
        format_dataset.format()
    elif args.action == 'check':
        data_check.check()
    elif args.action == 'upload':
        upload_file()
    elif args.action == 'start':
        start_finetune()
    elif args.action == 'status':
        check_finetune()
    else:
        print(f"Unknown action: {args.action}")

if __name__ == "__main__":
    main()