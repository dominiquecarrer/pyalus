Module brdfmodels

  ! size of the look-up-table for hemispherical integrals I1 and I2
  Integer, Parameter :: n_table = 18
  ! step width of solar zenith angle (in degrees) in the look-up-table
  Real, Parameter :: theta_step = 5.

  ! look-up-table for hemispherical integrals I1 and I2
  Real, Dimension(0:n_table-1,1:2) :: hint

  ! bi-hemispherical integrals of the model kernel functions
  ! isotropic term, geometric term, volume-scattering term
  Real, Dimension(0:2)             :: bihi_calc

Contains

  Function brdfmodel(theta_obs, phi_del, theta_sun, model)
    Implicit None
  
    Real, Intent(In)     :: theta_obs, phi_del, theta_sun
    Integer, Intent(In)  :: model
    Real, Dimension(0:2) :: brdfmodel
    
    Select Case (model)
    Case (0)
       brdfmodel = roujean(theta_obs, phi_del, theta_sun)
    Case (1)
       brdfmodel = liross(theta_obs, phi_del, theta_sun)    
    Case (2)
       print *,'This kernel case 2 is not used. We do not know which model is used.'
       stop
       brdfmodel = modis(theta_obs, phi_del, theta_sun)
    Case (3)
       brdfmodel = rossthicklisparse(theta_obs, phi_del, theta_sun)
    End Select

  End Function brdfmodel

  ! BRDF kernel model from Roujean, Leroy, and Deschamps (1992)
  Function roujean(theta_obs, phi_del, theta_sun)
    Implicit None
    
    Real, Intent(In)     :: theta_obs, phi_del, theta_sun
    Real, Dimension(0:2) :: roujean
    
    Real, Parameter :: pi           = 3.141592653589793238462643383279502884197
    Real, Parameter :: four_threepi = 4./(3.*pi)
    Real, Parameter :: pi_half      = pi/2.
    Real, Parameter :: one_third    = 1./3.
    Real, Parameter :: one_twopi    = 1./(2.*pi)
    Real, Parameter :: one_pi       = 1./pi
    
    Real :: phi, cos_tobs, cos_tsun, cos_phi, xi, tan_tobs, tan_tsun, cos_xi
  
    ! isotropic term
    roujean(0) = 1.0
    
    ! geometric kernel
    phi = phi_del
    If (phi .lt. 0.) phi = phi + 2.*pi
    If (phi .gt. pi) phi = 2.*pi - phi 
    cos_phi  = Cos(phi)
    tan_tobs = Tan(theta_obs)
    tan_tsun = Tan(theta_sun)
    roujean(1) = one_twopi * ( (pi-phi)*cos_phi+Sin(phi) ) *&
         & tan_tobs*tan_tsun -&
         & one_pi * ( tan_tobs + tan_tsun +&
         &   Sqrt( tan_tobs**2 + tan_tsun**2 - 2*tan_tobs*tan_tsun*cos_phi ) )
    
    ! volume-scattering kernel
    cos_tobs = Cos(theta_obs)
    cos_tsun = Cos(theta_sun)
    cos_xi = cos_tobs*cos_tsun + Sin(theta_obs)*Sin(theta_sun)*cos_phi
    if (cos_xi > 1) cos_xi = 1
    if (cos_xi < -1) cos_xi = -1
    xi = Acos(cos_xi)     
    roujean(2) = four_threepi * ( (pi_half-xi)*Cos(xi)+Sin(xi) ) /&
         & ( cos_tobs+cos_tsun) - one_third
    
  End Function roujean

  ! BRDF kernel model "LiRossHotspot" from Maignan, Br'eon, Lacaze (2004)
  Function liross(theta_obs, phi_del, theta_sun)
    Implicit None
  
    Real, Intent(In)     :: theta_obs, phi_del, theta_sun
    Real, Dimension(0:2) :: liross
    
    Real, Parameter :: pi           = 3.141592653589793238462643383279502884197
    Real, Parameter :: four_threepi = 4./(3.*pi)
    Real, Parameter :: pi_half      = pi/2.
    Real, Parameter :: one_third    = 1./3.
    Real, Parameter :: xi0          = 1.5/180.*pi
  
    Real :: phi, cos_phi, xi, cos_xi, mm, t, cos_t, sin_t
    Real :: cos_tobs, cos_tsun, tan_tobs, tan_tsun
  
    ! isotropic term
    liross(0) = 1.0
  
    ! geometric kernel
    phi = phi_del
    If (phi .lt. 0.) phi = phi + 2.*pi
    If (phi .gt. pi) phi = 2.*pi - phi 
    cos_phi  = Cos(phi)
    cos_tobs = Cos(theta_obs)
    cos_tsun = Cos(theta_sun)
    tan_tobs = Tan(theta_obs)
    tan_tsun = Tan(theta_sun)
    mm = 1./cos_tobs+1./cos_tsun
    cos_t = 2./mm *&
         & Sqrt( tan_tobs**2 + tan_tsun**2 - 2*tan_tobs*tan_tsun*cos_phi +&
         &       (tan_tobs*tan_tsun*Sin(phi))**2 )
    cos_t = Minval( (/cos_t, 1./) )
    t = Acos( cos_t )
    sin_t = sin(t)
    cos_xi = cos_tobs*cos_tsun + Sin(theta_obs)*Sin(theta_sun)*cos_phi
    if (cos_xi > 1) cos_xi = 1
    if (cos_xi < -1) cos_xi = -1
    xi = Acos(cos_xi)
    liross(1) = mm/pi * (t - sin_t*cos_t - pi) +&
         & (1.+cos_xi) / (2*cos_tobs*cos_tsun)

    ! volume-scattering kernel
    liross(2) = four_threepi * ( (pi_half-xi)*cos_xi+Sin(xi) ) *&
         & (1.+1./(1.+xi/xi0)) / (cos_tobs+cos_tsun) - one_third
  
  End Function liross

  ! BRDF kernel model used by MODIS 
  ! (except a constant factor of 3.pi/4. for the volumetric kernel f2)
  Function modis(theta_obs, phi_del, theta_sun)
    Implicit None
    
    Real, Intent(In)     :: theta_obs, phi_del, theta_sun
    Real, Dimension(0:2) :: modis    
    Real, Parameter :: pi           = 3.141592653589793238462643383279502884197
    Real, Parameter :: four_threepi = 4./(3.*pi)
    Real, Parameter :: pi_half      = pi/2.
    Real, Parameter :: one_third    = 1./3.    
    Real :: phi, cos_tobs, cos_tsun, cos_phi, xi, tan_tobs, tan_tsun
    Real :: cos_xi, mm, t, cos_t, sin_t

    ! isotropic term
    modis(0) = 1.0
    
    ! geometric kernel
    phi = phi_del
    If (phi .lt. 0.) phi = phi + 2.*pi
    If (phi .gt. pi) phi = 2.*pi - phi 
    cos_phi  = Cos(phi)
    cos_tobs = Cos(theta_obs)
    cos_tsun = Cos(theta_sun)
    tan_tobs = Tan(theta_obs)
    tan_tsun = Tan(theta_sun)
    mm = 1./cos_tobs+1./cos_tsun
    cos_t = 2./mm *&
         & Sqrt( tan_tobs**2 + tan_tsun**2 - 2*tan_tobs*tan_tsun*cos_phi +&
         &       (tan_tobs*tan_tsun*Sin(phi))**2 )
    cos_t = Minval( (/cos_t, 1./) )
    t = Acos( cos_t )
    sin_t = sin(t)
    cos_xi = cos_tobs*cos_tsun + Sin(theta_obs)*Sin(theta_sun)*cos_phi
    if (cos_xi > 1) cos_xi = 1
    if (cos_xi < -1) cos_xi = -1
    xi = Acos(cos_xi)
    modis(1) = mm/pi * (t - sin_t*cos_t - pi) +&
         & (1.+cos_xi) / (2*cos_tobs*cos_tsun)

    ! volume-scattering kernel
    cos_tobs = Cos(theta_obs)
    cos_tsun = Cos(theta_sun)
    xi = Acos( cos_tobs*cos_tsun +&
         & Sin(theta_obs)*Sin(theta_sun)*cos_phi )
    modis(2) = four_threepi * ( (pi_half-xi)*Cos(xi)+Sin(xi) ) /&
         & ( cos_tobs+cos_tsun) - one_third

  End Function modis

  ! BRDF kernel model used by MODIS (rossthicklisparse)
  Function rossthicklisparse(theta_obs, phi_del, theta_sun)
    Implicit None

    Real, Intent(In)     :: theta_obs, phi_del, theta_sun
    Real, Dimension(0:2) :: rossthicklisparse

    Real, Parameter :: pi           = 3.141592653589793238462643383279502884197
    Real, Parameter :: pi_over_two  = pi/2.
    Real, Parameter :: pi_over_four = pi/4.
    Real, Parameter :: one_two      = 1./2.
    Real, Parameter :: one_pi       = 1./pi

    Real :: phi, cos_tobs, cos_tsun, cos_phi, xi, tan_tobs, tan_tsun, big_O
    Real :: cos_xi, mm, t, cos_t, sin_t

    phi = phi_del
    If (phi .lt. 0.) phi = phi + 2.*pi
    If (phi .gt. pi) phi = 2.*pi - phi

    ! isotropic term
    rossthicklisparse(0) = 1.0

    cos_tobs = Cos(theta_obs)
    cos_tsun = Cos(theta_sun)
    cos_phi  = Cos(phi)

    cos_xi = cos_tobs*cos_tsun + Sin(theta_obs)*Sin(theta_sun)*cos_phi
    if (cos_xi > 1) cos_xi = 1
    if (cos_xi < -1) cos_xi = -1
    xi = Acos(cos_xi)

    mm = 1./cos_tobs+1./cos_tsun

    ! volume-scattering kernel
    tan_tobs = Tan(theta_obs)
    tan_tsun = Tan(theta_sun)
    cos_t = 2./mm *&
         & Sqrt( tan_tobs**2 + tan_tsun**2 - 2*tan_tobs*tan_tsun*cos_phi + &
         &       (tan_tobs*tan_tsun*Sin(phi))**2 )
    cos_t = Minval( (/cos_t, 1./) )
    t = Acos( cos_t )
    sin_t = sin(t)
    big_O = one_pi * mm * (t - sin_t * cos_t)
    ! geometric kernel
    rossthicklisparse(1) = big_O - ((1/cos_tobs)+(1/cos_tsun))  + &
                & one_two * ( 1 + cos_xi ) / (cos_tobs*cos_tsun)

    ! volume-scattering kernel
    rossthicklisparse(2) = (((pi_over_two - xi) * cos_xi + Sin(xi)) &
                          & / (cos_tobs+cos_tsun))  &
                          & - pi_over_four

  End Function rossthicklisparse

  ! select look-up-table
  Subroutine brdfinit(model)
    Implicit None

    Integer, Intent(In) :: model

    ! Roujean, Leroy, and Deschamps (1992)
    Real, Dimension(0:n_table-1,1:2), Parameter :: hint_r = Reshape( &
         (/ -0.997910  , -0.998980  , -1.00197   , -1.00702 ,   -1.01438    , &
         -1.02443   , -1.03773   , -1.05501   , -1.07742 ,   -1.10665    , &
         -1.14526   , -1.19740   , -1.27008   , -1.37595 ,   -1.54059    , &
         -1.82419   , -2.40820   , -4.20369   , &
         -0.00894619, -0.00837790, -0.00665391, -0.00371872,  0.000524714, &
         0.00621877,  0.0135606 ,  0.0228129 ,  0.0343240 ,  0.0485505  , &
         0.0661051 ,  0.0878086 ,  0.114795  ,  0.148698  ,  0.191944   , &
         0.248471  ,  0.325351  ,  0.438371 /), (/ n_table, 2 /) )
    Real, Parameter, Dimension(0:2) :: bihi_calc_r = (/ 1.,-1.28159,8.02838E-02 /)
    
    ! "LiRossHotspot"
    Real, Dimension(0:n_table-1,1:2), Parameter :: hint_l = Reshape( &
         (/ -1.2872    , -1.2883    , -1.29142   , -1.2966  ,   -1.30384    , &
         -1.31307   , -1.3243    , -1.33744   , -1.35237 ,   -1.3689     , &
         -1.38686   , -1.40582   , -1.4253    , -1.44471 ,   -1.46328    , &
         -1.48025   , -1.49538   , -1.51218   , &
         0.0052371 ,  0.00581059,  0.00754731,  0.0105049 ,  0.0147809  , &
         0.0205190 ,  0.0279187 ,  0.0372467 ,  0.0488525 ,  0.0632023  , &
         0.0809112 ,  0.102814  ,  0.130061  ,  0.164302  ,  0.208015   , &
         0.265199  ,  0.343066  ,  0.457749 /), (/ n_table, 2 /) )
    Real, Parameter, Dimension(0:2) :: bihi_calc_l = (/ 1.,-1.37760,9.52950E-02 /)
    
    ! "MODIS"
    Real, Dimension(0:n_table-1,1:2), Parameter :: hint_m = Reshape( &
         (/ -1.2872    , -1.2883    , -1.29142   , -1.2966  ,   -1.30384    , &
         -1.31307   , -1.3243    , -1.33744   , -1.35237 ,   -1.3689     , &
         -1.38686   , -1.40582   , -1.4253    , -1.44471 ,   -1.46328    , &
         -1.48025   , -1.49538   , -1.51218   , &
         -0.00894619, -0.00837790, -0.00665391, -0.00371872,  0.000524714, &
         0.00621877,  0.0135606 ,  0.0228129 ,  0.0343240 ,  0.0485505  , &
         0.0661051 ,  0.0878086 ,  0.114795  ,  0.148698  ,  0.191944   , &
         0.248471  ,  0.325351  ,  0.438371 /), (/ n_table, 2 /) )
    Real, Parameter, Dimension(0:2) :: bihi_calc_m = (/ 1.,-1.37760,8.02838E-02 /)
   !Lisparse Rossthick
    Real, Dimension(0:n_table-1, 1:2), Parameter :: hint_lsrt=Reshape( &
         (/-1.2889 , -1.2899 , -1.293 , -1.2981 , -1.3053 , &
          -1.3145  , -1.3256 , -1.3387, -1.3535 , -1.3698 , &
          -1.3875  , -1.4062 , -1.4253, -1.4441, -1.4618 , &
          -1.4773  , -1.4895 , -1.4973, &
          -0.02107921, -0.01973968, -0.01567785, -0.00876165, 0.00123677, &
           0.01465346, 0.03195199, 0.05375256, 0.08087403, 0.11439660, &
           0.15575623, 0.20689142, 0.27048166, 0.35035791, 0.45226682, &
           0.58545999, 0.76661237, 1.03292777 /), (/n_table, 2 /) )
    
    Real, Parameter, Dimension(0:2) :: bihi_calc_lsrt = (/ 1.,-1.37751,1.89186E-01 /)
    
    Select Case (model)
    Case (0)
       hint = hint_r
       bihi_calc = bihi_calc_r
    Case (1)
       hint = hint_l
       bihi_calc = bihi_calc_l
    Case (2)
       hint = hint_m
       bihi_calc = bihi_calc_m
    Case (3)
       hint = hint_lsrt
       bihi_calc = bihi_calc_lsrt
    End Select

  End Subroutine brdfinit

End Module brdfmodels
