import bs4, json
import urllib.request as ur
from datetime import date

class ShangaiRanking :

    settings_file = 'settings.json'
    settings = None

    def __init__(self) :
        self.settings = self.getSettings()

    def save(self, datas, output_file='output.json') :
        with open(output_file, 'w', encoding='utf8') as file :
            json.dump(datas, file, ensure_ascii=False)

    def getSettings(self) :
        with open(self.settings_file , encoding='utf8') as file :
            settings = json.load(file)
        return settings

    def getRanking(self, year = date.today().year, subject = None, save = False) :
        output = []
        domain = self.settings['domain']
        subjects = self.settings['subjects']

        if subject :
            output = self.getSubjectRanking(subject, year)
        else :
            output = self.getGlobalRanking(year)

        if save :
            self.save(output)

        return output

    def getGlobalRanking(self, year) :

        pattern_url = self.settings['pattern_world_ranking']
        url = pattern_url.replace('<domain>', self.settings['domain']).replace('<year>', str(year) )

        try :
            html = ur.urlopen(url).read()
        except ur.HTTPError :
            raise ValueError('HTTP Error, The current year or the specified one is probably not available.')

        soupe = bs4.BeautifulSoup(html, 'html.parser')
        table = soupe.find('table', {'id' :'UniversityRanking'})
        return self.getRankingWithTable(table, self.settings['ranking_tr_class'])

    def getSubjectRanking(self, subject, year):

        if subject not in self.settings['subjects'] :
            raise ValueError('This subject does not exist')

        url_pattern = self.settings['pattern_subject_ranking']
        url = url_pattern.replace('<domain>', self.settings['domain']).replace('<subject>', subject).replace('<year>', str(year))

        try :
            html = ur.urlopen(url).read()
        except ur.HTTPError :
            raise ValueError('HTTP Error, The current year or the specified one is probably not available.')

        soupe = bs4.BeautifulSoup(html, 'html.parser')
        table = soupe.find('table', {'id' : self.settings['ranking_table_id']})
        return self.getRankingWithTable(table, self.settings['ranking_tr_class'])

    def getRankingWithTable(self, table, target_class) :
        output = []
        legend = []
        raw_legend = table.find('tr')

        for case_legend in raw_legend.findAll('th'):
            if case_legend.find('select') :
                options = case_legend.findAll('option')
                for option in options :
                    legend.append(option.text)
            else :
                text = case_legend.text.replace('\n', '').strip()
                legend.append(' '.join(text.split()))

        raws_datas = table.findAll('tr', {'class' : target_class})

        for raw in raws_datas :
            university = {}
            cases_datas = raw.findAll('td')

            for i, key in enumerate(legend) :
                try :
                    university[key] = cases_datas[i].text
                except IndexError :
                    pass
                if 'Country' in key :
                    country_src_img = cases_datas[2].find('img')['src']
                    split_src = country_src_img.split('/')
                    country_name = split_src[ len(split_src) - 1 ].split('.')[0]
                    university[key] = country_name
            print(university)
            output.append(university)

        return output

    def search(self, query) :
        if not query :
            raise ValueError('Search query must be specified')

        result = []
        url_pattern = self.settings['pattern_search_university']
        url = url_pattern.replace('<domain>', self.settings['domain']).replace('<query>', query.replace(' ', '+'))

        try :
            html = ur.urlopen(url).read()
        except ur.HTTPError :
            raise ValueError('HTTP Error, page not found')

        soupe = bs4.BeautifulSoup(html, 'html.parser')
        raws = soupe.findAll('tr', {'class' : self.settings['search_tr_class']})
        if(len(raws) > 0 ):
            for raw in raws :
                result.append( raw.findAll('td')[0].text )

        return result
