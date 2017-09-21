import pickle
import requests


from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup
from utils import Episode
#
# NamedTuple(Episode) 을 사용해서
#   이미지 주소(img_url)
#   에피소드 제목(title)
#   에피소드 별점(rating)
#   에피소드 등록일(created_date)
# 를 가지는 NamedTuple의 리스트를 생성

# webtoon id를 입력받아 해당 웹툰의 첫 번째 페이지에 있는 episode리스트를 리턴하는 함수를 구현
# requests를 사용!
webtoon_yumi = 651673
webtoon_denma = 119874

def get_webtoon_episode_list(webtoon_id, page=1):
    """
    특정 page의 episode 리스트를 리턴하도록 리팩토링
    :param webtoon_id: 웹툰 고유 ID
    :param page: 가져오려는 Episode list 페이지
    :return: list(Episode)
    """
    # webtoon_url을 기반으로 특정 웹툰의 리스트페이지 내용을 가져와 soup객체에 할당
    webtoon_list_url = 'http://comic.naver.com/webtoon/list.nhn'
    params = {
        'titleId': webtoon_id,
        'page': page,
    }
    response = requests.get(webtoon_list_url, params=params)
    soup = BeautifulSoup(response.text, 'lxml')

    # 필요한 데이터들 (img_url, title, rating, created_date)추출
    episode_list = list()
    webtoon_table = soup.select_one('table.viewList')


    tr_list = webtoon_table.find_all('tr', recursive=False)
    for tr in tr_list:
        td_list = tr.find_all('td')
        if len(td_list) < 4:
            continue
        td_thumbnail = td_list[0]
        td_title = td_list[1]
        td_rating = td_list[2]
        td_created_date = td_list[3]

        # Episode고유의 no
        url_episode = td_thumbnail.a.get('href')
        parse_result = urlparse(url_episode)
        queryset = parse_qs(parse_result.query)
        no = queryset['no'][0]
        # td_thumbnail에 해당하는 Tag의 첫 번째 a tag의 첫 번째 img태그의 'src'속성값
        img_url = td_thumbnail.a.img.get('src')
        # td_title tag의 내용을 좌우여백 잘라냄
        title = td_title.get_text(strip=True)
        # td_rating내의 strong태그내의 내용을 좌우여백 잘라냄
        rating = td_rating.strong.get_text(strip=True)
        # td_title과 같음
        created_date = td_created_date.get_text(strip=True)

        # Episode형 namedtuple객체 생성, episode_list에 추가
        episode = Episode(
            no=no,
            img_url=img_url,
            title=title,
            rating=rating,
            created_date=created_date
        )
        episode_list.append(episode)

    return episode_list



def save_episode_list_to_file(webtoon_id, episode_list):
    """
    episode_list로 전달된 Episode의 리스트를
    쉼표단위로 속성을 구분, 라인단위로 episode를 구분해 저장
    파일명은 <webtoon_id>_<가장 최근 에피소드no>_<가장 나중 에피소드no>.txt
    ex) 651673_1070_1050.txt
    ex)
    1070,http://...jpg,109화 - 무언가,9.93,2017.09.13
    1069,http://...jpg,109화 - 무언가,9.93,2017.09.13
    1068,http://...jpg,109화 - 무언가,9.93,2017.09.13
    1067,http://...jpg,109화 - 무언가,9.93,2017.09.13
    :param episode_list: Episode namedtuple의 list
    :param webtoon_id: 웹툰 고유 ID값 (str또는 int)
    :return:
    """
    filename = '{webtoon_id}_{first_episode_no}_{last_episode_no}.txt'.format(
        webtoon_id=webtoon_id,
        # episode_list의 0번째 Episode의 no속성
        first_episode_no=episode_list[0].no,
        # episode_list의 마지막 Episode의 no속성
        last_episode_no=episode_list[-1].no,
    )
    # 위에서 작성한 <webtoon_id>_<first_episode_no>_<last_episode_no>.txt파일에 작성
    with open(filename, 'wt') as f:
        # 각 Episode를 순회하며 각 line에 해당하는 문자열을 생성, 기록
        for episode in episode_list:
            f.write('|'.join(episode) + '\n')


def load_episode_list_from_file(path):
    """
    path에 해당하는 file을 읽어 Episode리스트를 생성해 리턴
    1. file객체 f할당
    2. readline()함수를 이용해 한줄씩 읽기 <- 다른방법도 있습니다
    3. 한줄을 '|'단위로 구분해서 Episode객체 생성
    4. 객체들을 하나의 리스트에 담아 리턴
    :param path:
    :return:
    """
    with open(path, 'rt') as f:
        # String 객체의 메서드 strip은 문자열 양쪽의 공백을 지운다.
        # 공백을 지운 후 '|'로 나누어 다시 저장한다.
        # collections.namedtuple의
        # _make 함수는 기존에 생성된 namedtuple()에 새로운 인스턴스를 생성하는 메소드
        # 즉, Episode namedtuple(class라고 생각하면 쉽다.)의 인스턴스를 하나 더 생성
        episode_list = list()
        for line in f:
            episode_list.append(Episode._make(line.strip().split('|')))
        return episode_list

        # return [Episode._make(line.strip().split('|')) for line in f]





el = get_webtoon_episode_list(webtoon_yumi)
# print(el)
# pickle.dump(el, open('yumi_pickle.txt', 'wb'))

# el = pickle.load(open('yumi_pickle.txt', 'rb'))
# print(el)


save_episode_list_to_file(webtoon_yumi, el)
print(load_episode_list_from_file('651673_251_242.txt'))
