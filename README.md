# SongMind

## What is SongMind?
This is a project to organize local copies of mp3.
1. It sorts a user's music into different folders by language or genre.
2. It collects data related to the songs in those folders and stores them in a database.
3. It analyzes what makes these songs appeal to the users.

## How to use?

- git clone and cd to this repo.
- edit `config/config.yml` per your preference.
- run `python sort.py` in the current directory.


## Operations

- Place your music folder in the current directory.
- Running `sort.py` will make a copy of the music under `./Copy` and sort them according to language first and then by genre if the language is English.

## Logs

- Check error.log log and info.log for more details.

## Requirement

1. Install python
2. Install packages in the requirement.txt

## Known Issues:
1. Language is classified using polyglot. While it works pretty well most of the time, it does misclassify songs.
2. Genres are defined using the LastFM API. Tags are not standardized and one might see unexpected genres.
