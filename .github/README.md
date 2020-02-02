# \_boostertutor

## Current Status

![Twitter](https://github.com/brokenthumbs/_boostertutor/workflows/Twitter/badge.svg)

## Trigger

Currently set on a `schedule: cron: '* * * * *'`.

`repository_dispatch` uses the following `curl` to trigger:
```
curl --verbose -X POST -u "brokenthumbs:${GITHUB_PAT}" \
-H "Accept: application/vnd.github.everest-preview+json"  \
-H "Content-Type: application/json" \
https://api.github.com/repos/brokenthumbs/_boostertutor/dispatches \
--data '{"event_type": "dispatch"}'
```

## Notes

- Using booster pack format of 10 commons, 3 uncommons, and 1 rare or mythic for all editions. Upgrade to this script could adapt returning different numbers and combinations of cards for different editions.

## Links

- http://docs.tweepy.org/en/latest/extended_tweets.html
- https://developer.github.com/v3/activity/events/types/#repositorydispatchevent
- https://developer.github.com/v3/repos/#create-a-repository-dispatch-event
- https://developer.twitter.com/en/apps
- https://docs.python.org/3/library/pprint.html
- https://github.com/bear/python-twitter
- https://github.community/t5/GitHub-Actions/repository-dispatch-not-triggering-actions/td-p/33817#
- https://help.github.com/en/actions/automating-your-workflow-with-github-actions/configuring-a-workflow
- https://help.github.com/en/actions/automating-your-workflow-with-github-actions/creating-and-using-encrypted-secrets
- https://help.github.com/en/actions/automating-your-workflow-with-github-actions/events-that-trigger-workflows#external-events-repository_dispatch
- https://help.github.com/en/actions/automating-your-workflow-with-github-actions/using-python-with-github-actions
- https://help.github.com/en/actions/automating-your-workflow-with-github-actions/workflow-syntax-for-github-actions#jobs
- https://mtg.gamepedia.com/Booster_pack
- https://requests.readthedocs.io/en/master/user/quickstart/
- https://scryfall.com/docs/api/cards/random
- https://scryfall.com/docs/syntax
- https://stackoverflow.com/a/50542155
- https://stackoverflow.com/a/8569258
- https://stackoverflow.com/questions/22974772/querystring-array-parameters-in-python-using-requests
- https://stackoverflow.com/questions/5607551/how-to-urlencode-a-querystring-in-python

## Scrap

```
# https://scryfall.com/search?q=%28set%3Athb+%21%22Nylea%27s+Forerunner%22%29+or+%28set%3Athb+%21%22Bronze+Sword%22%29&as=grid&order=set
# https://scryfall.com/search?q=%28set%3Athb+%21%22Nylea%27s+Forerunner%22%29+or+%28set%3Athb+%21%22Bronze+Sword%22%29
# https://scryfall.com/search?q=edition%3Athb+rarity%3Acommon+-type%3Aland+%21%22Hyrax+Tower+Scout%22+

payload = {
  'q': [ f" \
    edition:{edition} \
    rarity:{rarity} \
    !\"Bronze Sword\" \
  "]
}

export TWITTER_ACCESS_TOKEN=
export TWITTER_ACCESS_TOKEN_SECRET=
export TWITTER_CONSUMER_KEY=
export TWITTER_CONSUMER_SECRET=

```

## ToDo
