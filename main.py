import bs4, json
import urllib.request as ur
from datetime import date

class ShangaiRanking :

    domain = 'http://www.shanghairanking.com/'
    subjects = ['Mathematics' , 'Physics', 'CS', 'EcoBus', 'Chemistry']

    def __init__(self) :
        return

    def save(self, datas, output_file='output.json') :
        with open(output_file, 'w', encoding='utf8') as file :
            json.dump(datas, file, ensure_ascii=False)

    def getRanking(self, year=str(date.today().year), subject = None, save = False) :
        output = []
        if subject :
            if subject in self.subjects :
                url = self.domain + 'Subject' + subject + str(year) + '.html'
            else :
                raise ValueError('Subject does not exist')
        else :
            url = self.domain + 'ARWU' + str(year) + '.html'

        try :
            html = ur.urlopen(url).read()
        except ur.HTTPError :
            raise ValueError('HTTP Error, The current year or the specified one is probably not available.')

        soupe = bs4.BeautifulSoup(html, 'html.parser')
        table = soupe.find('table', {'id' :'UniversityRanking'})

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

        raws_datas = soupe.findAll('tr', {'class' : 'bgfd'})

        for raw in raws_datas :
            university = {}
            cases_datas = raw.findAll('td')

            for i, key in enumerate(legend) :
                university[key] = cases_datas[i].text
                if 'Country' in key :
                    country_src_img = cases_datas[2].find('img')['src']
                    split_src = country_src_img.split('/')
                    country_name = split_src[ len(split_src) - 1 ].split('.')[0]
                    university[key] = country_name

            output.append(university)

        if save :
            self.save(output)
        return output
