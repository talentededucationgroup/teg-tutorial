#!/usr/bin/env python3
"""One-off/maintenance: delete Buffer DRAFT posts created by the autopost before 20/11/2026 21:00 WIB
(when the pipeline still saved everything to Drafts). Owner approved 20/11/2026. Only drafts, never queued/sent posts.
Mode: env MODE=inspect (print schema hints) or MODE=delete. Prints counts only, no post text."""
import json, os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from post_to_buffer import gql, KEY
CUT = datetime.datetime(2026, 11, 20, 14, 0, tzinfo=datetime.timezone.utc)  # 21:00 WIB
MODE = os.environ.get('MODE', 'inspect')
if not KEY:
    print('no key'); sys.exit(0)
def fields(t):
    d = gql('query T($n:String!){__type(name:$n){name kind fields{name args{name type{name kind ofType{name kind ofType{name}}}} type{name kind ofType{name kind}}} inputFields{name type{name kind ofType{name kind ofType{name}}}} enumValues{name}}}', {"n": t})
    return d['__type']
if MODE == 'inspect':
    q = fields('Query'); m = fields('Mutation')
    print('QUERY', [ (f['name'], [a['name'] for a in f['args']]) for f in q['fields'] if 'post' in f['name'].lower()])
    print('MUTATION', [ (f['name'], [a['name'] for a in f['args']]) for f in m['fields'] if 'post' in f['name'].lower() or 'draft' in f['name'].lower()])
    for t in ('PostsInput', 'PostsFiltersInput', 'PostFiltersInput', 'PostStatus', 'Post', 'DeletePostInput', 'PostsFilterInput'):
        try:
            x = fields(t)
            if x: print(t, x['kind'], [f['name'] for f in (x.get('fields') or x.get('inputFields') or [])] or [e['name'] for e in (x.get('enumValues') or [])])
        except Exception as e:
            print(t, 'ERR', str(e)[:120])
    sys.exit(0)
# delete mode
orgs = gql("query { account { organizations { id } } }")['account']['organizations']
total = deleted = 0
for o in orgs:
    after = None
    while True:
        d = gql("""query P($o:OrganizationId!,$a:String){ posts(input:{organizationId:$o, filter:{status:[draft]}}, first:50, after:$a){ edges{ node{ id status createdAt } } pageInfo{ hasNextPage endCursor } } }""", {"o": o['id'], "a": after})['posts']
        for e in d['edges']:
            n = e['node']; total += 1
            ts = datetime.datetime.fromisoformat(n['createdAt'].replace('Z', '+00:00'))
            if n['status'] == 'draft' and ts < CUT:
                r = gql("mutation D($i:PostId!){ deletePost(input:{id:$i}){ __typename } }", {"i": n['id']})
                deleted += 1
        if not d['pageInfo']['hasNextPage']:
            break
        after = d['pageInfo']['endCursor']
print(f'drafts seen {total}; deleted {deleted}')
