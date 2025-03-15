from datetime import datetime

def generate_backup_filename(base_name="LadderArchives"):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Format YYYY-MM-DD_HH-MM-SS
    return f"{base_name}/LadderArchives{timestamp}.txt"
