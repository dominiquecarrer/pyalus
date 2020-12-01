Recursive Subroutine brdfwrapper(brdfmodellocal, errcode, errmsg, debuglevel,theta_obs, phi_del, theta_sun, model)
    Use brdfmodels
    Character (Len=1024) :: errmsg
    Integer :: errcode
    Real, Intent(In)     :: theta_obs, phi_del, theta_sun
    Integer, Intent(In)  :: model
    Real, Dimension(0:2), Intent(Out):: brdfmodellocal
    !f2py intent(out) errmsg
    !f2py intent(out) errcode
    !f2py intent(out) brdfmodellocal
    errcode = 0
    errmsg = ''
    if (debuglevel .gt. 0) print *, theta_sun
    brdfmodellocal(:) = brdfmodel(theta_obs, phi_del, theta_sun, model)
    if (debuglevel .gt. 0) print *, brdfmodellocal
End Subroutine brdfwrapper
