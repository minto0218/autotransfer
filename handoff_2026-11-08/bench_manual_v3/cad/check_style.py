"""Check that rounded shaping retains the mounting, spring and idler supports."""
import json
import build as b
b.make_parts();s=b.PARTS['spring_cassette'];pts={
 'mount_left':(-9,-35,40.5),'mount_right':(9,-35,40.5),
 'curved_rib_centre':(18.9375,-30.625,37),'upper_plate_neck':(23,-12,36),
 'grip_hook_surround':(23,19.2,14.65),'twist_hook_surround':(23,19.2,21.6),'press_hook_surround':(23,19.2,25.1)}
for z in(14.65,21.6,25.1):
 pts['lower_idler_'+str(z)]=(14,-26,z-1.2);pts['upper_idler_'+str(z)]=(14,-26,z+1.2)
checks={n:s.isInside(p,1e-6)for n,p in pts.items()};bb=s.BoundingBox();rep=dict(scope=__doc__,support_control_points=checks,solids=len(s.Solids()),plate_outer_x_mm=24.5,bbox_tolerance_mm=.01,maximum_x_mm=bb.xmax,pass_=all(checks.values())and len(s.Solids())==1 and bb.xmax<=24.51)
(b.OUT/'validation/style.json').write_text(json.dumps(rep,indent=2));print('STYLE_PASS',rep['pass_'],checks,flush=True)
if not rep['pass_']:raise SystemExit(1)
