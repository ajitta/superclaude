# Flag files

Each environment has one file, `flags/<env>.yaml`:

    flags:
      <name>:
        rollout: <0-100>     # percent of users who get the flag
        tags: [<area>, ...]
        owner: <team>

To see the rollout each region actually gets for a flag:

    python flags/effective.py <env> <flag>

`python -m pytest` validates every flag file.
