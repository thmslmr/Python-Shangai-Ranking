# Python-Shangai-Ranking

[Shangai Ranking](http://www.shanghairanking.com/)

Dependencies
------------

    pip install beautifulsoup4

Example
-------
```python
ranking = ShangaiRanking()
# Get the current Shangai Ranking
world_current_ranking = ranking.get()

# Get the 2015 Shangai Ranking in Mathematics
params = {'year' : 2015, 'subject' : 'Mathematics'}
math_ranking_2015 = ranking.get(**params)

# Get the rank of a specified university
params = {'university' : 'Harvard University'}
harvard_university = ranking.get(**params)

# Get search result for 'Harvard University' and 'China'
havard_search = ranking.search('Harvard University')
china_search = ranking.search('China')
```
