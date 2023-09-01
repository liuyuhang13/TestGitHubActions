import filecmp
import os
import traceback
import shutil

BLOB_BASE_DIR = 'samples'
MODEL_FOLDER = 'model_folder'
BLOB_FILES_DIR = 'models'
GITHUB_FILES_DIR = 'temp'
EXAMPLES_UPLOAD_DIR = 'examples'


def get_examples_to_upgrade(blob_dir, blob_examples, github_dir):
    examples_to_upgrade = []
    for example in blob_examples:
        blob_example_dir = os.path.join(blob_dir, example)
        version = get_latest_version(blob_example_dir)
        blob_files = get_all_files(os.path.join(blob_example_dir, f'v{version}', MODEL_FOLDER))
        github_files = get_all_files(os.path.join(github_dir, example))
        print(os.path.join(blob_example_dir, f'v{version}', MODEL_FOLDER))
        print(len(blob_files))
        print(os.path.join(github_dir, example))
        print(len(github_files))
        changed = False
        if(len(blob_files) != len(github_files) and len(github_files) != 0):
            print(f'{example} changed, new files added or deleted.')
            changed = True
        for blob_file, github_file in zip(blob_files, github_files):
            if not filecmp.cmp(blob_file, github_file):
                print(f'blob_file:{blob_file}, github_file:{github_file} changed.')
                changed = True
                break

        if (changed):
            examples_to_upgrade.append(
                {'example': example, 'new_path': os.path.join(example, f'v{version + 1}', MODEL_FOLDER)})

    return examples_to_upgrade


def generate_examples_to_upload(examples_changed, examples_upload_dir='examples'):
    for item in examples_changed:
        src = os.path.join(GITHUB_FILES_DIR, item.get('example'))
        dst = os.path.join(examples_upload_dir, item.get('new_path'))
        print(dst)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copytree(src, dst)


def get_latest_version(example_dir):
    versions = os.listdir(example_dir)
    version_nums = [int(x[1:]) for x in versions]  # v1, v2, ... vN -> 1, 2, ... N
    return max(version_nums)


def get_all_files(example_dir):
    files = [file for sublist in [[os.path.join(i[0], j) for j in i[2]] for i in os.walk(example_dir)] for file in
             sublist]
    files.sort()
    return files


if __name__ == '__main__':
    try:
        blob_examples = set(os.listdir(os.path.join(BLOB_FILES_DIR, BLOB_BASE_DIR)))
        github_examples = set(os.listdir(GITHUB_FILES_DIR))
        print(f'examples in blob:{blob_examples}')
        print(f'examples in github:{github_examples}')
        new_examples = list(github_examples - blob_examples)
        if len(new_examples):
            print(f'New examples added: {new_examples}')
        new_examples = [{'example': x, 'new_path': os.path.join(x, 'v1', 'MODEL_FOLDER')} for x in new_examples]

        examples_to_upgrade = get_examples_to_upgrade(os.path.join(BLOB_FILES_DIR, BLOB_BASE_DIR), blob_examples, GITHUB_FILES_DIR)
        if len(examples_to_upgrade):
            print(f'Examples to upgrade: {[x["example"] for x in examples_to_upgrade]}')

        examples_changed = []
        examples_changed_path = []
        for item in new_examples:
            examples_changed.append(item)
            examples_changed_path.append(item['new_path'])

        for item in examples_to_upgrade:
            examples_changed.append(item)
            examples_changed_path.append(item['new_path'])

        generate_examples_to_upload(examples_changed, EXAMPLES_UPLOAD_DIR)
        examples_changed_path = [os.path.join(BLOB_BASE_DIR, x) for x in examples_changed_path]
        print(f'Examples updated paths: {examples_changed_path}')
    except Exception:
        traceback.print_exc()
        exit(-1)
