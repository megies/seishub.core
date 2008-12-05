# -*- coding: utf-8 -*-
"""
Various CSS themes for the administration pages.
"""

from seishub.core import Component, implements
from seishub.processor.interfaces import IAdminTheme


class OldTheme(Component):
    """
    Old WebAdmin theme.
    """
    implements(IAdminTheme)
    
    theme_id = 'oldstyle'
    theme_css_file = 'css/default.css'
    
    def getThemeId(self):
        return ('default', '/css/default.css')


class MagicTheme(Component):
    """
    New *magic* WebAdmin theme.
    """
    implements(IAdminTheme)
    
    theme_id = 'magic'
    theme_css_file = 'css/magic.css'
    
    def getThemeId(self):
        return ('magic', '/css/magic.css')