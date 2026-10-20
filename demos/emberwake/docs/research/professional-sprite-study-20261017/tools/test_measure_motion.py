"""Analytic checks for the actual geometric/held-frame claims, not art scoring."""
import unittest
import numpy as np
from measure_motion import stance_fit

class ConditionalFitTests(unittest.TestCase):
    def test_known_boundary_contact_does_not_mean_held_contact(self):
        phase=[0,.125,.25,.375]
        points=[[20-16*p,30] for p in phase]
        r=stance_fit(phase,points,[1,0],64)
        self.assertAlmostEqual(r['fitted_root_pixels_per_cycle'],16)
        self.assertAlmostEqual(r['boundary_residual_rms_px'],0,places=10)
        # If cycle is.8sec and this exposure is.1sec, a held pose moves2px.
        self.assertAlmostEqual(r['fitted_root_pixels_per_cycle']/.8*.1,2)
    def test_diagonal_projection_and_lateral_residual(self):
        phase=np.array([0,.1,.3,.6]);d=np.array([1,-1])/np.sqrt(2)
        p=np.array([10,20])-phase[:,None]*24*d
        r=stance_fit(phase,p,[1,-1],48)
        self.assertAlmostEqual(r['fitted_root_heights_per_cycle'],.5)
        self.assertLess(r['boundary_residual_rms_px'],1e-10)
        p[:,0]+=[0,1,-1,0]
        self.assertGreater(stance_fit(phase,p,[1,-1],48)['boundary_residual_rms_px'],0)
    def test_wrong_hypothesized_direction_is_not_clamped(self):
        r=stance_fit([0,.1,.2],[[0,0],[1,0],[2,0]],[1,0],10)
        self.assertLess(r['fitted_root_pixels_per_cycle'],0)
        self.assertFalse(r['direction_contact_hypothesis_consistent_with_forward_motion'])

if __name__=='__main__':unittest.main()
