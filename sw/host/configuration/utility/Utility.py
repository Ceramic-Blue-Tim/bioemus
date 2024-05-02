from fxpmath import Fxp

class SFI_ENC:
    WIDTH = 0
    DEC   = 0

    def __init__(self, width, dec) -> None:
        self.WIDTH  = width
        self.DEC    = dec

class SFI:
    G            = SFI_ENC(width = 27, dec =  23)
    V            = SFI_ENC(width = 32, dec =  23)
    E            = SFI_ENC(width = 32, dec =  23)
    CUR          = SFI_ENC(width = 32, dec =  23)
    ION          = SFI_ENC(width = 27, dec =  25)
    V_TRUNC      = SFI_ENC(width = 18, dec =  10)
    CUR_TRUNC    = SFI_ENC(width = 18, dec =  10)
    MU           = SFI_ENC(width = 18, dec =  10)
    THETA        = SFI_ENC(width = 18, dec =  16)
    SIGMA        = SFI_ENC(width = 18, dec =  16)
    BRATE_SYN    = SFI_ENC(width = 12, dec =  10)
    TRATE_SYN    = SFI_ENC(width = 18, dec =  16)
    WSYN         = SFI_ENC(width = 14, dec =  12)
    GSYN         = SFI_ENC(width = 18, dec =  16)
    ESYN         = SFI_ENC(width = 18, dec =  10)
    SYN          = SFI_ENC(width = 18, dec =  16)
    SN_GABAB_IN  = SFI_ENC(width = 18, dec = -24)
    SN_GABAB_OUT = SFI_ENC(width = 18, dec =  16)
    PMUL_GSYN    = SFI_ENC(width = 18, dec =  16)

def writeFPGASimFile(gen_fpga_sim_files, fname, rate, length, FP_WIDTH, FP_DEC):
    """Write FPGA simulation files"""
    if gen_fpga_sim_files:
        with open(fname, "w") as f:
            for i in range(length): f.write(str(Fxp(rate[i], signed=True, n_word=FP_WIDTH, n_frac=FP_DEC).val) + "\n")

def writeFPGASimFileFloat(gen_fpga_sim_files, fname, rate, length):
    """Write FPGA simulation files"""
    if gen_fpga_sim_files:
        with open(fname, "w") as f:
            for i in range(length): f.write(str(rate[i]) + "\n")

def forwardEuler(dx, xpre, dt):
    return xpre + dx*dt