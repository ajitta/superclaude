# CDN

`cache-rules.json` is applied with `cdnctl rules apply cache-rules.json`.

Purge cached objects at every edge:

    cdnctl purge --path '/static/img/*'
