from bs4 import BeautifulSoup
from selenium import webdriver

import datetime
from dateutil.relativedelta import relativedelta
import re
import signal


url = 'https://www.twitch.tv/dspstanky/videos/all'

def get_html_content(url):
	b = webdriver.PhantomJS()
	b.get(url)
	content = b.page_source

	b.service.process.send_signal(signal.SIGTERM)
	b.quit()

	return content

content = get_html_content(url)

# format datetime and discard all the html after that date
two_month_ago = datetime.date.today() + relativedelta(months=-2)
format = '%b %-d, %Y'
date_str = two_month_ago.strftime(format)

ind = content.find(date_str)

if ind:
    content = content[:ind]


soup = BeautifulSoup(content, 'html.parser')
tmp = soup.find_all('div', class_='tower--bleed')
source_str = str(tmp[0])

loots = re.findall(r'/videos/[0-9]{9}', source_str)

if loots:
    ids = [l.replace('/videos/', '') for l in loots]
else:
    # redo
    print 'No loots!'
