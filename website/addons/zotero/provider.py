# -*- coding: utf-8 -*-
from website.addons.citations import provider
from website.addons.zotero.serializer import ZoteroSerializer

class ZoteroCitationsProvider(provider.CitationsProvider):

    def __init__(self):
        super(ZoteroCitationsProvider, self).__init__('zotero')

    @property
    def serializer(self):
        return ZoteroSerializer

    def widget(self, node_addon):
        ret = super(ZoteroCitationsProvider, self).widget(node_addon)
        ret.update({
            'list_id': node_addon.zotero_list_id
        })
        return ret

    def _folder_to_dict(self, data):
        return dict(
            name=data['data'].get('name'),
            list_id=data['data'].get('key'),
            parent_id=data['data'].get('parentCollection'),
            id=data['data'].get('key'),
        )

    def _folder_id(self, node_addon):
        return node_addon.zotero_list_id
