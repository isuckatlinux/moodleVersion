import argparse
import requests
import re

import pyfiglet


def print_banner():
    ascii_banner = pyfiglet.figlet_format("Moodle Version")
    print(ascii_banner)


def parse_args():
    parser = argparse.ArgumentParser(description='Return the moodle version')
    parser.add_argument('-u', '--url', help='Url of the moodle main page', required=True)
    parser.add_argument('--username', help='Username of the teacher', required=True)
    parser.add_argument('--password', help='Password of the teacher', required=True)
    return vars(parser.parse_args())


def send_post(data):
    session = requests.Session()
    session.get('http://10.10.10.153/moodle/login/index.php')
    return session.post('http://10.10.10.153/moodle/login/index.php', data=data)


def sanitaze_url(url):
    if url[:-1] != '/':
        return url + '/'


def login(session: requests.Session, url: str, username: str, password: str):
    login_url = url + 'login/'
    credentials = {'anchor': '', 'username': username, 'password': password}
    session.get(login_url)
    respond = session.post(login_url, data=credentials)
    if 'loginerrormessage' in respond.text:
        print('Invalid credentials')
        return False
    return True


def get_ids(session: requests.Session, url):
    courses = []
    ids = []
    url = url + 'my/'
    html = session.get(url).text
    pattern = re.compile(r'http.+course.+id=[0-9]+.*')
    matches = pattern.finditer(html)
    for match in matches:
        if not courses.__contains__(match.group()):
            courses.append(match.group())
    pattern_id_course = re.compile(r'id=[0-9]+')
    for course in courses:
        id = pattern_id_course.search(course).group()[3:]
        ids.append(int(id))

    return ids


def get_moodle_version(session: requests.Session, url, course_id):
    url = url + f'course/view.php?id={course_id}&lang=en'
    response = session.get(url).text
    pattern = re.compile(r'http.*docs.*topics')
    pattern_version = re.compile(r'[0-9]+')
    match = pattern.search(response).group()
    match = pattern_version.search(match).group()
    match = match[:1] + '.' + match[1:]
    return match


def main():
    print_banner()
    args = parse_args()
    url = sanitaze_url(args['url'])
    username = args['username']
    password = args['password']
    print(f'{username}:{password}')
    session = requests.Session()
    if login(session, url, username, password):
        print('Valid credentials')
    else:
        print('Invalid credentials')
    ids = get_ids(session, url)
    version = get_moodle_version(session, url, ids[0])
    print(f'Version -> {version}')


main()
