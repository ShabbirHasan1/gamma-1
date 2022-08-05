from bs4 import BeautifulSoup as bs4
import requests


def main():
    r = requests.get('https://trendlyne.com/stock-screeners/by-type/?tag=technical')
    soup = bs4(r.text, 'html.parser')
    print(soup.prettify())

main()