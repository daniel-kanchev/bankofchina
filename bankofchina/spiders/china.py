import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bankofchina.items import Article


class ChinaSpider(scrapy.Spider):
    name = 'china'
    start_urls = ['https://www.bankofchina.com/aboutboc/bi1/']

    def parse(self, response):
        yield response.follow(response.url, self.parse_page, dont_filter=True)

        pages = int(response.xpath('//div[@class="turn_page"]//span/text()').get())
        current_page = 1

        while current_page <= pages:
            link = f'https://www.bankofchina.com/aboutboc/bi1/index_{current_page}.html'
            yield response.follow(link, self.parse_page)
            current_page += 1

    def parse_page(self, response):
        links = response.xpath('//div[@class="news"]//li/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//p[@class="con_time"]/text()').get()
        if date:
            date = datetime.strptime(date.strip(), '%Y-%m-%d')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@class="sub_con"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[:-2]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
