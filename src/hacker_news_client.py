import requests
from bs4 import BeautifulSoup

class HackerNewsClient:
    @staticmethod
    def fetch_hackernews_top_stories():
        url = 'https://news.ycombinator.com/'
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功

        soup = BeautifulSoup(response.text, 'html.parser')
        # 查找包含新闻的所有 <tr> 标签
        stories = soup.find_all('tr', class_='athing')

        top_stories = []
        for story in stories:
            title_tag = story.find('span', class_='titleline').find('a')
            if title_tag:
                title = title_tag.text
                link = title_tag['href']
                top_stories.append({'title': title, 'link': link})


        return top_stories

if __name__ == "__main__":
    stories = HackerNewsClient.fetch_hackernews_top_stories()
    if stories:
        for idx, story in enumerate(stories, start=1):
            print(f"{idx}. {story['title']}")
            print(f"   Link: {story['link']}")
    else:
        print("No stories found.")