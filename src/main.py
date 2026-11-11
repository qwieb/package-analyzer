import configparser
import sys
import os

def load_config(config_path: str) -> dict:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Файл конфигурации не найден: {config_path}")

    config = configparser.ConfigParser()
    config.read(config_path)

    if 'Settings' not in config:
        raise ValueError("В файле конфигурации отсутствует секция [Settings]")

    settings = config['Settings']
    parsed_config = {}

    package_name = settings.get('package_name')
    if not package_name:
        raise ValueError("Параметр 'package_name' не задан или пуст.")
    parsed_config['package_name'] = package_name

    repo_url = settings.get('repo_url')
    if not repo_url:
        raise ValueError("Параметр 'repo_url' не задан или пуст.")
    parsed_config['repo_url'] = repo_url

    test_mode_str = settings.get('test_mode', 'False').lower()
    if test_mode_str not in ['true', 'false']:
        raise ValueError(
            "Параметр 'test_mode' должен быть 'True' или 'False'."
        )
    parsed_config['test_mode'] = (test_mode_str == 'true')

    output_image = settings.get('output_image')
    if not output_image:
        raise ValueError("Параметр 'output_image' не задан или пуст.")
    parsed_config['output_image'] = output_image

    ascii_tree_str = settings.get('ascii_tree', 'False').lower()
    if ascii_tree_str not in ['true', 'false']:
        raise ValueError(
            "Параметр 'ascii_tree' должен быть 'True' или 'False'."
        )
    parsed_config['ascii_tree'] = (ascii_tree_str == 'true')

    return parsed_config

def main():
    config_file = 'config.ini'
    
    try:
        cfg = load_config(config_file)
        
        print("=== Текущая конфигурация ===")
        for key, value in cfg.items():
            print(f"{key}: {value}")
        print("============================")
        
        print("\n[Успех] Конфигурация загружена без ошибок.")

    except Exception as e:
        print(f"[Ошибка] {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()