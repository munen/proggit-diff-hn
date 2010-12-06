What it does
------------

Get all submissions from [Proggit](http://www.reddit.com/r/programming/) and check if the submission has already been on [Hackernews](http://news.ycombinator.com/news).

If not, send an e-mail with the diff information using GMail.

Obviously this is intended to be run as a daily cronjob.

Configuration
-------------

The mail configuration is done in config.ini - it's straight forward.


Sample mail body
----------------

    Ratio on hn/off hn: 13/13
    
    nweb: a tiny, safe Web server (static pages only)
        http://www.ibm.com/developerworks/systems/library/es-nweb/index.html
        74 points
        69 comments
        http://www.reddit.com/r/programming/comments/eftiq/nweb_a_tiny_safe_web_server_static_pages_only/
    
    [snip for brevity]
