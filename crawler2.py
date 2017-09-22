"""
class NaverWebtoonCrawler생성
    init 메서드
        webtoon_id
        episode_list (빈 list) 를 할당
"""
import os
import requests
import utils
import pickle

#test
class NaverWebtoonCrawler:
    def __init__(self, webtoon_id):
        self.webtoon_id = webtoon_id
        self.episode_list = list()
        # 객체 생성 시, 'db/{webtoon_id}.txt'파일이 존재하면
        # 바로 load() 해오도록 작성
        self.load(init=True)

    @property
    def total_episode_count(self):

        el = utils.get_webtoon_episode_list(self.webtoon_id)
        return int(el[0].no)

    @property
    def up_to_date(self):
        """
        현재 가지고있는 episode_list가 웹상의 최신 episode까지 가지고 있는지
        :return: boolean값
        """

        # 지금 가지고 있는 총 Episode의 개수
        # self.episode_list에 저장되어있음.
        #   -> list형 객체
        #   -> list형 객체의 길이를 구하는 함수(시퀀스형 객체는 모두 가능)
        #   -> 내장함수 len(s)
        ###################################################
        cur_episode_count = len(self.episode_list)
        print(cur_episode_count)
        total_episode_count = self.total_episode_count

        # return cur_episode_count == total_episode_count
        return len(self.episode_list) == self.total_episode_count

    def update_episode_list(self, force_update=False):
        """
        self.episode_list에 존재하지 않는 episode들을 self.episode_list에 추가
        :param force_update: 이미 존재하는 episode도 강제로 업데이트
        :return: 추가된 episode의 수 (int)
        """
        ###############
        # 1. recent_episode_no = self.episode_list에서 가장 최신화의 no
        # 2. while문 또는 for문 내부에서 page값을 늘려가며
        # utils.get_webtoon_episode_list를 호출
        # 반환된 list(episode)들을 해당 episode의 no가
        # recent_episode_no보다 클 때 까지만 self.episode_list에 추가
        ###############

        recent_episode_no = self.episode_list[0].no if self.episode_list else 0

        print('- Update episode list atart ( Recent episode no : %s) - ' % recent_episode_no)
        page = 1
        new_list = list()
        while True:
            print('Get webtoon episode list (Loop %s)' % page)
            # 계속해서 증가하는 'page'를 이용해 다음 episode리스트를 가져옴
            el = utils.get_webtoon_episode_list(self.webtoon_id, page)
            # 가져온 episode list를 순회
            for episode in el:
                # 각 episode의 no가 recent_episode_no보다 클 경우
                # self.episode_list에 추가
                if int(episode.no) > int(recent_episode_no):
                    new_list.append(episode)
                    if int(episode.no) == 1:
                        break
                else:
                    break
            # break가 호출되지 않았을 때
            else:
                # 계속해서 진행해야 하므로 page값을 증가시키고 continue로 처음으로 돌아감
                page += 1
                continue
            # el의 for문에서 break가 호출될 경우(더 이상 추가할 episode없음)
            # while문을 빠져나가기위해 breakt실행

            break

        self.episode_list = new_list + self.episode_list
        # 총 업데이트 된 에피소드 수 리턴
        return len(new_list)

    def get_first_page_episode_list(self):
        el = utils.get_webtoon_episode_list(self.webtoon_id, 99999)
        self.episode_list = el
        return len(self.episode_list)



    def save(self, path=None):
        """
        현재폴더를 기준으로 db/<webtoon_id>.txt 파일에
        pickle로 self.episode_list를 저장

        1. 폴더 생성시
            os.is_dir(path)
                path가 디렉토리인지 확인ㄴ
            os.mkdir(path)
                path가 디렉토리를 생성

        2. 저장시
            pickle.dump(obj, file)

            :return: None
        """
        if not os.path.isdir('db'):
            os.mkdir('db')

        obj = self.episode_list
        path = 'db/%s.txt' % self.webtoon_id
        pickle.dump(obj, open(path, 'wb'))

    def load(self, path=None, init=False):
        """
        현재폴더를 기준으로 db/<webtoon_id>.txt 파일의 내용을 불러와
        pickle로 self.episode_list를 복원
        :return:
        """
        try:
            path = f'db/{self.webtoon_id}.txt'
            # path = 'db/%s.txt' % self.webtoon_id
            self.episode_list = pickle.load(open(path, 'rb'))
        except FileNotFoundError:
            if not init:
                print('파일이 없습니다')

    def save_list_thumbnail(self):
        """
        webtoon/{webtoon_id}_thumbnail/<episode_no>.jpg
        1. webtoon/{webtoon_id}_thumbnail이라는 폴더가 존재하는지 확인 후 생성
        2. self.episode_list를 순회하며 각 episode의 img_url경로의 파일을 저장
        :return: 저장한 thumbnail 개수
        """
        # webtoon/{self.webtoon_id}에 해당하는 폴더 생성
        thumbnail_dir = f'webtoon/{self.webtoon_id}_thumbnail'
        os.makedirs(thumbnail_dir, exist_ok=True)

        # 각 episode의 img_url속성에 해당하는 이미지를 다운로드
        for episode in self.episode_list:
            response = requests.get(episode.img_url)
            filepath = f'{thumbnail_dir}/{episode.no}.jpg'

            if not os.path.exists(filepath):
                with open(filepath, 'wb') as f:
                    f.write(response.content)

    def make_list_html(self):
        '''
        self.episode_list를 HTML파일로 만들어준다.
        webtoon/{webtoon_id}.html

        1. webtoon 폴더 있는지 검사 후 생성
        2. webtoon/{webtoon_id}.html 파일객체 할당 또는 with문으로 open
        3. open한 파일에 html앞부분 작성
        4. episode_list를 for문 돌며 <tr>...</tr> 부분 반복작성
        5. html 뒷부분 작성
        6. 파일닫기 또는 with문 빠져나가기
        7. 해당파일 경로 리턴

        :return:
        '''

        if not os.path.isdir('webtoon'):
            os.mkdir('webtoon')

        filename = f'webtoon/{self.webtoon_id}.html'
        with open(filename, 'wt') as f:
            # HTML 앞부분 작성
            f.write(utils.LIST_HTML_HEAD)

            # episode_list 순회하며 나머지 코드 작성
            for e in self.episode_list:
                f.write(utils.LIST_HTML_TR.format(
                    img_url=f'./{self.webtoon_id}_thumbnail/{e.no}.jpg',
                    title=e.title,
                    rating=e.rating,
                    created_date=e.created_date))

            f.write(utils.LIST_HTML_TAIL)
        return filename


if __name__ == '__main__':

    crawler = NaverWebtoonCrawler(696617)
    crawler.update_episode_list()

    if crawler.up_to_date:
        print('아 업로드 왤케 느린거야 ㅡㅡ')
    else:
        print('최신화 업로드됐다! 업데이트 ㄱㄱ!')
        crawler.update_episode_list()

    crawler.save()
    crawler.save_list_thumbnail()
    crawler.make_list_html()


