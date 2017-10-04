#!/usr/bin/env python

import context
from ispyb.sp.core import core
from ispyb.sp.mxprocessing import mxprocessing
from datetime import datetime
from testtools import get_connection

def insert_integration_and_processing(c):
    params = mxprocessing.get_program_params()
    params['cmd_line'] = 'ls -ltr'
    params['message'] = 'Just started ...'
    id = mxprocessing.upsert_program(c, list(params.values()))
    assert id is not None
    assert id > 0

    params['id'] = id
    params['status'] = True
    params['message'] = 'Finished'
    programid = mxprocessing.upsert_program(c, list(params.values()))
    assert programid is not None
    assert programid > 0

    params = mxprocessing.get_program_attachment_params()
    params['parentid'] = programid
    params['file_name'] = 'file.log'
    params['file_path'] = '/tmp'
    params['file_type'] = 'Log' # should be one of Log, Result, Graph
    id = mxprocessing.upsert_program_attachment(c, list(params.values()))
    assert id is not None
    assert id > 0

    params = mxprocessing.get_integration_params()
    params['datacollectionid'] = 993677
    params['start_image_no'] = 1
    params['end_image_no'] = 100
    params['refined_detector_dist'] = 1106.20
    params['refined_xbeam'] = 20.5
    params['refined_ybeam'] = 19.8
    params['rot_axis_x'] = 1.0
    params['rot_axis_y'] = 1.0
    params['rot_axis_z'] = 1.0
    params['beam_vec_x'] = 1.0
    params['beam_vec_y'] = 1.0
    params['beam_vec_z'] = 1.0
    params['cell_a'] = 10.7
    params['cell_b'] = 10.8
    params['cell_c'] = 9.1
    params['cell_alpha'] = 90.0
    params['cell_beta'] = 90.0
    params['cell_gamma'] = 90.0

    id = mxprocessing.upsert_integration(c, list(params.values()))
    assert id is not None
    assert id > 0

    params = mxprocessing.get_processing_params()
    params['parentid'] = id
    params['spacegroup'] = 'P212121'
    params['refinedcell_a'] = 10
    params['refinedcell_b'] = 10
    params['refinedcell_c'] = 10
    params['refinedcell_alpha'] = 90
    params['refinedcell_beta'] = 90
    params['refinedcell_gamma'] = 90

    id = mxprocessing.upsert_processing(c, list(params.values()))
    assert id is not None
    assert id > 0

    parentid = id
    params1 = mxprocessing.get_inner_shell_scaling_params()
    params2 = mxprocessing.get_outer_shell_scaling_params()
    params3 = mxprocessing.get_overall_scaling_params()
    params1['res_lim_low'] = 2.9
    params1['res_lim_high'] = 1.0
    params1['r_merge'] = 2.1
    params1['cc_half'] = 49.2
    params1['cc_anom'] = 56.0
    params2['res_lim_low'] = 2.9
    params2['res_lim_high'] = 1.0
    params2['r_merge'] = 2.1
    params2['cc_half'] = 49.2
    params2['cc_anom'] = 56.0
    params3['res_lim_low'] = 2.9
    params3['res_lim_high'] = 1.0
    params3['r_merge'] = 2.1
    params3['cc_half'] = 49.2
    params3['cc_anom'] = 56.0
    id = mxprocessing.insert_scaling(c, parentid, list(params1.values()), list(params2.values()), list(params3.values()))

    assert id is not None

    params = mxprocessing.get_quality_indicators_params()
    params['datacollectionid'] = 993677 # only works on dev
    params['image_number'] = 1
    params['spot_total'] = 130
    params['programid'] = programid
    id = mxprocessing.insert_quality_indicators(c, list(params.values()))
    print(id)

    assert id is not None

def upsert_run(c):
    params = mxprocessing.get_run_params()
    params['parentid'] = 596133 # some autoProcScalingId
    params['message'] = 'Just started ...'
    params['pipeline'] = 'dimple v2'
    params['cmd_line'] = 'dimple.sh --input=file.xml'
    run_id = mxprocessing.upsert_run(c, list(params.values()))
    assert run_id is not None
    assert run_id > 0

    params['id'] = run_id
    params['success'] = True
    params['message'] = 'Finished'
    id = mxprocessing.upsert_run(c, list(params.values()))
    assert id is not None
    assert id > 0

    params = mxprocessing.get_run_blob_params()
    params['parentid'] = run_id
    params['view1'] = 'file1.png'
    params['view2'] = 'file2.png'
    params['view3'] = 'file3.png'
    id = mxprocessing.upsert_run_blob(c, list(params.values()))
    assert id is not None
    assert id > 0

def test_insert_integration_and_processing():
    conn = get_connection()
    insert_integration_and_processing(conn)
    conn.disconnect()

def test_dict_upsert_run():
    conn = get_connection()
    upsert_run(conn)
    conn.disconnect()
