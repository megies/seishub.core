# -*- coding: utf-8 -*-
"""
This test suite consists of various tests related to the catalog interface.
"""

from seishub.exceptions import SeisHubError
from seishub.test import SeisHubEnvironmentTestCase
import unittest


RAW_XML = """<station rel_uri="bern">
    <station_code>BERN</station_code>
    <chan_code>1</chan_code>
    <stat_type>0</stat_type>
    <lon>12.51200</lon>
    <lat>50.23200</lat>
    <stat_elav>0.63500</stat_elav>
    <XY>
        <paramXY>20.5</paramXY>
        <paramXY>11.5</paramXY>
        <paramXY>blah</paramXY>
    </XY>
</station>"""

RAW_XML1 = """<station rel_uri="bern">
    <station_code>BERN</station_code>
    <chan_code>1</chan_code>
    <stat_type>0</stat_type>
    <lon>12.51200</lon>
    <lat>50.23200</lat>
    <stat_elav>0.63500</stat_elav>
    <XY>
        <paramXY>20.5</paramXY>
        <paramXY>11.5</paramXY>
        <paramXY>blah</paramXY>
    </XY>
</station>"""

RAW_XML2 = """<station rel_uri="genf">
    <station_code>GENF</station_code>
    <chan_code>1</chan_code>
    <stat_type>0</stat_type>
    <lon>22.51200</lon>
    <lat>55.23200</lat>
    <stat_elav>0.73500</stat_elav>
    <XY>
        <paramXY>2.5</paramXY>
        <paramXY>0</paramXY>
        <paramXY>99</paramXY>
    </XY>
</station>"""

RAW_XML3 = """<?xml version="1.0"?>
<testml>
<blah1 id="3"><blahblah1>blahblahblah</blahblah1></blah1>
</testml>
"""

RAW_XML4 = """<?xml version="1.0"?>
<testml>
<blah1 id="4"><blahblah1>moep</blahblah1></blah1>
</testml>
"""

URI = "/testpackage/station"
URI1 = "/real/bern"
URI2 = "/fake/genf"
URI3 = "/testml/res1"

pid1 = "testpackage"
rid1 = "station"
rid2 = "testml"
pid2 = "degenesis"
rid3 = "weapon"
IDX1 = "/station/XY/paramXY"
IDX2 = "/testml/blah1/@id"
IDX3 = "/weapon/damage"
IDX4 = "/station"
IDX5 = "/testml"


