import os
import re
import sys
import json
import time
import aiohttp
import asyncio
import pathlib
import logging
import contextlib
from collections import OrderedDict

import openai


class LazyDecoder(json.JSONDecoder):
    def decode(self, s, **kwargs):
        regex_replacements = [
            (re.compile(r'([^\\])\\([^\\])'), r'\1\\\\\2'),
            (re.compile(r',(\s*])'), r'\1'),
        ]
        for regex, replacement in regex_replacements:
            s = regex.sub(replacement, s)
        return super().decode(s, **kwargs)


def get_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger


LOGGER = get_logger()
MARKETPLACE_PROTOCOL = 'https'
MARKETPLACE_DOMAIN = "marketplace.cloudify.co"
MARKETPLACE_PREFIX = f'{MARKETPLACE_PROTOCOL}://{MARKETPLACE_DOMAIN}'
SCHEMA_FILENAME = pathlib.Path('cloudify_dsl.schema.json').as_posix()
SCHEMA = {}
NODE_TYPES = []
NODE_TYPE_DEFINITIONS = []
NEW_NODE_TYPE_DEFINITIONS = {}
openai.api_type = os.environ['OPENAI_TYPE']
openai.api_base = os.environ['OPENAI_BASE']
openai.api_version = os.environ['OPENAI_VERSION']
openai.api_key = os.environ['OPENAI_API_KEY']
CONTENT = 'Create a description in less than 50 words of this node type {node_type}. It should start with "{node_type} is a Cloudify node type".'
NEW_UPDATES = {}
OPENSTACK_CLIENT_KEYS = {
    'auth_url',
    'user_domain_id',
    'user_domain_name',
    'project_domain_id',
    'project_domain_name'
}


def get_chat_response(prompt, max_tokens=10000):
    time.sleep(1)
    try:
        resp = openai.ChatCompletion.create(
            engine="gpt35-16k",
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
            max_tokens=max_tokens
        )
    except openai.error.RateLimitError as e:
        waitfor = int(str(e).split('Please retry after ')[1].split(' seconds')[0])
        time.sleep(waitfor)
        return get_chat_response(prompt, max_tokens)
    result = resp.to_dict()['choices'][0].message['content']
    if '```json' in result:
        try:
            result = json.loads(result.split('```')[1].lstrip('json'), cls=LazyDecoder, strict=False, object_pairs_hook=OrderedDict)
        except json.decoder.JSONDecodeError:
            LOGGER.error('Failed here: {}'.format(result))
            raise
    return result


def get_novel_description(node_type):
    return get_chat_response(CONTENT.format(node_type=node_type), 100)


def generate_json_schema(properties):
    return get_chat_response(
        'Limit your response to pure JSON. '
        'Please do not use any escape characters.'
        'Can you generate a JSON schema for the following '
        'properties: {}'.format(properties)
    )


def generate_ref(key, val):
    if key == 'use_external_resource':
        val = {'$ref': '#/definitions/cloudifyBooleanOrGetInput'}
    elif key == 'create_if_missing':
        val = {'$ref': '#/definitions/cloudifyBooleanOrGetInput'}
    if isinstance(val, dict):
        for x, y in list(val.items()):
            if x == 'description':
                continue
            elif x in ['required']:
                del val[x]
        new_val = generate_json_schema(val)
        if isinstance(new_val, str):
            try:
                new_val = json.loads(new_val, object_pairs_hook=OrderedDict)
            except json.decoder.JSONDecodeError as e:
                str_e = str(e)
                if 'Char ' in str_e:
                    char = int(str_e.split('char ')[-1].strip(')'))
                LOGGER.error('Failed on this: {}'.format(new_val))
                raise
        elif not isinstance(new_val, dict):
            raise Exception('We are getting this junk: {}'.format(new_val))
        for i in list(new_val.keys()):
            if i not in val:
                del new_val[i]
        val = new_val
    return val



def create_properties(properties):
    for key, val in list(properties.items()):
        properties.update(generate_ref(key, val))
    return properties


def get_new_node_type_definition(node_name, node):
    properties = create_properties(node['properties'])
    definitions = [
        {
            f'nodeType{node_name}Properties': properties,
        }
    ]
    return definitions


