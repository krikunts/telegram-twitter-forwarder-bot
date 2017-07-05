from functools import wraps
import html
import re


def with_touched_chat(f):
    @wraps(f)
    def wrapper(bot, update=None, *args, **kwargs):
        if update is None:
            return f(bot, *args, **kwargs)

        chat = bot.get_chat(update.message.chat)
        chat.touch_contact()
        kwargs.update(chat=chat)
        return f(bot, update, *args, **kwargs)

    return wrapper


def escape_markdown(text):
    """Helper function to escape telegram markup symbols"""
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)


def markdown_link(text, url):
    """Get markdown link from text and url"""
    return '[{text}]({url})'.format(text=text, url=url)


def markdown_username_link(username):
    """Get markdown twitter user link"""
    return markdown_link('@' + username, 'https://twitter.com/' + username)


def markdown_hashtag_link(hashtag):
    """Get markdown twitter hashtag link"""
    return markdown_link('#' + hashtag, 'https://twitter.com/hashtag/' + hashtag)


def markdown_tweet_link(text, screen_name, tweet_id):
    """Get markdown tweet link"""
    return markdown_link(text, 'https://twitter.com/{}/status/{}'.format(screen_name, tweet_id))


def entity_replace_args(tweet, entity, entity_field_name):
    """Get old and new text for replace from tweet entity"""
    entity_value = entity[entity_field_name]
    indices = entity['indices']
    old_text = tweet.text[indices[0]:indices[1]]
    return escape_markdown(old_text), entity_value


def expand_urls(text, tweet):
    """Substitute all shortened urls with their expanded version"""
    for url_entity in tweet.entities['urls']:
        old_url, new_url = entity_replace_args(tweet, url_entity, 'expanded_url')
        text = text.replace(old_url, escape_markdown(new_url))
    return text


def markdown_twitter_usernames(text, tweet):
    """Restore markdown escaped usernames and make them link to twitter"""
    for mention_entity in tweet.entities['user_mentions']:
        old_text, screen_name = entity_replace_args(tweet, mention_entity, 'screen_name')
        text = text.replace(old_text, markdown_username_link(screen_name))
    return text


def markdown_twitter_hashtags(text, tweet):
    """Restore markdown escaped hashtags and make them link to twitter"""
    for hashtag_entity in tweet.entities['hashtags']:
        old_text, hashtag_text = entity_replace_args(tweet, hashtag_entity, 'text')
        text = text.replace(escape_markdown(old_text), markdown_hashtag_link(hashtag_text))
    return text


def prepare_tweet_text(tweet):
    """Do all escape things for tweet text"""
    res = html.unescape(tweet.text)
    res = escape_markdown(res)
    res = expand_urls(res, tweet)
    res = markdown_twitter_usernames(res, tweet)
    res = markdown_twitter_hashtags(res, tweet)
    return res
