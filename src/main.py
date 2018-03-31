import bs4
import json
from urllib.request import urlopen, HTTPError
from datetime import date


class ShangaiRanking:

    def __init__(self):
        """ Init Shangai Ranking """
        self.__set_settings()

    def __set_settings(self):
        """ Get settings from settings.json """
        try:
            with open('settings.json', encoding='utf8') as file:
                settings = json.load(file)
        except FileNotFoundError as e:
            raise Exception('Settings file must be provided')

        if not settings:
            raise Exception('Settings file must be filled')

        self.settings = settings

    def __get_settings(self, keys=None):
        """ Get settings for given keys or all"""
        return (self.settings[key] for key in keys or self.settings.keys())

    def __get_url(self, pattern, keys=[]):
        """ Get url from pattern and match keys """
        if not pattern:
            raise Exception('URL pattern must be provided.')

        url = pattern
        for key in keys:
            url = url.replace('<{0}>'.format(key), keys[key])

        return url

    def __get_bsoupe(self, url):
        """ Get soupe from html of a given url """
        try:
            html = urlopen(url).read()
        except HTTPError:
            raise Exception('HTTP Error, page not found')

        return bs4.BeautifulSoup(html, 'html.parser')

    def __get_ranking_from_table(self, table, target_class):
        """ Scrap ranking from table html element """
        if not table:
            raise Exception('Table element must be provided.')
        if not target_class:
            raise Exception('Target class must be provided.')

        output = []
        legend = []
        raw_legend = table.find('tr')
        raws_datas = table.findAll('tr', {'class': target_class})

        for case_legend in raw_legend.findAll('th'):
            if case_legend.find('select'):
                options = case_legend.findAll('option')
                for option in options:
                    legend.append(option.text)
            else:
                text = case_legend.text.replace('\n', '').strip()
                legend.append(' '.join(text.split()))

        for raw in raws_datas:
            university = {}
            cases_datas = raw.findAll('td')

            for i, key in enumerate(legend):
                try:
                    university[key] = cases_datas[i].text
                except IndexError:
                    pass

                if 'Country' in key:
                    country_src_img = cases_datas[2].find('img')['src']
                    split_src = country_src_img.split('/')
                    country_name = split_src[len(split_src) - 1].split('.')[0]
                    university[key] = country_name

            output.append(university)

        return output

    def __get_university_ranking(self, univ):
        """ Get ranking of a given univeristy """
        if not univ:
            raise Exception('University name must be provided.')

        (url_pattern, domain, tr_class) = self.__get_settings([
            'pattern_university',
            'domain',
            'ranking_tr_class'])

        univ = univ.replace(' ', '-')
        url = self.__get_url(url_pattern, {'domain': domain,
                                           'univeristy': univ})
        soupe = self.__get_bsoupe(url)
        tables = soupe.findAll('table')[1:]

        output = {}
        for table in tables:
            years = []

            for th in table.findAll('th'):
                years.append(th.text)
            years = years[1:]

            for tr in table.findAll('tr')[1:]:
                ranks = []
                for td in tr.findAll('td'):
                    if td.text == '/':
                        ranks.append(None)
                    else:
                        ranks.append(td.text)
                key = ranks[0].replace(' ', '_')
                ranks = ranks[1:]
                output[key] = dict(zip(years, ranks))

        return output

    def __get_ranking(self, year):
        """ Get global Shangai Ranking """
        if not year:
            raise Exception('Year must be provided.')

        (url_pattern, domain, tr_class) = self.__get_settings([
            'pattern_world_ranking',
            'domain',
            'ranking_tr_class'])

        url = self.__get_url(url_pattern, {'domain': domain, 'year': year})
        soupe = self.__get_bsoupe(url)
        table = soupe.find('table', {'id': 'UniversityRanking'})

        return self.__get_ranking_from_table(table, tr_class)

    def __get_subject_ranking(self, subject, year):
        """ Get Shangai Ranking for a given subject """
        if not year:
            raise Exception('Year must be provided.')

        if subject not in self.__get_settings(['settings']):
            raise Exception('This subject does not exist')

        (subjects, url_pattern,
         domain, tr_class, table_id) = self.__get_settings([
            'subjects',
            'pattern_subject_ranking',
            'domain',
            'ranking_tr_class',
            'ranking_table_id'])

        url = self.__get_url(url_pattern, {'domain': domain,
                                           'subject': subject,
                                           'year': year})
        soupe = self.__get_bsoupe(url)
        table = soupe.find('table', {'id': table_id})

        return self.__get_ranking_from_table(table, tr_class)

    def search(self, query):
        """ Search ranking of a given univeristy """
        if not query:
            raise Exception('Search query must be provided.')

        (url_pattern, domain, tr_class) = self.__get_settings([
            'pattern_search_university',
            'domain',
            'search_tr_class'])

        query = query.replace(' ', '+')
        url = self.__get_url(url_pattern, {'domain': domain, 'query': query})
        soupe = self.__get_bsoupe(url)
        raws = soupe.findAll('tr', {'class': tr_class})

        result = []
        if raws:
            for raw in raws:
                result.append(raw.findAll('td')[0].text)

        return result

    def get(self,
            subject=None,
            university=None,
            year=date.today().year):
        """ Main function """
        if subject:
            output = self.__get_subject_ranking(subject, str(year))
        elif university:
            output = self.__get_university_ranking(university)
        else:
            output = self.__get_ranking(str(year))

        return output