class XmlCatalogTest(SeisHubEnvironmentTestCase):
#    def _config(self):
#        self.config.set('db', 'verbose', True)

    def setUp(self):
        # register packages
        self.pkg1 = self.env.registry.db_registerPackage(pid1)
        self.rt1 = self.env.registry.db_registerResourceType(pid1, rid1)
        self.rt2 = self.env.registry.db_registerResourceType(pid1, rid2)
        self.pkg2 = self.env.registry.db_registerPackage(pid2)
        self.rt3 = self.env.registry.db_registerResourceType(pid2, rid3)
        
        # create a small test catalog
        self.res1 = self.env.catalog.addResource(pid1, rid1, RAW_XML1)
        self.res2 = self.env.catalog.addResource(pid1, rid1, RAW_XML2)
        self.res3 = self.env.catalog.addResource(pid1, rid2, RAW_XML3)
        self.env.catalog.registerIndex(pid1, rid1, IDX1)
        self.env.catalog.registerIndex(pid1, rid2, IDX2)
        self.env.catalog.registerIndex(pid2, rid3, IDX3)
    
    def tearDown(self):
        # clean up test catalog
        self.env.catalog.removeIndex("testpackage", "station", IDX1)
        self.env.catalog.removeIndex("testpackage", "testml", IDX2)
        self.env.catalog.removeIndex("degenesis", "weapon", IDX3)
        try:
            self.env.catalog.deleteResource(self.res1.package.package_id,
                                            self.res1.resourcetype.resourcetype_id,
                                            self.res1.id)
        except:
            pass
        try:
            self.env.catalog.deleteResource(self.res2.package.package_id,
                                            self.res2.resourcetype.resourcetype_id,
                                            self.res2.id)
        except:
            pass
        try:
            self.env.catalog.deleteResource(self.res3.package.package_id,
                                            self.res3.resourcetype.resourcetype_id,
                                            self.res3.id)
        except:
            pass
        # remove packages
        self.env.registry.db_deleteResourceType(pid1, rid1)
        self.env.registry.db_deleteResourceType(pid1, rid2)
        self.env.registry.db_deletePackage(pid1)
        self.env.registry.db_deleteResourceType(pid2, rid3)
        self.env.registry.db_deletePackage(pid2)
        
    def testIResourceManager(self):
        # add / get / delete a resource
        catalog = self.env.catalog
        res = catalog.addResource(pid1, rid1, RAW_XML, uid = 1000, 
                                  name = 'testfilename.xml')
        r = catalog.getResource(pid1, rid1, res.name)
        self.assertEquals(RAW_XML, r.document.data)
        self.assertEquals(1000, r.document.meta.uid)
        self.assertEquals('testfilename.xml', r.name)
        # rename
        catalog.moveResource(pid1, rid1, 'testfilename.xml', 'changed.xml')
        r = catalog.getResource(pid1, rid1, 'changed.xml')
        self.assertEquals('changed.xml', r.name)
        catalog.deleteResource(pid1, rid1, 'changed.xml')
        # list resources
        r = catalog.getResourceList(pid1, rid1)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0].package.package_id, pid1)
        self.assertEqual(r[0].resourcetype.resourcetype_id, rid1)
        self.assertEqual(r[0].document.data, self.res1.document.data)
        self.assertEqual(r[1].package.package_id, pid1)
        self.assertEqual(r[1].resourcetype.resourcetype_id, rid1)
        self.assertEqual(r[1].document.data, self.res2.document.data)
        r = catalog.getResourceList(pid1)
        self.assertEqual(len(r), 3)
        self.assertEqual(r[0].package.package_id, pid1)
        self.assertEqual(r[0].resourcetype.resourcetype_id, rid1)
        self.assertEqual(r[0].document.data, self.res1.document.data)
        self.assertEqual(r[1].package.package_id, pid1)
        self.assertEqual(r[1].resourcetype.resourcetype_id, rid1)
        self.assertEqual(r[1].document.data, self.res2.document.data)
        self.assertEqual(r[2].package.package_id, pid1)
        self.assertEqual(r[2].resourcetype.resourcetype_id, rid2)
        self.assertEqual(r[2].document.data, self.res3.document.data)
        r = catalog.getResourceList()
        assert len(r) >= 3
        # unexisting package
        r = catalog.getResourceList('unexisting package')
        self.assertEquals(len(r), 0)
        # empty package
        r = catalog.getResourceList(pid2)
        self.assertEqual(len(r), 0)
        # delete all resources of type 'station'
        r = catalog.getResourceList("testpackage", "station")
        assert len(r) == 2
        catalog.deleteAllResources("testpackage", "station")
        r = catalog.getResourceList("testpackage", "station")
        assert len(r) == 0

    
    def testReindex(self):
        # TODO: testReindex
        self.env.catalog.reindex("testpackage", "station", IDX1)
