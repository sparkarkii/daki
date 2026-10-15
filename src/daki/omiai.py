import requests
from bs4 import BeautifulSoup
import datetime
from collections import namedtuple

from mailer import Mailer
from dotenv import load_dotenv
from os import environ
from jinja2 import Environment, PackageLoader, select_autoescape


Daki = namedtuple('Daki', ['title', 'date', 'image', 'link'])

class Task:
	SITE = 'http://omiai-dakimakura.com/page/' 
	def __init__(self):
		self._date = datetime.date.today()
		self._new_dakis = []

	def run(self):
		are_new, page = True, 1
		while are_new:
			soup = self._fetch(page)
			dakis = self._get_data(soup)
			are_new = self._check(dakis)
			page += 1
		self._notify()

	def _fetch(self, page: int) -> BeautifulSoup:
		html = requests.get(Task.SITE+str(page), verify=False).content.decode()
		return BeautifulSoup(html, 'html5lib')

	def _get_data(self, soup) -> list[Daki]:
		return [
			Daki(
				title = str(arti.find('h2', class_='post-title').a.string),
				date = datetime.datetime.strptime(arti.find('p', class_='post-date').string, r'%Y年%m月%d日').date(),
				image = arti.find('div', class_='post-thumbnail').img.get('src'),
				link = arti.find('h2', class_='post-title').a.get('href'),
			)
			for arti in soup.find_all('article')
		]

	def _check(self, dakis: list[Daki]) -> bool:
		for daki in dakis: 
			if daki.date < self._date:
				return False
			self._new_dakis.append(daki)
		return True

	def _notify(self) -> None:
		load_dotenv()
		acco, pw = environ['EMAIL'], environ['PW']
		env = Environment(loader=PackageLoader('daki'), autoescape=select_autoescape)
		templ = env.get_template('email.html')
		subj = f'{self._date} new dakis'
		cont = templ.render(dakis=self._new_dakis)
		mailer = Mailer(acco, pw)
		mailer.send(subj, cont, subtype='html')


def main():
	task = Task()
	task.run()

if __name__ == '__main__':
	main()
