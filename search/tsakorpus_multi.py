
import glob
import os
import shutil
import subprocess
import sys

import flask
import werkzeug.middleware.dispatcher as dispatcher
from werkzeug.serving import run_simple

import web_app

base_dir_path = '__corpus_data__'

def main_prepare(args):

    index_value = len('perspective_')

    for perspective_dir_path in (

        glob.glob(
            os.path.join(
                args[0], 'perspective_*_*'))):

        corpus_name = (
            os.path.basename(perspective_dir_path)[index_value:])

        corpus_dir_path = (
            os.path.join(base_dir_path, corpus_name))

        # Configuration.

        conf_dir_path = (
            os.path.join(corpus_dir_path, 'conf'))

        os.makedirs(
            conf_dir_path, exist_ok = True)

        shutil.copy(
            os.path.join(perspective_dir_path, 'categories.json'),
            conf_dir_path)

        shutil.copy(
            os.path.join(perspective_dir_path, 'corpus.json'),
            conf_dir_path)

        # Data.

        data_dir_path = (
            os.path.join(corpus_dir_path, 'corpus', corpus_name))

        os.makedirs(
            data_dir_path, exist_ok = True)

        shutil.copy(
            os.path.join(perspective_dir_path, 'corpus.json.gz'),
            data_dir_path)

        # Translations.

        translations_dir_path = (
            os.path.join(corpus_dir_path, 'translations'))

        shutil.copytree(
            'web_app/translations',
            translations_dir_path,
            dirs_exist_ok = True)

        shutil.copy(
            os.path.join(perspective_dir_path, 'corpus-specific-en.txt'),
            os.path.join(translations_dir_path, 'en', 'corpus-specific.txt'))

        shutil.copy(
            os.path.join(perspective_dir_path, 'corpus-specific-ru.txt'),
            os.path.join(translations_dir_path, 'ru', 'corpus-specific.txt'))

def main_index(args):

    for corpus_dir_path in (

        glob.glob(
            os.path.join(
                base_dir_path, '*'))):

        corpus_name = (
            os.path.basename(corpus_dir_path))

        arg_list = [
            'python3',
            '../indexator/indexator.py',
            '-y',
            '--tsakorpus-dir=..',
            f'--data-dir={corpus_dir_path}']

        print(arg_list)
        subprocess.run(arg_list, check = True)

def create_app():

    app_list = []

    for corpus_dir_path in (

        glob.glob(
            os.path.join(
                base_dir_path, '*'))):

        corpus_name = (
            os.path.basename(corpus_dir_path))

        app = (

            web_app.create_app(
                corpus_dir_path,
                os.path.join(corpus_dir_path, 'translations'),
                app_list[0][1].sc.es if app_list else None))

        app_list.append(
            ('/' + corpus_name, app))

    return (
        dispatcher.DispatcherMiddleware(
            app_list[0][1], dict(app_list)))

def main_run(args):

    run_simple('localhost', 5000, create_app())

if __name__ == "__main__":

    if len(sys.argv) > 1:

        if sys.argv[1] == 'prepare':
            main_prepare(sys.argv[2:])

        elif sys.argv[1] == 'index':
            main_index(sys.argv[2:])

        else:
            raise NotImplementedError

    else:
        main_run(sys.argv[1:])