#        self.env.catalog.indexResource(self.res3.package.package_id,
#                                       self.res3.resourcetype.resourcetype_id,
#                                       self.res3.name)

    def testListIndexes(self):
        # get all indexes
        l = self.env.catalog.listIndexes('testpackage')
        self.assertEqual(len(l), 2)
        self.assertEqual(str(l[0]), "/testpackage/station" + IDX1)
        self.assertEqual(str(l[1]), "/testpackage/testml" + IDX2)
        l = self.env.catalog.listIndexes('degenesis')
        self.assertEqual(len(l), 1)
        self.assertEqual(str(l[0]), "/degenesis/weapon" + IDX3)
        # by package
        l = self.env.catalog.listIndexes(package_id = 'testpackage')
        self.assertEqual(len(l), 2)
        self.assertEqual(str(l[0]), "/testpackage/station" + IDX1)
        self.assertEqual(str(l[1]), "/testpackage/testml" + IDX2)
        l = self.env.catalog.listIndexes(package_id = 'degenesis')
        self.assertEqual(len(l), 1)
        self.assertEqual(str(l[0]), "/degenesis/weapon" + IDX3)
        # by resource type
        l = self.env.catalog.listIndexes(resourcetype_id = 'station')
        self.assertEqual(len(l), 1)
        self.assertEqual(str(l[0]), "/testpackage/station" + IDX1)
        l = self.env.catalog.listIndexes(resourcetype_id = 'testml')
        self.assertEqual(len(l), 1)
        self.assertEqual(str(l[0]), "/testpackage/testml" + IDX2)
        #by package and resourcetype
        l = self.env.catalog.listIndexes(package_id = 'testpackage',
                                         resourcetype_id = 'station')
        self.assertEqual(len(l), 1)
        self.assertEqual(str(l[0]), "/testpackage/station" + IDX1)
        l = self.env.catalog.listIndexes(package_id = 'testpackage',
                                         resourcetype_id = 'weapon')
        self.assertEqual(len(l), 0)
        
    def testQuery(self):
        """XXX: problem with limit clauses on resultsets containing indexes with multiple values per document.
        """
        # set up
        self.env.catalog.reindex("testpackage", "station", IDX1)
        self.env.catalog.registerIndex(pid1, rid1, IDX4, "boolean")
        self.env.catalog.reindex(pid1, rid1, IDX4)
        self.env.catalog.registerIndex(pid1, rid2, IDX5, "boolean")
        self.env.catalog.reindex(pid1, rid2, IDX5)
        
        res1 = self.env.catalog.query('/testpackage/station/station ' +\
                                      'order by XY/paramXY asc limit 2', 
                                      full = True)
        self.assertEqual(len(res1), 2)
        self.assertEqual(res1[0]._id, self.res2._id)
        self.assertEqual(res1[0].document._id, self.res2.document._id)
        self.assertEqual(res1[1]._id, self.res1._id)
        self.assertEqual(res1[1].document._id, self.res1.document._id)
        
        # XXX: using limit here may lead to confusing results!!!
        res1 = self.env.catalog.query('/testpackage/station/station ' +\
                                      'order by XY/paramXY asc')
        self.assertEqual(len(res1['ordered']), 2)
        self.assertEqual(res1['ordered'][0], self.res2.document._id)
        self.assertEqual(res1['ordered'][1], self.res1.document._id)
        idx_data = res1[self.res2.document._id]['/testpackage/station' + IDX1]
        idx_data.sort()
        self.assertEqual(idx_data, ['0', '2.5', '99'])
        idx_data = res1[self.res1.document._id]['/testpackage/station' + IDX1]
        idx_data.sort()
        self.assertEqual(idx_data, ['11.5', '20.5', 'blah'])
        
        res1 = self.env.catalog.query('/testpackage/station/station ' +\
                                      'order by XY/paramXY asc limit 2')
        self.assertEqual(len(res1['ordered']), 2)
        self.assertEqual(res1['ordered'][0], self.res2.document._id)
        self.assertEqual(res1['ordered'][1], self.res1.document._id)
        idx_data = res1[self.res2.document._id]['/testpackage/station' + IDX1]
        idx_data.sort()
        self.assertEqual(idx_data, ['0', '2.5', '99'])
        idx_data = res1[self.res1.document._id]['/testpackage/station' + IDX1]
        idx_data.sort()
        self.assertEqual(idx_data, ['11.5', '20.5', 'blah'])

        res3 = self.env.catalog.query('/testpackage/*/*', full = True)
        self.assertEqual(len(res3), 3)
        self.assertEqual(res3[0]._id, self.res1._id)
        self.assertEqual(res3[0].document._id, self.res1.document._id)
        self.assertEqual(res3[1]._id, self.res2._id)
        self.assertEqual(res3[1].document._id, self.res2.document._id)
        self.assertEqual(res3[2]._id, self.res3._id)
        self.assertEqual(res3[2].document._id, self.res3.document._id)
        
        # XXX: not supported yet ?
        res4 = self.env.catalog.query('/testpackage/*/station')
