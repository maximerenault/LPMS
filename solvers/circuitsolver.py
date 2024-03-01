class CircuitSolver:
    def __init__(self) -> None:
        self.circM1 = None
        self.circM0 = None
        self.circSource = None
        self.dt = 1.0
        # Backwards Differentiation Formula
        self.time_integrations = ["BDF", "BDF2"]
        self.time_integration = None

    def set_dt(self, dt):
        self.dt = dt
        
    def get_dt(self):
        return self.dt

    def set_time_integration(self, ti):
        self.time_integration = ti

    def buildLHS(self, paths,) -> None:

        return
