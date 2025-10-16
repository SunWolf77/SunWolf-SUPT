import pandas as pd
import numpy as np

def compute_metrics(cf_df, vulc_df, kp_index):
    """Simplified SUPT core metrics."""
    def shallow_ratio(df): return (df['depth'] < 3).mean()
    cf_sr, vulc_sr = shallow_ratio(cf_df), shallow_ratio(vulc_df)
    eii = 0.5 * (cf_sr + vulc_sr) * (1 + min(kp_index/7, 0.25))
    status = "ELEVATED" if eii > 0.55 else "NORMAL"
    return dict(EII=round(eii,3), RPAM=status,
                psi_scale=round(1+min(kp_index/28,0.25),3))
