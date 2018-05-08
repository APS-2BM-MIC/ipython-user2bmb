print(__file__)

import APS_BlueSky_tools

# Set up default metadata

# IOC is off 2018-05-08
#prop_num = EpicsSignal("2bmS1:ProposalNumber", name="prop_num", string=True)

RE.md['beamline_id'] = '2-BM tomography'
#RE.md['proposal_id'] = str(prop_num.value)
RE.md['pid'] = os.getpid()
RE.md['USER2BMB_ROOT_DIR'] = USER2BMB_ROOT_DIR

import socket 
import getpass 
HOSTNAME = socket.gethostname() or 'localhost' 
USERNAME = getpass.getuser() or 'synApps_xxx_user' 
RE.md['login_id'] = USERNAME + '@' + HOSTNAME
RE.md['BLUESKY_VERSION'] = bluesky.__version__
RE.md['OPHYD_VERSION'] = ophyd.__version__
RE.md['APS_BlueSky_tools_VERSION'] = APS_BlueSky_tools.__version__
RE.md['SESSION_STARTED'] = datetime.isoformat(datetime.now(), " ")

print("Metadata dictionary:")
for k, v in sorted(RE.md.items()):
    print("RE.md['%s']" % k, "=", v)
