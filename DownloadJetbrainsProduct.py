import os
import requests
import sys

__author__ = 'lirui'

products = [
    ('CLion', 'cpp', '1.1.1', ),
    ('RubyMine', 'ruby', '7.1.2'),
    ('ideaIU', 'idea', '14.1.5'),
    ('ideaIC', 'idea', '14.1.5'),
    ('PhpStorm', 'webide', '8.0.3'),
    ('pycharm-professional', 'python', '4.5.1'),
    ('pycharm-community', 'python', '4.5.1'),
    ('WebStorm', 'webstorm', '10'),
]
extensions = [
    '.dmg',
    '.exe',
    '.tar.gz',
    '-jdk-bundled.dmg',
    '-jdk-bundled.exe',
    '-jdk-bundled.tar.gz',
]
products_dir = 'jetbrains'
url_template = 'http://download.jetbrains.com/{1}/{0}-{2}{3}'


def make_directories(dir):
    try:
        os.makedirs(dir)
    except Exception as ex:
        print >> sys.stderr, '-> ignore', ex


def product_file(product, extension):
    return os.path.join(products_dir, product[1], product[0], product[2], product[0] + '-' + product[2] + extension)


def detect_available(product):
    url = url_template.format(*(product + (extensions[0],)))
    try:
        r = requests.head(url, allow_redirects=True)
        return r.headers['Content-Type'] not in ('application/xml', 'text/html')
    except IOError:
        return False


def next_versions(version):
    parts = version.split('.')
    for i, part in enumerate(parts):
        new_version = '.'.join(parts[0:i] + [str(int(part) + 1)] + map(lambda x: '0', parts[i + 1:])) 
        nv = new_version 
        yield new_version 

        while len(new_version.split('.')) < 3: 
            yield new_version + ".1"
            new_version += ".0"
            yield new_version 
            
        new_version = nv
        while new_version.endswith(".0"):
            new_version = new_version[:new_version.rindex(".0")]
            yield new_version


def download_product(product):
    for extension in extensions:
        local_file = product_file(product, extension)
        if os.path.exists(local_file):
            print '-> ignore downloaded', local_file
            continue

        tmp_file = local_file + ".tmp"
        make_directories(os.path.dirname(local_file))
        url = url_template.format(*(product + (extension, )))
        with open(tmp_file, 'wb') as tmp:
            print '-> downloading', local_file, 'from', url
            tmp.write(requests.get(url).content)
        os.rename(tmp_file, local_file)
        print '-> downloaded', local_file


def is_product_all_downloaded(product):
    for extension in extensions:
        local_file = product_file(product, extension)
        if not os.path.exists(local_file):
            return False
    return True


def main():
    for product in products:
        print 'checking', product[0]
        versions = [product[2]] + list(next_versions(product[2]))
        checked_versions = set()
        while versions:
            version = versions.pop()
            while version in checked_versions:
                if not len(versions):
                    version = None
                    break
                version = versions.pop()
            if not version:
                break

            checked_versions.add(version)

            print 'checking', product[0], version
            current_product = product[0:2] + (version, )
            if not detect_available(current_product):
                continue
            versions.extend(list(next_versions(version)))
            if is_product_all_downloaded(current_product):
                continue
            download_product(current_product)


if __name__ == '__main__':
    main()



