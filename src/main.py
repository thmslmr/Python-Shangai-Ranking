import bs4
import json
import urllib.request as ur
from datetime import date


class ShangaiRanking:

    def __init__(self):
        """ Init Shangai Ranking """
        self.set_settings()

    def set_settings(self):
        """ Get settings from settings.json """
        try:
            with open('settings.json', encoding='utf8') as file:
                settings = json.load(file)
        except FileNotFoundError as e:
            raise Exception('Settings file must be provided')

        if not settings:
            raise Exception('Settings file must be filled')

        self.settings = settings

    def get_settings(self, keys=None):
        """ Get settings for given keys or all"""
        return (self.settings[key] for key in keys or self.settings.keys())

    def get_url(self, pattern, keys):
        """ Get url from pattern and match keys """
        url = pattern

        for key in keys:
            url = url.replace('<{key}>', keys[key])

        return url

    def get_bsoupe(self, url):
        """ Get soupe from html of a given url """
        try:
            html = ur.urlopen(url).read()
        except ur.HTTPError:
            raise Exception('HTTP Error, page not found')

        return bs4.BeautifulSoup(html, 'html.parser')

    def get_ranking_from_table(self, table, target_class):
        output = []
        legend = []
        raw_legend = table.find('tr')

        for case_legend in raw_legend.findAll('th'):
            if case_legend.find('select'):
                options = case_legend.findAll('option')
                for option in options:
                    legend.append(option.text)
            else:
                text = case_legend.text.replace('\n', '').strip()
                legend.append(' '.join(text.split()))

        raws_datas = table.findAll('tr', {'class': target_class})

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

    def get(self,
            subject=None,
            university=None,
            year=date.today().year):
        """ Main function """
        if subject:
            output = self.get_subject_ranking(subject, str(year))
        elif university:
            output = self.get_university_ranking(university)
        else:
            output = self.get_ranking(str(year))

        return output

    def get_university_ranking(self, univ):
        """ Get ranking of a given univeristy """
        (url_pattern, domain, tr_class) = self.get_settings([
            'pattern_university',
            'domain',
            'ranking_tr_class'])

        if not univ:
            raise Exception('University name must be provided.')

        univ = univ.replace(' ', '-')
        url = self.get_url(url_pattern, {'domain': domain, 'univeristy': univ})
        soupe = self.get_bsoupe(url)
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

    def get_ranking(self, year):
        """ Get global Shangai Ranking """
        (url_pattern, domain, tr_class) = self.get_settings([
            'pattern_world_ranking',
            'domain',
            'ranking_tr_class'])

        if not year:
            raise Exception('Year must be provided.')

        url = self.get_url(url_pattern, {'domain': domain, 'year': year})
        soupe = self.get_bsoupe(url)
        table = soupe.find('table', {'id': 'UniversityRanking'})

        return self.get_ranking_from_table(table, tr_class)

    def get_subject_ranking(self, subject, year):
        """ Get Shangai Ranking for a given subject """
        (subjects, url_pattern,
         domain, tr_class, table_id) = self.get_settings([
            'subjects',
            'pattern_subject_ranking',
            'domain',
            'ranking_tr_class',
            'ranking_table_id'])

        if subject not in subjects:
            raise Exception('This subject does not exist')

        url = self.get_url(url_pattern, {'domain': domain, 'subject': subject,
                                         'year': year})
        soupe = self.get_bsoupe(url)
        table = soupe.find('table', {'id': table_id})

        return self.get_ranking_from_table(table, tr_class)

    def search(self, query):
        """ Search ranking of a given univeristy """
        (url_pattern, domain, tr_class) = self.get_settings([
            'pattern_search_university',
            'domain',
            'search_tr_class'])

        if not query:
            raise Exception('Search query must be provided.')

        query = query.replace(' ', '+')
        url = self.get_url(url_pattern, {'domain': domain, 'query': query})
        soupe = self.get_bsoupe(url)
        raws = soupe.findAll('tr', {'class': tr_class})

        result = []
        if raws:
            for raw in raws:
                result.append(raw.findAll('td')[0].text)

        return result
