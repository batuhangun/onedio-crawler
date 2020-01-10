import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta
import re

date_dict = {"Ocak": "01", "Şubat": "02", "Mart": "03",
             "Nisan": "04", "Mayıs": "05", "Haziran": "06", "Temmuz": "07", "Ağustos": "08", "Eylül": "09",
             "Ekim": "10", "Kasım": "11", "Aralık": "12"}


class OnedioCrawler:
    url = "https://onedio.com/ara/haber/"
    sort = "?sort=updated%20desc"

    def share(self, sharetext):  # eskiden postlarda paylaşım sayıları vardı

        pat = re.compile(r"(\d+(\.\d+)?)([a-z])")
        reg = pat.match(sharetext)

        if reg:
            if reg.groups()[1]:
                return int(reg.groups()[0][0]) * 1000 + int(reg.groups()[1][1]) * 100
            else:
                return int(reg.groups()[0]) * 1000
        else:
            return int(sharetext)

    def time(self, timetext):
        f = "%d %m %Y %H:%M"
        timetext = timetext[:8] + " " + str(datetime.utcnow().year) + timetext[8:]
        timetext_list = timetext.split()
        try:
            timetext_list[1] = date_dict[timetext_list[1].replace(",", "")]
        except:
            return None

        return datetime.strptime(" ".join(timetext_list), f)

    def crawler(self, keyword, min_datetime=None):

        r = requests.get("{0}{1}{2}".format(self.url, keyword, self.sort))
        soup = bs(r.text, "html.parser")
        posts = []
        for item in soup.select(".common-horizontal"):
            post = {}

            timetext = item.select("div.content time")[0].text
            posttime = self.time(timetext)
            if not posttime: continue
            min_timestamp = min_datetime.timestamp() - 900
            if min_timestamp > datetime.timestamp(posttime): break

            post['date'] = posttime
            post["title"] = item.select("h3")[0].text
            post["url"] = "{0}{1}".format("https://onedio.com",
                                          item.select("a:nth-of-type({})".format(len([i for i in item.select("a")])))
                                          [0]["href"])

            post["content"] = item.select("div.content p")[0].text if len(item.select("div.content p")) else " "

            posts.append(Onedio(**post))

        return posts


class Onedio:

    def __init__(self, title, content, date, url):
        self.title = title
        self.content = content
        self.date = date
        self.url = url


if __name__ == "__main__":
    items = OnedioCrawler().crawler("aşk", min_datetime=datetime.utcnow() - timedelta(days=11111))
    for item in items: print(item.__dict__)
