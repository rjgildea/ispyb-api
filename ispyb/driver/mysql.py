from __future__ import absolute_import, division

import ConfigParser
import os.path

import ispyb.interface.main
import ispyb.exception
import mysql.connector

class ISPyBMySQLDriver(ispyb.interface.main.IF):
  '''This driver connects directly to an ISPyB MySQL/MariaDB database.
  '''

  def __init__(self, host=None, port=None, database=None,
               username=None, password=None, config_file=None):
    if config_file:
      cfgparser = ConfigParser.ConfigParser()
      if not cfgparser.read(config_file):
        raise RuntimeError('Could not read from configuration file %s' %
                           config_file)
      cfgsection = dict(cfgparser.items('ispyb'))
      if not host: host = cfgsection.get('host')
      if not port: port = cfgsection.get('port', 3306)
      if not database: database = cfgsection.get('database')
      if not username: username = cfgsection.get('username')
      if not password: password = cfgsection.get('password')
    if not port: port = 3306

    self._db_conndata = { 'host': host, 'port': port, 'user': username,
                          'password': password, 'database': database }
    self._db = mysql.connector.connect(**self._db_conndata)

    class context_cursor(object):
      '''Context manager for a mysql.connector cursor with two differences
         to a regular cursor: By default results are returned as a dictionary,
         and a new .run() function is an alias to .execute which accepts query
         parameters as function parameters rather than a list.'''
      def __init__(cc, **parameters):
        if 'dictionary' not in parameters:
          parameters['dictionary'] = True
        cc.cursorparams = parameters
      def __enter__(cc):
        cc.cursor = self._db.cursor(**cc.cursorparams)
        def flat_execute(stmt, *parameters):
          cc.cursor.execute(stmt, parameters)
        setattr(cc.cursor, 'run', flat_execute)
        return cc.cursor
      def __exit__(cc, *args):
        cc.cursor.close()
    self._db_cc = context_cursor

  def _db_call(self, query, *parameters):
    cursor = self._dbcursor()
    cursor.execute(query, parameters)
    return cursor

  def get_reprocessing_id(self, reprocessing_id):
    with self._db_cc() as cursor:
      cursor.run("SELECT * "
                 "FROM Reprocessing "
                 "LEFT JOIN AutoProcProgram USING (reprocessingId) "
                 "WHERE reprocessingId = %s;", reprocessing_id)
      result = cursor.fetchone()
    if result:
      if not result.get('autoProcProgramId'):
        result['readableStatus'] = 'submitted'
      elif result.get('processingStatus') == None:
        result['readableStatus'] = 'running'
      elif result.get('processingStatus') == 1:
        result['readableStatus'] = 'success'
      elif result.get('processingStatus') == 0:
        result['readableStatus'] = 'failure'
      else:
        result['readableStatus'] = 'unknown'
      return result
    raise ispyb.exception.ISPyBNoResultException()

  def get_datacollection_id(self, dcid):
    with self._db_cc() as cursor:
      cursor.run("SELECT * "
                 "FROM DataCollection "
                 "WHERE dataCollectionId = %s "
                 "LIMIT 1;", dcid)
      result = cursor.fetchone()
    if result:
      return result
    raise ispyb.exception.ISPyBNoResultException()

  def get_datacollection_template(self, dcid):
    with self._db_cc() as cursor:
      cursor.run("SELECT imageDirectory, fileTemplate "
                 "FROM DataCollection "
                 "WHERE dataCollectionId = %s "
                 "LIMIT 1;", dcid)
      result = cursor.fetchone()
    if result:
      return os.path.join(result['imageDirectory'], result['fileTemplate'])
    raise ispyb.exception.ISPyBNoResultException()

  def get_reprocessing_parameters(self, reprocessing_id):
    params = {}
    with self._db_cc() as cursor:
      cursor.run("SELECT parameterKey, parameterValue "
                 "FROM ReprocessingParameter "
                 "WHERE reprocessingId = %s;", reprocessing_id)
      while True:
        result = cursor.fetchmany(size=50)
        if not result: break
        for row in result:
          params[row['parameterKey']] = row['parameterValue']
    return params

  def get_reprocessing_sweeps(self, reprocessing_id):
    sweeps = []
    with self._db_cc() as cursor:
      cursor.run("SELECT dataCollectionId, startImage, endImage "
                 "FROM ReprocessingImageSweep "
                 "WHERE reprocessingId = %s;", reprocessing_id)
      while True:
        result = cursor.fetchmany(size=50)
        if not result: break
        sweeps.extend(result)
    return sweeps

  def update_reprocessing_status(self, reprocessing_id, status='running',
                                 start_time=None,
                                 update_time=None, update_message=None):
    raise ispyb.exception.UpdateFailed("This operation is currently not supported by ISPyB. SCI-6048")
