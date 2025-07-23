def get_trailer_url(movie_id: int) -> dict:
    """
    Request:
    Url = https://hdrezka320fkk.org/engine/ajax/gettrailervideo.php
    Method = POST
    Content-type = multipart/form-data
    Body: id=65407
    Response example:
    {
        "success": true,
        "message": "Возникла неизвестная ошибка",
        "code": "<iframe width=\"640\" height=\"360\" src=\"https://www.youtube.com/embed/jZZvQvqWiao?iv_load_policy=3&modestbranding=1&hd=1&rel=0&showinfo=0&autoplay=1\" frameborder=\"0\" allow=\"accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen style=\"background: transparent; position: relative;\"></iframe>",
        "title": "&laquo;Меч короля&raquo; <small>(оригинальное название: \"Bastarden / The Promised Land\", 2023)</small>",
        "description": "Датский король отправляет своего лучшего рыцаря обуздать дикие земли, покуда простирается его длань. Но здесь, за стенами высоких замков, свои законы. Местные князья не спешат подчиняться королевскому наместнику. Они сами решают, кто будет возделывать их земли, а кто упокоится в них навсегда. Конфликт усугубляет прекрасная дева, обещанная отцом местному феодалу. Оставить её — значит потерять честь. Спасти — обречь себя на верную гибель. Но там, где опытный политик отступает, истинный рыцарь обнажает меч.",
        "link": "https://hdrezka320fkk.org/films/drama/65407-mech-korolya-2023.html"
    }
    """
    raise NotImplementedError


def get_quick_content(movie_id: int) -> dict:
    """
    Request:
    Url = https://hdrezka320fkk.org/engine/ajax/quick_content.php
    Method = POST
    Content-type = multipart/form-data
    Body: id=65415&is_touch=1
    Response example:
    <div class="b-content__catlabel films">
        <i class="entity">Фильм</i>
        <i class="icon"></i>
    </div>
    <div class="b-content__bubble_title">
        <a href="https://hdrezka320fkk.org/films/thriller/65415-sredi-volkov-2023.html">Среди волков</a>
    </div>
    <div class="b-content__bubble_rating">
        <span class="label">Рейтинг фильма:</span>
        <b>5.35</b>
        (23)

        <span class="b-rating">
            <span class="current" style="width: 53.5%;"></span>
        </span>
    </div>
    <div class="b-content__bubble_text">Брат и сестра, не видевшие друг друга много лет, оказываются вовлеченными в одно и то же ограбление по разные стороны баррикад: она — в качестве офицера полиции, он — в качестве преступника. Старые раны вновь напомнят о себе, брату и сестре придется сделать...
        </div>
    <div class="b-content__bubble_text">
        <span class="label">Жанр:</span>
        <a href="https://hdrezka320fkk.org/films/thriller/">Триллеры</a>
        , <a href="https://hdrezka320fkk.org/films/drama/">Драмы</a>
        , <a href="https://hdrezka320fkk.org/films/crime/">Криминал</a>
        , <a href="https://hdrezka320fkk.org/films/foreign/">Зарубежные</a>
    </div>
    <div class="b-content__bubble_str">
        <span class="label">Режиссер:</span>
        <span class="person-name-item" itemprop="director" itemscope itemtype="http://schema.org/Person" data-id="242583" data-pid="65415">
            <a href="https://hdrezka320fkk.org/person/242583-lida-patituchchi/" itemprop="url">
                <span itemprop="name">Лида Патитуччи</span>
            </a>
        </span>
    </div>
    <div class="b-content__bubble_str">
        <span class="label">В ролях:</span>
        <span class="person-name-item" itemprop="actor" itemscope itemtype="http://schema.org/Person" data-id="33559" data-pid="65415">
            <a href="https://hdrezka320fkk.org/person/33559-izabella-ragoneze/" itemprop="url">
                <span itemprop="name">Изабелла Рагонезе</span>
            </a>
        </span>
        ,
        <span class="person-name-item" itemprop="actor" itemscope itemtype="http://schema.org/Person" data-id="189264" data-pid="65415">
            <a href="https://hdrezka320fkk.org/person/189264-andrea-arkandzheli/" itemprop="url">
                <span itemprop="name">Андреа Арканджели</span>
            </a>
        </span>
        ,
        <span class="person-name-item" itemprop="actor" itemscope itemtype="http://schema.org/Person" data-id="431520" data-pid="65415">
            <a href="https://hdrezka320fkk.org/person/431520-karolina-mikelandzheli/" itemprop="url">
                <span itemprop="name">Каролина Микеланджели</span>
            </a>
        </span>
        ,
        <span class="person-name-item" itemprop="actor" itemscope itemtype="http://schema.org/Person" data-id="431521" data-pid="65415">
            <a href="https://hdrezka320fkk.org/person/431521-aleksandr-gavranich/" itemprop="url">
                <span itemprop="name">Александр Гавранич</span>
            </a>
        </span>
        ,
        <span class="person-name-item" itemprop="actor" itemscope itemtype="http://schema.org/Person" data-id="229103" data-pid="65415">
            <a href="https://hdrezka320fkk.org/person/229103-gennaro-di-colandrea/" itemprop="url">
                <span itemprop="name">Gennaro Di Colandrea</span>
            </a>
        </span>
        ,
        <span class="person-name-item" itemprop="actor" itemscope itemtype="http://schema.org/Person" data-id="383321" data-pid="65415">
            <a href="https://hdrezka320fkk.org/person/383321-klara-posnett/" itemprop="url">
                <span itemprop="name">Клара Поснетт</span>
            </a>
        </span>
        ,
        <span class="person-name-item" itemprop="actor" itemscope itemtype="http://schema.org/Person" data-id="9111" data-pid="65415">
            <a href="https://hdrezka320fkk.org/person/9111-klara-ponso/" itemprop="url">
                <span itemprop="name">Клара Понсо</span>
            </a>
        </span>
        ,
        <span class="person-name-item" itemprop="actor" itemscope itemtype="http://schema.org/Person" data-id="113572" data-pid="65415">
            <a href="https://hdrezka320fkk.org/person/113572-alan-katich/" itemprop="url">
                <span itemprop="name">Алан Катич</span>
            </a>
        </span>
        ,
        <span class="person-name-item" itemprop="actor" itemscope itemtype="http://schema.org/Person" data-id="57995" data-pid="65415">
            <a href="https://hdrezka320fkk.org/person/57995-milosh-timotievich/" itemprop="url">
                <span itemprop="name">Милош Тимотиевич</span>
            </a>
        </span>
        и
        <span class="person-name-item" itemprop="actor" itemscope itemtype="http://schema.org/Person" data-id="431522" data-pid="65415">
            <a href="https://hdrezka320fkk.org/person/431522-gabriele-portogeze/" itemprop="url">
                <span itemprop="name">Габриэле Портогезе</span>
            </a>
        </span>
    </div>
    <div class="b-content__bubble_rates">
        <span class="imdb">
            IMDb: <b>6.4</b>
            <i>(273)</i>
        </span>
    </div>
    """
    raise NotImplementedError
