import yaml
from pathlib import Path

def main():
    path = Path("config/config.yaml")
    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    config["language"]["user_mother_tongue"] = "ja-JP"
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True)
    print("Config updated")

if __name__ == "__main__":
    main()
