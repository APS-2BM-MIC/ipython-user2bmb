print(__file__)

import APS_BlueSky_tools

# Set up default metadata


@property
def ipython_profile_name():
    """
    return the name of the current ipython profile or `None`
    
    Example (add to default RunEngine metadata)::

        RE.md['ipython_profile'] = str(ipython_profile_name)

"""
    import IPython.paths
    import IPython.core.profileapp
    import IPython.core.profiledir
    
    path = IPython.paths.get_ipython_dir()
    ipd = IPython.core.profiledir.ProfileDir()
    for p in IPython.core.profileapp.list_profiles_in(path):
        pd = ipd.find_profile_dir_by_name(path, p)
        if os.path.dirname(__file__) == pd.startup_dir:
            return p


RE.md['beamline_id'] = '2-BM tomography'
RE.md['ipython_profile'] = str(ipython_profile_name)
print("using profile: " + RE.md['ipython_profile'])

try:
    # IOC is off 2018-05-08 for switchgear maintenance
    prop_num = EpicsSignal("2bmS1:ProposalNumber", name="prop_num", string=True)
    RE.md['proposal_id'] = str(prop_num.value)
except Exception as _exc:
    print(_exc)

RE.md['pid'] = os.getpid()
RE.md['USER2BMB_ROOT_DIR'] = USER2BMB_ROOT_DIR

import socket 
import getpass 
HOSTNAME = socket.gethostname() or 'localhost' 
USERNAME = getpass.getuser() or '2-BM-B user' 
RE.md['login_id'] = USERNAME + '@' + HOSTNAME
RE.md['BLUESKY_VERSION'] = bluesky.__version__
RE.md['OPHYD_VERSION'] = ophyd.__version__
RE.md['APS_BlueSky_tools_VERSION'] = APS_BlueSky_tools.__version__
RE.md['SESSION_STARTED'] = datetime.isoformat(datetime.now(), " ")

print("Metadata dictionary:")
for k, v in sorted(RE.md.items()):
    print("RE.md['%s']" % k, "=", v)
