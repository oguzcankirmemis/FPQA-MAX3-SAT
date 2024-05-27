class FPQA:
    def __init__(self,  slm: SLM, aod: AOD, slm_atoms: list[tuple[int]], aod_atoms: list[tuple[int]], ):
        self.aod = aod
        self.slm = slm
        for atom in slm_atoms:
            self.slm.toggle(slm_atoms[0], slm_atoms[1])
        for atom in aod_atoms:
            