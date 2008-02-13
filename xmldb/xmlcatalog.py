# -*- coding: utf-8 -*-

from zope.interface import implements

from seishub.xmldb.interfaces import IXmlCatalog
from seishub.xmldb.xmlindexcatalog import XmlIndexCatalog
from seishub.xmldb.xmldbms import XmlDbManager
from seishub.xmldb.xmlresource import XmlResource
from seishub.xmldb.xmlindex import XmlIndex
from seishub.xmldb.xpath import IndexDefiningXpathExpression


class XmlCatalog(XmlDbManager):
    implements(IXmlCatalog)
    
    def __init__(self, db):
        XmlDbManager.__init__(self,db)
        self.index_catalog=XmlIndexCatalog(db, self)
    
    # methods from IXmlCatalog:
    def newXmlResource(self,uri,xml_data):
        return XmlResource(uri,xml_data)
    
    def newXmlIndex(self,xpath_expr,type="text"):
        exp_obj=IndexDefiningXpathExpression(xpath_expr)
        if type=="text":
            return XmlIndex(value_path = exp_obj.value_path,
                            key_path = exp_obj.key_path)
        else:
            return None
    
    def registerIndex(self,xml_index):
        return self.index_catalog.registerIndex(xml_index)
    
    def removeIndex(self,xpath_expr):
        exp_obj=IndexDefiningXpathExpression(xpath_expr)
        return self.index_catalog.removeIndex(value_path = exp_obj.value_path,
                                              key_path = exp_obj.key_path)
        
    def getIndex(self,xpath_expr):
        exp_obj=IndexDefiningXpathExpression(xpath_expr)
        return self.index_catalog.getIndex(value_path = exp_obj.value_path,
                                           key_path = exp_obj.key_path)
        
    def flushIndex(self,xpath_expr):
        exp_obj=IndexDefiningXpathExpression(xpath_expr)
        return self.index_catalog.flushIndex(value_path = exp_obj.value_path,
                                           key_path = exp_obj.key_path)
        
    def listIndexes(self,res_type = None, data_type = None):
        return self.index_catalog.getIndexes(value_path = res_type,
                                             data_type = data_type)
        
    def reindex(self,xpath_expr):
        exp_obj = IndexDefiningXpathExpression(xpath_expr)
        if not exp_obj:
            return
        key_path = exp_obj.key_path
        value_path = exp_obj.value_path
        
        # get index from db
        self.index_catalog.getIndex(key_path, value_path)
        
        # flush index
        self.flushIndex(xpath_expr)
        
        # find all resources the index applies to by resource type
        if value_path.startswith('/'):
            type = value_path[1:]
        else:
            type = value_path
        uris = self.getUriList(type)
        
        # reindex
        for uri in uris:
            self.index_catalog.indexResource(uri, value_path, key_path)
        
        return True