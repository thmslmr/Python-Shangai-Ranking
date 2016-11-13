# Python-Shangai-Ranking

Dependencies
------------

    pip install beautifulsoup4

Example
-------

    ranking = ShangaiRanking()

    # Get the current Shangai Ranking
    world_current_ranking = ranking.getRanking()

    # Get the 2015 Shangai Ranking in Mathematics
    math_ranking_2015 = ranking.getRanking(2015, 'Mathematics')

    # Get search result for 'Harvard University' and 'China'
    havard_search = ranking.search('Harvard University')
    china_search = ranking.search('China')