def camel_case(string):
    string = string.replace('cloudify.nodes', '')
    up = False
    words = []
    for word in string.split('.'):
        if up:
            words.append(word.title())
        else:
            words.append(word.lower())
            up =True
    return ''.join(words)


def get_current_schema(filename: str=SCHEMA_FILENAME) -> dict:
    with open(filename, 'r') as outf:
        return json.load(outf)


def put_new_schema(filename: str=SCHEMA_FILENAME):
    with open(f'new_{filename}', 'w') as inf:
        json.dump(SCHEMA, inf, indent=2, sort_keys=True)


def check_if_node_type_in_schema(node):
    node_type = node['type']
    node_name =  camel_case(node_type)
    if not node_type.startswith('cloudify.nodes'):
        return
    if node_type.casefold() not in NODE_TYPES:
        LOGGER.info('Not in NODE TYPES: {}'.format(node_type))
    if node_type.casefold() not in NODE_TYPE_DEFINITIONS:
        node_type_definitions = get_new_node_type_definition(node_name, node)
        NEW_NODE_TYPE_DEFINITIONS.update(
            {
                f'nodeType{node_name}': {
                    'type': node_type,
                    'allOf': {
                        'if': {
                            'properties': {
                                'type': {'const': node_type}
                            }
                        },
                        'then': {
                            'properties': {
                                'properties': {'$ref': f'#/definitions/nodeType{node_name}Properties'},
                                # 'interfaces': {'$ref': f'#/definitions/nodeType{node_name}Interfaces'}
                            }
                        }
                    },
                    'definitions': node_type_definitions,
                }
            }
        )


def process_node_type_result(resp, total, maximum, func):
    for item in resp['items']:
        func(item)


async def get_node_types():
    total = 0
    maximum = 10
    url = f'{MARKETPLACE_PREFIX}/node-types?offset='
    async with aiohttp.ClientSession() as session:
        while True:
            LOGGER.debug('Getting results after {}.'.format(str(total)))
            async with session.get(url + str(total)) as resp:
                result = await resp.json()
                total += result['pagination']['size']
                process_node_type_result(
                    result,
                    0,
                    None,
                    check_if_node_type_in_schema
                )
            if not maximum:
                maximum = result['pagination']['total']
            if total >= maximum:
                break


def setup_node_types():
    node_types = []
    try:
        node_types = SCHEMA['definitions']['nodeTemplate']['properties']['type']['anyOf'][1]['enum']
    except (KeyError, IndexError):
        node_types = SCHEMA['definitions']['nodeTemplate']['properties']['type']['anyOf'][1]['enum']
    NODE_TYPES.extend([v.casefold() for v in node_types])


def update_node_types(new):
    LOGGER.info('update_node_types: Adding new: {}'.format(new))
    try:
        SCHEMA['definitions']['nodeTemplate']['properties']['type']['anyOf'][1]['enum'].append(new)
    except (KeyError, IndexError):
        SCHEMA['definitions']['nodeTemplate']['properties']['type']['anyOf'][1]['enum'].append(new)



def setup_node_type_definitions():
    for mapping in SCHEMA['definitions']['nodeTemplate']['allOf']:
        NODE_TYPE_DEFINITIONS.append(mapping['if']['properties']['type']['const'].casefold())


def update_node_type_definitions(new):
    LOGGER.info('update_node_type_definitions: Adding new: {}'.format(new))
    SCHEMA['definitions']['nodeTemplate']['allOf'].append(new)


def update_definitions(new):
    LOGGER.info('update_definitions: Adding new: {}'.format(new))
    SCHEMA['definitions'].update(new)


if __name__ == '__main__':
    SCHEMA = get_current_schema()
    setup_node_types()
    setup_node_type_definitions()
    asyncio.run(get_node_types())
    for k, v in NEW_NODE_TYPE_DEFINITIONS.items():
        update_node_types(v['type'])
        update_node_type_definitions(v['allOf'])
        for definiton in v['definitions']:
            update_definitions(definiton)
    put_new_schema()
