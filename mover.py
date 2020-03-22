#!/usr/local/bin/python3
import os
import argparse
import re
from concurrent import futures
from datetime import datetime
import shutil

from file_operations.filename_operations import file_exist, filename_ext, filename_without_ext, path_leaf


LINE_RE = "(?:!\[(.*?)\]\((.*?)\))"
line_regex = re.compile(LINE_RE)


def parse_files_from_list(files, direc=''):
    f_list = []

    for file_path in files:
        file_path = direc + file_path
        if not os.path.exists(file_path):
            print(f"file {file_path} not exists in the system.")
            continue
        if os.path.isdir(file_path):
            f_list.extend(parse_files_from_list(os.listdir(file_path), direc=file_path + '/'))
            continue
        elif not filename_ext(file_path) == '.md':
            print(f"file {file_path} is not a .md file.")
            continue
        f_list.append(file_path)
    return f_list


def get_base_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Process some markdown files')

    parser.add_argument('files', metavar='N', type=str, nargs='+',
                        help='input the files in the list')

    return parser


def exec_func(cmd_parser: argparse.ArgumentParser, task_func):
    """
    执行任务，在线程池中 处理任务的执行

    :param cmd_parser: 任务的 parser 对象
    :param task_func: 需要执行的任务函数
    :param need_field: 需要的字段
    :return:
    """
    args = cmd_parser.parse_args()
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(task_func, file_name): file_name for file_name in parse_files_from_list(args.files)}
        for future in futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                _ = future.result()
            except Exception as exc:
                print('%r generated an exception:\n %s' % (url, exc))
            else:
                print(f"Down with {future}")


def replace_link_with_related_path(link: str) -> str:
    """
    :param link: the input file link.
    :return: result of the target link.
    """
    pass


def process_file(file_name: str) -> bool:
    """
    :param file_name: markdown file name
    :return:
    """
    print(f'filename: {file_name}')
    if not file_exist(file_name):
        raise FileNotFoundError(f"file {file_name} not exists in the system.")
    if not filename_ext(file_name) == '.md':
        raise Exception(f"file {file_name} is not a .md file.")
    # get path leaf
    file_name_without_path = filename_without_ext(path_leaf(file_name))
    dir_path = os.path.dirname(file_name)
    new_text = ''
    cnt_line, image_cnt = 0, 0
    with open(file_name, encoding='utf-8', mode='r') as f:
        for line in f.readlines():
            cnt_line += 1
            match_result = line_regex.search(line)
            if match_result is not None:
                image_cnt += 1
                print(f"result: {match_result}, group: {match_result.group(2)}")

                image_link = match_result.group(2)
                print(f'image_link: {image_link}')
                if 'nmsl.maplewish.cn' not in image_link and 'http' not in image_link and 'www' not in image_link\
                        and not image_link.startswith('static'):
                    # new_file_name = f'blog:{file_name_without_path}:{path_leaf(image_link)}'
                    # f_name = file_name.replace(' ', '-')
                    f_leaf = path_leaf(image_link).replace(' ', '-')
                    new_file_name = f'{f_leaf}'

                    # a local file
                    image_abs_old_link = os.path.join(dir_path, image_link)
                    target_dir = os.path.join('static', datetime.today().strftime('%Y-%m-%d'))
                    image_new_link = os.path.join(target_dir, new_file_name)
                    if not os.path.exists(target_dir):
                        os.mkdir(target_dir)
                    if os.path.exists(image_new_link):
                        print(f"file {image_new_link}->{image_abs_old_link} already exists")
                    elif not os.path.exists(image_new_link):
                        shutil.copy(image_abs_old_link, image_new_link)

                    line = line.replace(image_link, image_new_link)
            new_text = new_text + line
    print(f'the file has {cnt_line} lines, and {image_cnt} has image')
    with open(file_name, encoding='utf-8', mode='w') as fw:
        fw.write(new_text)
    print(f' {file_name} markdown 成功转化为 static 下的链接')


if __name__ == '__main__':
    parser = get_base_parser()

    exec_func(parser, process_file)

