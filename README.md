# SongMind

## What is SongMind?
This is a project to organize local copies of mp3 and recommand new songs.

## How to use?

- git clone and cd to this repo.
- edit `config/config.yml` per your preference.
- run `python app_Organizer.py` in the current directory to organizer songs.
- run `python app_NewTunes.py` in the current directory to get new songs.


## Organizer

- Place your music folder in the current directory.
- Running `app_Organizer.py` will make a copy of the music under `./Copy` and sort them according to language first and then by genre if the language is English.

## NewTunes
A web scraper that grabs new music titles from around the world from targeted music charts. Focus on getting new songs and songs that entered the desired position. It will generate a csv file (artist, title) with no duplications across charts and entries from the previous run.

Currently support table styles from following music charts:
- [billboard](https://www.billboard.com/charts/hot-100)
- [officialcharts](https://www.officialcharts.com/charts/singles-chart/)
- [euro200](https://euro200.net/)
- [tophit](https://tophit.ru/ru/chart/airplay_youtube/weekly/current/rus/new)
- [hitlisten](http://hitlisten.nu/default.asp?list=t40)
- [dutchcharts](https://dutchcharts.nl/weekchart.asp?cat=s)
- [acharts](https://acharts.co/france_singles_top_100)
- [ariacharts](https://www.ariacharts.com.au/charts/singles-chart)
- [mediaforest](http://www.mediaforest.ro/weeklycharts/HistoryWeeklyCharts.aspx)
- [shazam](https://www.shazam.com/charts/top-200/romania)

## Contribute
Feel free to add more chart sources with the corresponding scraper method.
- Add your class in sites/
- Add the corresponding information in charts.py 
- Could use help for http://www.radiomirchi.com
- adding test

## Logs

- Check error.log log and info.log for more details.

## Requirement

1. Install python
2. Install packages in the requirement.txt
3. You will need to get the keys for each of the apis in the config/config.yml. They are all free to use.

## Known Issues:
1. Language is classified using polyglot, google translate, and detectlanguage. While it works pretty well most of the time, it is not guaranteed to work perfectly.
2. Genres are defined using the LastFM API and Spotify API. Tags are not standardized and one might see unexpected genres.

## License
See the license file.