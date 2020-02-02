from datetime import datetime
import os
import pprint
import re
import requests
import sys
import time
import tweepy
import urllib

pp = pprint.PrettyPrinter(indent=4)
requests_per_second = 5
mentions_timeline_count = 10

# setup twitter api
TWITTER_SCREEN_NAME = os.environ.get("TWITTER_SCREEN_NAME", "_boostertutor")
TWITTER_CONSUMER_KEY = os.environ.get("TWITTER_CONSUMER_KEY", "")
TWITTER_CONSUMER_SECRET = os.environ.get("TWITTER_CONSUMER_SECRET", "")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET", "")

tweepy_auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
tweepy_auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
tweepy_api = tweepy.API(tweepy_auth)

# get the last_processed_timestamp
twitter_user = tweepy_api.get_user(screen_name=TWITTER_SCREEN_NAME)
last_processed_timestamp = twitter_user.description.split(':', 1)[1].strip()
print(f"last_processed_timestamp: {last_processed_timestamp}")
t1 = datetime.strptime(last_processed_timestamp, "%a %b %d %H:%M:%S %z %Y")

# gather all unprocessed mentions since last_processed_timestamp
unprocessed_requests = []
oldest_id = ""
oldest_id_found = False
while not oldest_id_found:
  if not oldest_id:
    mentions = tweepy_api.mentions_timeline(count=mentions_timeline_count, tweet_mode="extended")
    if not mentions:
      oldest_id_found = True
      break
  else:
    mentions = tweepy_api.mentions_timeline(count=mentions_timeline_count, max_id=oldest_id, tweet_mode="extended")
    if length(mentions) <= mentions_timeline_count:
      oldest_id_found = True
      break
  for mention in mentions:
    tweet_created_at = mention._json["created_at"]
    tweet_favorited = mention._json["favorited"]
    tweet_id = mention._json["id"]
    tweet_screen_name = mention._json["user"]["screen_name"]
    tweet_full_text = mention._json["full_text"]
    oldest_id = tweet_id
    try:
      mention.retweeted_status.full_text
      print(f"https://twitter.com/_/status/{tweet_id} - skipping, status is a retweet")
    except AttributeError:
      t2 = datetime.strptime(tweet_created_at, "%a %b %d %H:%M:%S %z %Y")
      if max((t1, t2)) == t1:
        print(f"https://twitter.com/_/status/{tweet_id} - skipping, older than {last_processed_timestamp}")
        oldest_id_found = True
        break
      elif tweet_favorited:
        print(f"https://twitter.com/_/status/{tweet_id} - skipping, already processed")
      else:
        if not any(d['id'] == tweet_id for d in unprocessed_requests):
          print(f"https://twitter.com/_/status/{tweet_id} - queueing, waiting to be processed")
          unprocessed_requests.append({
            "id": tweet_id,
            "text": tweet_full_text,
            "screen_name": tweet_screen_name,
            "created_at": tweet_created_at
          })

print()
for unprocessed_request in reversed(unprocessed_requests):
  print(f"Processing request for https://twitter.com/_/status/{unprocessed_request['id']} [{unprocessed_request['created_at']}]")
  m = re.search(r"\[([A-Za-z0-9_]+)\]", unprocessed_request["text"])
  try:
    edition = m.group(1).upper()

    # check scryfall that specified edition is valid
    payload = {
      'q': [ f" \
        edition:{edition} \
      "]
    }
    r = requests.get('https://api.scryfall.com/cards/random', params=payload)
    time.sleep(1/requests_per_second)

    if "status" in r.json() and r.json()["status"] == 404:
      tweepy_reply = f"Booster Tutor could not find a booster pack in Scryfall for [{edition}]. https://en.wikipedia.org/wiki/List_of_Magic:_The_Gathering_sets"
      print(tweepy_reply)
      tweepy_api.update_status(
        status=tweepy_reply,
        in_reply_to_status_id=unprocessed_request["id"],
        auto_populate_reply_metadata=True
      )
      tweepy_api.create_favorite(id=unprocessed_request["id"])
      tweepy_api.update_profile(description=f"most recent booster opened on: {unprocessed_request['created_at']}")

    else:
      print(f"Generating booster pack for [{edition}]")

      commons = []
      uncommons = []
      rares = []

      # get commons
      rarity = "common"
      while len(commons) < 10:
        not_card = ""
        for card in commons:
          not_card += f"-!\"{card}\" "
        payload = {
          'q': [ f" \
            edition:{edition} \
            rarity:{rarity} \
            -type:land \
            {not_card} \
          "]
        }
        r = requests.get('https://api.scryfall.com/cards/random', params=payload)
        print(f"Common: {r.json()['name']}")
        commons.append(r.json()["name"])
        time.sleep(1/requests_per_second)

      # get uncommons
      rarity = "uncommon"
      while len(uncommons) < 3:
        not_card = ""
        for card in uncommons:
          not_card += f"-!\"{card}\" "
        payload = {
          'q': [ f" \
            edition:{edition} \
            rarity:{rarity} \
            -type:land \
            {not_card} \
          "]
        }
        r = requests.get('https://api.scryfall.com/cards/random', params=payload)
        print(f"Uncommon: {r.json()['name']}")
        uncommons.append(r.json()["name"])
        time.sleep(1/requests_per_second)

      # get rares and mythics
      rarity = "rare"
      while len(rares) < 1:
        not_card = ""
        for card in rares:
          not_card += f"-!\"{card}\" "
        payload = {
          'q': [ f" \
            edition:{edition} \
            rarity>={rarity} \
            -type:land \
            {not_card} \
          "]
        }
        r = requests.get('https://api.scryfall.com/cards/random', params=payload)
        print(f"Rare: {r.json()['name']}")
        rares.append(r.json()["name"])
        time.sleep(1/requests_per_second)

      # generate scryfall link
      query_params = []
      for common in commons:
        query_params.append(f"(edition:{edition} !\"{common}\")")
      for uncommon in uncommons:
        query_params.append(f"(edition:{edition} !\"{uncommon}\")")
      for rare in rares:
        query_params.append(f"(edition:{edition} !\"{rare}\")")
      query_params = urllib.parse.quote_plus(" or ".join(query_params))

      tweepy_reply = f"Here is your booster pack of [{edition}]! https://scryfall.com/search?order=rarity&dir=desc&q={query_params}"
      print(tweepy_reply)
      tweepy_api.update_status(
        status=tweepy_reply,
        in_reply_to_status_id=unprocessed_request["id"],
        auto_populate_reply_metadata=True
      )
      tweepy_api.create_favorite(id=unprocessed_request["id"])
      tweepy_api.update_profile(description=f"most recent booster opened on: {unprocessed_request['created_at']}")

  except Exception as e:
    tweepy_reply = f"Please specify which pack you wish to open. For example: \"[LEA]\" https://en.wikipedia.org/wiki/List_of_Magic:_The_Gathering_sets"
    print(tweepy_reply)
    tweepy_api.update_status(
      status=tweepy_reply,
      in_reply_to_status_id=unprocessed_request["id"],
      auto_populate_reply_metadata=True
    )
    tweepy_api.create_favorite(id=unprocessed_request["id"])
    tweepy_api.update_profile(description=f"most recent booster opened on: {unprocessed_request['created_at']}")
  print()
