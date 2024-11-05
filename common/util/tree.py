import os


def print_directory_tree(root_dir, indent="", file_extensions=None, exclude_dirs=None):
    # 주어진 확장자가 없으면 모든 파일을 허용
    if file_extensions is None:
        file_extensions = []
    if exclude_dirs is None:
        exclude_dirs = []

    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)

        # 디렉토리일 경우, 제외할 디렉토리가 아니면 탐색
        if os.path.isdir(item_path):
            if item not in exclude_dirs:
                print(f"{indent}├── {item}/")
                print_directory_tree(item_path, indent + "│   ", file_extensions, exclude_dirs)
        else:
            # 지정한 확장자의 파일만 출력
            if any(item.endswith(ext) for ext in file_extensions):
                print(f"{indent}├── {item}")


if __name__ == "__main__":
    root_directory = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath((__file__)))))
    extensions = [".yaml", ".yml", ".py", ".env", ".txt"]
    exclude_dirs = ["venv", ".venv", "__pycache__", ".idea", ".git"]  # 제외할 디렉토리들

    print(f"{root_directory}/")
    print_directory_tree(root_directory, file_extensions=extensions, exclude_dirs=exclude_dirs)
