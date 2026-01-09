import argparse

def add_common_env_args(parser):
    parser.add_argument("--github", dest="GITHUB",
                        action=argparse.BooleanOptionalAction,
                        default=True)
    parser.add_argument("--ci", dest="CI",
                        action=argparse.BooleanOptionalAction,
                        default=True)
    return parser

def config2args(cfg: dict):
    def helper(val):
        if isinstance(val, bool):
            return str(val).lower()
        return val

    return [f"{k}={helper(v)}" for k, v in cfg.items()]
