import configparser
import sys
import os
import json 
import urllib.request 
from collections import deque

def load_config(config_path: str) -> dict:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Файл конфигурации не найден: {config_path}")
    config = configparser.ConfigParser()
    config.read(config_path)
    if 'Settings' not in config:
        raise ValueError("В файле конфигурации нет секции [Settings]")
    settings = config['Settings']
    parsed_config = {}
    package_name = settings.get('package_name')
    if not package_name:
        raise ValueError("Параметр 'package_name' не задан или пуст.")
    parsed_config['package_name'] = package_name
    repo_url = settings.get('repo_url')
    if not repo_url:
        raise ValueError(
            "Параметр 'repo_url' не задан или пуст."
        )
    parsed_config['repo_url'] = repo_url
    test_mode_str = settings.get('test_mode', 'False').lower()
    if test_mode_str not in ['true', 'false']:
        raise ValueError(
            "Параметр 'test_mode' должен быть 'True' или 'False'."
        )
    parsed_config['test_mode'] = (test_mode_str == 'true')
    output_image = settings.get('output_image')
    if not output_image:
        raise ValueError(
            "Параметр 'output_image' не задан или пуст."
        )
    parsed_config['output_image'] = output_image
    ascii_tree_str = settings.get('ascii_tree', 'False').lower()
    if ascii_tree_str not in ['true', 'false']:
        raise ValueError(
            "Параметр 'ascii_tree' должен быть 'True' или 'False'."
        )
    parsed_config['ascii_tree'] = (ascii_tree_str == 'true')
    max_depth_str = settings.get('max_depth')
    if not max_depth_str:
        raise ValueError("Параметр 'max_depth' не задан или пуст.")
    try:
        parsed_config['max_depth'] = int(max_depth_str)
    except ValueError:
        raise ValueError("Параметр 'max_depth' должен быть числом.")
    return parsed_config

def fetch_dependencies(config: dict) -> list:
    if config['test_mode']:
        print(f"[*] Режим тестирования: читаем {config['repo_url']}")
        try:
            with open(config['repo_url'], 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            raise ValueError(f"Ошибка чтения файла: {e}")
    else:
        print(f"[*] Загрузка данных из {config['repo_url']}...")
        try:
            response = urllib.request.urlopen(config['repo_url'])
            data = json.loads(response.read().decode('utf-8'))
        except Exception as e:
            raise ValueError(f"Ошибка сети: {e}")
    if 'info' in data:
        requires = data.get('info', {}).get('requires_dist', [])
    else:
        pkg_name = config['package_name']
        pkg_data = data.get(pkg_name, {})
        requires = pkg_data.get('info', {}).get('requires_dist', [])
    return requires if requires else []

def build_graph(config: dict) -> dict:
    start_pkg = config['package_name']
    max_depth = config['max_depth']
    graph = {start_pkg: []}
    queue = deque([(start_pkg, 0)])
    visited = {start_pkg}
    print(f"\n[*] Построение графа (BFS, глубина {max_depth})...")
    while queue:
        current_pkg, depth = queue.popleft()
        if depth >= max_depth:
            continue
        print(f"  -> Уровень {depth}: {current_pkg}")
        config['package_name'] = current_pkg
        deps = fetch_dependencies(config)
        config['package_name'] = start_pkg
        graph[current_pkg] = deps
        for dep in deps:
            dep_name = dep.split(' ')[0].strip()
            if dep_name not in visited:
                visited.add(dep_name)
                if dep_name not in graph:
                    graph[dep_name] = []
                queue.append((dep_name, depth + 1))
    return graph

def main():
    config_file = 'config.ini'
    try:
        cfg = load_config(config_file)
        print("=== Текущая конфигурация ===")
        for key, value in cfg.items():
            print(f"{key}: {value}")
        print("============================")
        print(f"\n[*] Анализ пакета: {cfg['package_name']}")
        deps = fetch_dependencies(cfg)
        graph = build_graph(cfg)
        print("\n=== Граф зависимостей ===")
        for pkg, pkg_deps in graph.items():
            if pkg_deps:
                print(f" {pkg} -> {', '.join(pkg_deps)}")
            else:
                print(f" {pkg} -> (нет зависимостей)")
        print("\n=== Прямые зависимости ===")
        if not deps:
            print("Зависимостей не найдено.")
        else:
            for dep in deps:
                print(f" - {dep}")
        print("==========================")
    except Exception as e:
        print(f"[Ошибка] {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()