# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template, request, url_for, flash, redirect, abort
from flask_login import login_required
from asimov.extensions import db
import requests
import bs4

from .models import Feed, FeedItem, FeedForm
from asimov.utils import flash_errors

mod = Blueprint('feeds', __name__, url_prefix='', static_folder='../static')


@mod.route('/')
@login_required
def show_recent_items():
    feed_items = FeedItem.query.order_by(FeedItem.published_date).limit(30)
    feed_form = FeedForm(request.form)
    return render_template('feeds/list_recent_items.html', feed_items=feed_items,
        feed_form=feed_form)


@mod.route('/feeds')
@login_required
def show_feeds():
    feeds = Feed.query.order_by(Feed.title)
    return render_template('feeds/list_feeds.html', feeds=feeds)


@mod.route('/feeds', methods=['POST'])
def subscribe_to_feed():
    form = FeedForm(request.form)
    if form.validate_on_submit():
        feed_url = form.url.data
        response = requests.get(feed_url)
        if not response.ok:
            flash('Server at %s didn\'t respond, if you\'re sure the URL is correct'
                ' you should try again in a moment' % feed_url)
            return render_template('feeds/list_recent_items.html', feed_form=form), 503
        remote_content_type = response.headers.get('content-type')
        rss_content_types = (
            'application/rss+xml',
            'text/xml',
        )
        if remote_content_type == 'application/atom+xml':
            # atom feed, good stuff
            title = 'atom something'
        elif remote_content_type in rss_content_types:
            # rss feed, a bit wobbly
            title = 'rss something'
        else:
            # probably just a normal front page, check it for an actual feed url
            html_soup = bs4.BeautifulSoup(response.content, 'lxml')
            links = html_soup.find_all('link', rel='alternate')

            # TODO: Figure out how to handle multiple feeds on a page, like on f.ex
            # adactio.com
            if len(links) == 1:
                title = links[0].get('title') or feed_url

        feed = Feed.create(url=feed_url, title=title)
        flash('Successfully subscribed to feed %s.' % title, 'success')
        redirect_url = url_for('.show_feed', feed_id=feed.id)
        return redirect(redirect_url)
    else:
        flash_errors(form)
        return render_template('public/home.html', form=form), 400


@mod.route('/feeds/<int:feed_id>', methods=['GET', 'POST', 'DELETE'])
@login_required
def feed_details(feed_id):
    feed = Feed.query.get_or_404(feed_id)
    method = request.method

    if method == 'POST':
        # check for override
        override_method = request.args.get('method', '').upper()
        if override_method == 'DELETE':
            method = override_method
        else:
            abort(504)

    if method == 'DELETE':
        feed.delete()
        return redirect(url_for('.show_feeds'))


@mod.route('/feeds/update', methods=['POST'])
@login_required
def update_feeds():
    # Usually not necessary to hit this, but included for ease of testing now
    # in the beginning

    # TODO: Parallelize with multiprocessing.Queue
    for feed in Feed.query.all():
        feed.update()

    return redirect(url_for('.show_recent_items'))
