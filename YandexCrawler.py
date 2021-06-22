import argparse
from bs4 import BeautifulSoup
from selenium import webdriver
from pathlib import Path
from tqdm import tqdm


parser = argparse.ArgumentParser()
parser.add_argument("-name", "--search_word", required=True)
parser.add_argument("-count", "--want_count", type=int, default=40)
args = parser.parse_args()
search_word = args.search_word
want_count = args.want_count

scroll_count = max(want_count // 10, 1)

chore_driver_path = '/Users/stardust/code/project/Yandex-Image-Crawler/chromedriver'
url_list_dir = '/Users/stardust/code/project/Yandex-Image-Crawler/url_list'

url_list_file = f'{url_list_dir}/{search_word}.txt'

proxy="socks5://127.0.0.1:1086"

Path(url_list_dir).mkdir(parents=True, exist_ok=True)
print(f'search_word: {search_word}, want_count: {want_count}, scroll_count: {scroll_count}, url_list_file: {url_list_file}')

def get_url(driver, link_tag):
    href_src = "https://yandex.com" + link_tag.attrs['href']
    driver.get(href_src)
    temp_data = BeautifulSoup(driver.page_source,"html.parser").find_all("img","MMImage-Origin")
        
    try:
        attr_src = temp_data[0].attrs['src']
    except KeyError:
        attr_src = temp_data[0].attrs['data-src']
    except IndexError:
        return ''

    # print(attr_src)

    return attr_src

def crawl_yandex_img():
    url_info = "https://yandex.com/images/search?text="
    url_list = []

    # Chromedriver Option
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('--proxy-server={}'.format(proxy))
    options.add_argument('window-size=1920x1080')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--log-level=3')

    # Chromedriver 
    driver = webdriver.Chrome(chore_driver_path, options=options)

    driver.get(url_info + search_word)

    print('Load webpage complete')

    for i in range(scroll_count):
        driver.execute_script('window.scrollBy(0,document.body.scrollHeight)')
    
    print('Scroll complete')

    all_data = BeautifulSoup(driver.page_source,"html.parser").find_all("a", "serp-item__link")

    selected_data = all_data[:want_count]
    for i, link_tag in enumerate(tqdm(selected_data)):
        url = get_url(driver, link_tag)
        url_list.append(url)

    print('Gather url complete')

    url_list = list(filter(lambda x: x != '', url_list))
    url_list = list(map(lambda x: x + '\n', url_list))

    with open(url_list_file, 'w') as f:
        f.writelines(url_list)
    print(f"Write data to {url_list_file} complete")

# Main
if __name__ == "__main__":
    crawl_yandex_img()
