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
    params = {'year' : 2015, 'subject' : 'Mathematics'}
    math_ranking_2015 = ranking.getRanking(params)

    # Get the rank of a specified university
    params = {'university' : 'Harvard University'}
    harvard_university = ranking.getRanking(params)

    # Get search result for 'Harvard University' and 'China'
    havard_search = ranking.search('Harvard University')
    china_search = ranking.search('China')
