def nmr_1to1(params, xdata, *args, **kwargs):
    """
    Calculates predicted [HG] given parameters and x data as input
    """

    k = params[0]

    h0 = xdata[0]
    g0 = xdata[1]

    # Calculate predicted [HG] concentration given input [H]0, [G]0 matrices
    # and Ka guess
    hg = 0.5*(\
        (g0 + h0 + (1/k)) - \
        np.lib.scimath.sqrt(((g0+h0+(1/k))**2)-(4*((g0*h0))))\
    )
    h  = h0 - hg

    # Replace any non-real solutions with sqrt(h0*g0) 
    inds = np.imag(hg) > 0
    hg[inds] = np.sqrt(h0[inds] * g0[inds])

    # Convert [HG] concentration to molefraction for NMR
    hg /= h0
    h  /= h0

    # Make column vector
    hg_mat_fit = np.vstack((h, hg))
    hg_mat     = np.vstack((h, hg))

    return hg_mat_fit, hg_mat
