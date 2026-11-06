"""Development preview only. Desktop builds never bind a public interface."""
import argparse

import uvicorn

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8000)
    # Test harness only. Saving refuses in a browser preview because a browser
    # has nowhere to write, so scripts/check_save.py needs a server that behaves
    # like the desktop shell. The desktop shell sets this same flag itself, and
    # additionally requires a request token. Never enable it for a hosted copy.
    parser.add_argument('--qa-desktop', action='store_true',
                        help='QA only: behave like the desktop shell (enables the save endpoints).')
    args = parser.parse_args()
    if args.qa_desktop:
        from app.server import app
        app.state.desktop = True
    uvicorn.run('app.server:app', host=args.host, port=args.port, access_log=False,
                loop='asyncio', http='h11', ws='none')