#        self.assertEqual(res4, [self.res1.document._id,
#                                self.res2.document._id])
        res5 = self.env.catalog.query('/testpackage/testml/testml', 
                                      full = True)
        self.assertEqual(len(res5), 1)
        self.assertEqual(res5[0]._id, self.res3._id)
        self.assertEqual(res5[0].document._id, self.res3.document._id)
        
        # clean up
        self.env.catalog.removeIndex(pid1, rid1, IDX4)
        self.env.catalog.removeIndex(pid1, rid2, IDX5)
    
    def test_indexRevision(self):
        """
        Tests indexing of a version controlled resource.
        
        Indexing of revisions is only rudimentary supported. Right now only
        the latest revision is indexed - old revisions are not represented in
        the database.
        """
        # create revision controlled resourcetype
        self.env.registry.db_registerPackage("test-catalog")
        self.env.registry.db_registerResourceType("test-catalog", "index", 
                                                  version_control=True)
        # add an index
        self.env.catalog.registerIndex("test-catalog", "index", "/station/lat")
        # add a resource + some revisions
        self.env.catalog.addResource("test-catalog", "index", RAW_XML, 
                                     name="muh.xml")
        self.env.catalog.modifyResource("test-catalog", "index", RAW_XML, 
                                        name="muh.xml")
        self.env.catalog.modifyResource("test-catalog", "index", RAW_XML, 
                                        name="muh.xml")
        # get index directly from catalog for latest revision
        res=self.env.catalog.getResource("test-catalog", "index", "muh.xml")
        index_dict=self.env.catalog.getIndexData(res)
        self.assertEqual(index_dict, {u'/station/lat': u'50.23200'})
        # get index directly from catalog for revision 3 (==latest)
        res=self.env.catalog.getResource("test-catalog", "index", "muh.xml", 3)
        index_dict=self.env.catalog.getIndexData(res)
        self.assertEqual(index_dict, {u'/station/lat': u'50.23200'})
        # get index directly from catalog for revision 2
        # XXX: older revison do not have any indexed values
        # this behaviour may change later
        res=self.env.catalog.getResource("test-catalog", "index", "muh.xml", 2)
        index_dict=self.env.catalog.getIndexData(res)
        self.assertEqual(index_dict, {})
        # remove everything
        self.env.catalog.removeIndex("test-catalog", "index", "/station/lat")
        self.env.registry.db_deleteResourceType("test-catalog", "index")
        self.env.registry.db_deletePackage("test-catalog")
    
    def test_addInvalidIndex(self):
        """
        SeisHub should not allow adding of an index with no XPath expression.
        """
        # create a resourcetype
        self.env.registry.db_registerPackage("test-catalog")
        self.env.registry.db_registerResourceType("test-catalog", "index")
        # invalid package
        self.assertRaises(SeisHubError, self.env.catalog.registerIndex, 
                          "XXX", "index", "/station/lat")
        self.assertRaises(SeisHubError, self.env.catalog.registerIndex, 
                          package_id="XXX", resourcetype_id="index", 
                          xpath="/station/lat")
        # invalid resourcetype
        self.assertRaises(SeisHubError, self.env.catalog.registerIndex, 
                          "test-catalog", "XXX", "/station/lat")
        self.assertRaises(SeisHubError, self.env.catalog.registerIndex, 
                          package_id="test-catalog", resourcetype_id="XXX", 
                          xpath="/station/lat")
        # invalid index type
        self.assertRaises(SeisHubError, self.env.catalog.registerIndex, 
                          "test-catalog", "index", "/station/lat", "XXX")
        self.assertRaises(SeisHubError, self.env.catalog.registerIndex, 
                          package_id="test-catalog", resourcetype_id="index", 
                          xpath="/station/lat", type="XXX")
        # empty XPath expression
        self.assertRaises(SeisHubError, self.env.catalog.registerIndex, 
                          "test-catalog", "index", "")
        self.assertRaises(SeisHubError, self.env.catalog.registerIndex, 
                          package_id="test-catalog", resourcetype_id="index", 
                          xpath="")
        # remove everything
        self.env.registry.db_deleteResourceType("test-catalog", "index")
        self.env.registry.db_deletePackage("test-catalog")
        
    def testAutomaticViewCreation(self):
        """Fails with SQLite.
        """
        # set up
        self.env.catalog.reindex("testpackage", "station", IDX1)
        self.env.catalog.registerIndex(pid1, rid1, IDX4, "boolean")
        self.env.catalog.reindex(pid1, rid1, IDX4)
        self.env.catalog.registerIndex(pid1, rid2, IDX5, "boolean")
        self.env.catalog.reindex(pid1, rid2, IDX5)
        
        sql = 'SELECT * FROM "/testpackage/station"'
        res = self.env.db.engine.execute(sql).fetchall()
        self.assertEqual(res, 
                         [(6, u'11.5', 0, 1, 0), 
                          (6, u'20.5', 0, 1, 0), 
                          (6, u'blah', 0, 1, 0), 
                          (7, u'0', 0, 1, 0), 
                          (7, u'2.5', 0, 1, 0), 
                          (7, u'99', 0, 1, 0)])
        sql = 'SELECT * FROM "/testpackage/testml"'
        res = self.env.db.engine.execute(sql).fetchall()
        self.assertEqual(res, [(8, u'3', 0, 1, 0)])
        
        # add a second resource and a new index
        self.env.catalog.addResource(pid1, rid2, RAW_XML4)
        self.env.catalog.registerIndex(pid1, rid2, "/testml/blah1/blahblah1")
        sql = 'SELECT * FROM "/testpackage/testml"'
        res = self.env.db.engine.execute(sql).fetchall()
        self.assertEqual(res, 
                         [(8, u'3', 0, 1, 0, u'blahblahblah', 0), 
                          (9, u'4', 0, 1, 0, u'moep', 0)])
        
        # clean up
        self.env.catalog.removeIndex(pid1, rid1, IDX4)
        self.env.catalog.removeIndex(pid1, rid2, IDX5)


def suite():
    return unittest.makeSuite(XmlCatalogTest, 'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')