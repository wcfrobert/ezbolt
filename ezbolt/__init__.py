"""
ezbolt is a package that can be used to calculate in-plane forces in a bolt-group.
It does so using three methods: elastic method, elastic center of rotation method,
and the instant center of rotation method.
"""

__version__ = "0.1.0"
__author__ = "Robert Wang"
__license__ = "MIT"

from ezbolt.boltgroup import BoltGroup
from ezbolt.plotter import (preview, 
                            plot_elastic, 
                            plot_ECR, 
                            plot_ICR, 
                            plot_ICR_anim)