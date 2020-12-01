Recursive Subroutine MODEL_FIT (errcode, errmsg, debuglevel, &
      & sat_specific, &
      & enable_normalisation, &
      & brdf, covariance, quality,&
      & brdf1, covariance1, quality1, &
      & age_out, &
      & snow_mask_out, &
      & n_valid_obs_out, &
      & lwcs_mask, lwcs_mask_missing, &
      & latitude, longitude, &
      & debuginfo, &
      & spectral_normalisation, &
      & spectral_normalisation_err, &
      & recursion, &
      & startseries, &
      & composition, &
      & theta_sat_limit, &
      & theta_sol_limit, &
      & theta_sat_wlimit, &
      & theta_sol_wlimit, &
      & bad_CMa_elim, &
      & bad_CMa_factor, &
      & shadow_elim, &
      & shadow_factor, &
      & par_max, par_min, &
      & cxx_max ,cxx_min, &
      & cxy_max ,cxy_min, &
      & sig_nadir_a, &
      & sig_nadir_b, &
      & sigrefl_min, &
      & sigrefl_max, &
      & typical_cov_rescale_values, &
      & angle_index, &
      & k_reg, &
      & sig_k_reg, &
      & N_slot_elim, &
      & N_obs_limit, &
      & snow_flag_one, &
      & timescale , &
      & model , &
      & day_of_year, &
      & days_last_in, &
      & zenith_sat,   &
      & azimuth_sat,  &
      & zenith_sol,   &
      & azimuth_sol,  &
      & reflectance,  &
      & reflectance_cov,  &
      & scenesdatetimes, &
      & currentdatetime, &
      & quality_in, age_obs_in, &
      & brdf_in,  &
      & covariance_in, &
      & brdf_clim,  &
      & covariance_clim, &
      & brdf_clim_activated, &
      & refl_outliers_elim_param1, &
      & refl_outliers_elim_param2, &
      & refl_outliers_elim_band_ref, & != 2
      & refl_outliers_elim_band_in, & != 1
      & xstart, xend, ystart, yend,&
      & ndvi_nir, ndvi_red, &
      & ndvi2_nir, ndvi2_red, &
      & n_debuginfo, &
      & MSGpixX, Lines, N_channels_in, N_channels_ref, N_scenes, MM)

    Use algoconf
    Use brdfmodels

    Implicit None

    Character (Len=1024) :: errmsg
    Integer              :: errcode
    Integer, Intent (In) :: debuglevel

    Integer, Intent (In) :: sat_specific
    Logical, Intent (In) :: enable_normalisation ! if True, perform spectral normalisation, if False, don't.

    ! days since the last execution of the algorithm
    Real, Intent(In) :: days_last_in

    ! matrices dimensions
    Integer, Intent (In) :: MSGpixX
    Integer, Intent (In) :: Lines
    Integer, Intent (In) :: N_channels_in  ! number of channels/bands before normalisation
    Integer, Intent (In) :: N_channels_ref ! number of channels/bands after normalisation (this is 4 for VGT)
    Integer, Intent (In) :: N_scenes
    Integer, Intent(in)   :: MM
    Integer, Intent(in)   :: n_debuginfo
    integer, Intent(In) :: ndvi_nir
    integer, Intent(In) :: ndvi_red
    integer, Intent(In) :: ndvi2_nir
    integer, Intent(In) :: ndvi2_red
    
    Integer, Intent(In)   :: xstart, xend, ystart, yend ! window to process
    Integer (Kind=quakind), Dimension (1:MSGpixX, 1:Lines,1:N_channels_in, 1:N_scenes), Intent (In) :: lwcs_mask 
    Integer (Kind=quakind), Intent (In) :: lwcs_mask_missing

    ! spectral normalisation coefficients
    !!Real, Dimension(1:2,1:N_channels_ref, 0:N_channels_in ), Intent(In)      :: spectral_normalisation old version
    Real, Dimension(1:2,1:N_channels_ref, 0:3 ), Intent(In)                  :: spectral_normalisation_err 

    Real, Dimension(1:2,1:N_channels_ref, 0:N_channels_in,1:4), Intent(In)      :: spectral_normalisation

    ! input reflectances
    Real (Kind=4), Dimension (1:MSGpixX, 1:Lines,1:N_channels_in, 1:N_scenes), Intent (In) :: reflectance
    Real (Kind=4), Dimension (1:MSGpixX, 1:Lines,1:N_channels_in, 1:N_scenes), Intent (In) :: reflectance_cov
    Integer (Kind=8), Intent(In) :: currentdatetime
    Integer (Kind=8), Dimension (1:N_scenes), Intent (In) :: scenesdatetimes
    ! input a priori
    Real (Kind=4), Dimension (1:MSGpixX, 1:Lines,1:N_channels_ref,0:MM),        Intent(In) :: brdf_in
    Real(Kind=4), Dimension(1:MSGpixX, 1:Lines,1:N_channels_ref,0:MM,0:MM),     Intent(In) :: covariance_in ! TODO 0:MM and not 1:MM ?
    Integer (Kind=quakind), Dimension (1:MSGpixX, 1:Lines,1:N_channels_ref),    Intent(In) :: quality_in
    Integer (Kind=agekind), Dimension (1:MSGpixX, 1:Lines,1:N_channels_ref),    Intent(In) :: age_obs_in
    
    ! input climatic 
    Real (Kind=4), Dimension (1:MSGpixX, 1:Lines,1:N_channels_ref,0:MM),        Intent(In) :: brdf_clim
    Real(Kind=4), Dimension(1:MSGpixX, 1:Lines,1:N_channels_ref,0:MM,0:MM),     Intent(In) :: covariance_clim ! TODO 0:MM and not 1:MM ?
    
    ! input auxiliary data
    Real(Kind=realkind), Dimension(1:MSGpixX, 1:Lines),                    Intent(In) :: latitude
    Real(Kind=realkind), Dimension(1:MSGpixX, 1:Lines),                    Intent(In) :: longitude
    Integer(Kind=realkind), Dimension(1:n_debuginfo),                           Intent(In) :: debuginfo
    Real (Kind=4), Dimension (1:MSGpixX, 1:Lines,1:N_channels_in,1:N_scenes),  Intent (In) :: azimuth_sat
    Real (Kind=4), Dimension (1:MSGpixX, 1:Lines,1:N_scenes),                   Intent (In) :: azimuth_sol
    Real (Kind=4), Dimension (1:MSGpixX, 1:Lines,1:N_channels_in,1:N_scenes),  Intent (In) :: zenith_sat
    Real (Kind=4), Dimension (1:MSGpixX, 1:Lines,1:N_scenes),                   Intent (In) :: zenith_sol



    Integer, Intent(In)  :: model             ! 0=Roujean et al., 1="LiRossHotspot"
    Integer, Intent (In) :: day_of_year     ! day of the year
    Logical, Intent (In) :: recursion         ! .true. = generate recursive result based on previous estimate
    Logical, Intent (In) :: startseries       ! .true. = start the recursive sequence
    Logical, Intent (In) :: composition       ! .true. = generate one-day composition result
    Integer, Intent (In) :: N_slot_elim       ! number of slots eliminated next to cloudy slots
    Integer, Intent (In) :: N_obs_limit       ! minimal number of observations
    Logical, Intent (In) :: snow_flag_one     ! .true. = one "snowy" slot suffices to set snow flag
    Real, Intent (In)    :: timescale         ! characteristic time scale of temporal composition (in days)
    Logical, Intent(In)  :: bad_CMa_elim      ! .true. = eliminate reflectances with bad cloud mask quality
    Real, Intent(In)     :: bad_CMa_factor    ! penalisation factor for observations with bad cloud mask quality
    Logical, Intent(In)  :: shadow_elim       ! .true. = eliminate observations marked with shadow flag
    Real, Intent(In)     :: shadow_factor     ! penalisation factor for observations marked with shadow flag

    Real(Kind=realkind), Intent (In) :: theta_sat_limit
    Real(Kind=realkind), Intent (In) :: theta_sol_limit
    Real(Kind=realkind), Intent (In) :: theta_sat_wlimit
    Real(Kind=realkind), Intent (In) :: theta_sol_wlimit

    Real, Intent(In) :: par_max    ! maximum value for kernel parameters
    Real, Intent(In) :: par_min    ! minimum value for kernel parameters
    Real, Intent(In) :: cxx_max    ! maximum value for diagonal covariance matrix elements
    Real, Intent(In) :: cxx_min    ! minimum value for diagonal covariance matrix elements
    Real, Intent(In) :: cxy_max    ! maximum value for other covariance matrix elements
    Real, Intent(In) :: cxy_min    ! minimum value for other covariance matrix elements
    Real, Dimension(1:N_channels_ref), Intent(In)      :: sig_nadir_a
    Real, Dimension(1:N_channels_ref), Intent(In)      :: sig_nadir_b
    Real, Dimension(1:N_channels_ref), Intent(In)      :: typical_cov_rescale_values    
    Real, Dimension(1:N_channels_ref), Intent(In)      :: angle_index    
    Real, Intent(In) :: sigrefl_min          ! lower limit for reflectance error estimates
    Real, Intent(In) :: sigrefl_max          ! upper limit for reflectance error estimates
    ! regularisation for model parameters
    Real, Dimension(0:MM,1:N_channels_ref), Intent(In)     :: k_reg
    Real, Dimension(0:MM,1:N_channels_ref), Intent(In)     :: sig_k_reg

    Real, Intent(In):: refl_outliers_elim_param1
    Real, Intent(In):: refl_outliers_elim_param2
    Integer, Intent(In) :: refl_outliers_elim_band_ref
    Integer, Intent(In) :: refl_outliers_elim_band_in

    ! output : brdf data (with a priori and daily, and additional info)
    Real (Kind=4), Dimension(1:MSGpixX, 1:Lines,1:N_channels_ref, 0:MM),       Intent(InOut) :: brdf
    Real (Kind=4), Dimension(1:MSGpixX, 1:Lines,1:N_channels_ref, 0:MM),       Intent(InOut) :: brdf1
    Real (Kind=4), Dimension(1:MSGpixX, 1:Lines,1:N_channels_ref, 0:MM, 0:MM), Intent(InOut) :: covariance
    Real (Kind=4), Dimension(1:MSGpixX, 1:Lines,1:N_channels_ref, 0:MM, 0:MM), Intent(InOut) :: covariance1
    Integer(Kind=quakind), Dimension(1:MSGpixX,1:Lines,1:N_channels_ref),      Intent(InOut) :: quality
    Integer(Kind=quakind), Dimension(1:MSGpixX,1:Lines,1:N_channels_ref),      Intent(InOut) :: quality1
    Integer(Kind=agekind), Dimension(1:MSGpixX,1:Lines,1:N_channels_ref),      Intent(InOut) :: age_out
    Integer (Kind=1), Dimension(1:MSGpixX, 1:Lines),                       Intent(InOut) :: snow_mask_out
    Integer (Kind=1), Dimension(1:MSGpixX, 1:Lines,1:N_channels_ref),          Intent(InOut) :: n_valid_obs_out

    !f2py intent(in,hide) n_debuginfo
    !f2py intent(in,hide) Lines
    !f2py intent(in,hide) MSGpixX
    !f2py intent(in,hide) N_channels_in
    !f2py intent(in,hide) N_channels_ref
    !f2py intent(in,hide) N_scenes
    !f2py intent(in,hide) MM
    !f2py intent(out) errmsg
    !f2py intent(out) errcode

    ! Local variables

    Logical, Dimension(1:N_channels_ref) :: valids  ! validity of spectral albedo estimates
    Real (Kind=4), Dimension (0:MM) :: kernels_values
    ! variables for linear model inversion
    Real, Dimension(1:N_scenes,0:MM):: A
    Real, Dimension(0:MM,1:N_scenes):: AT
    Real, Dimension(1:N_scenes)    :: b
    ! variables for linear model inversion
    Real, Dimension(0:MM)      :: k         ! model parameters
    Real, Dimension(0:MM,0:MM) :: Ck        ! covariance matrix of the k estimate
    Real, Dimension(0:MM,0:MM) :: CkI       ! inverse of the covariance matrix of the k estimate
    Real, Dimension(0:MM,0:MM) :: ATA       ! matrix ATA
    Real, Dimension(0:MM)      :: k_in      ! previous estimate for k parameters
    Real, Dimension(0:MM,0:MM) :: Ck_in     ! covariance matrix of previous estimate
    Real, Dimension(0:MM,0:MM) :: CkI_in    ! inverse of covariance matrix of previous estimate
    Real, Dimension(0:MM,0:MM) :: CkI_reg   ! inverse of regularisation covariance matrix
    Real, Dimension(0:MM,0:MM) :: sqcvm     ! square root of cov. matrix elements
    Real, Dimension(0:MM)      :: k_clim_in      ! Climatologic estimate for k parameters
    Real, Dimension(0:MM,0:MM) :: Ck_clim_in     ! covariance matrix of climatologic brdf k parameters
    Real, Dimension(0:MM,0:MM) :: CkI_clim_in     ! covariance matrix of climatologic brdf k parameters
   
    ! directional-hemispherical integrals of the model kernel functions
    Logical, Dimension(1:N_scenes)            :: ang_ok, processed
    Real, Dimension(1:N_scenes)               :: refl, refl_cov_tmp
    Real, Dimension(1:N_channels_ref, 1:N_scenes):: sigrefl
    Real, Dimension(1:N_channels_in, 1:N_scenes) :: nreflect_in
    Real, Dimension(1:N_scenes) :: nreflect_in_one_band
    Real, Dimension(1:N_scenes) :: distances
    Real, Dimension(1:N_channels_in, 1:N_scenes) :: nreflect_cov_in
    Real, Dimension(1:N_channels_ref, 1:N_scenes) :: nreflect_ref
    Real, Dimension(1:N_channels_ref, 1:N_scenes) :: nreflect_cov_ref
    Integer (Kind=quakind), Dimension(1:N_channels_ref, 1:N_scenes) :: lwcs_mask_ref

    Real, Dimension(1:N_channels_ref, 1:N_scenes) :: theta_sat_ref
    Real, Dimension(1:N_channels_ref, 1:N_scenes) :: phi_del_ref

    ! mathematical constants
    Real, Parameter :: pi      = 3.141592653589793238462643383279502884197
    Real, Parameter :: two_pi  = 2.*pi
    Real, Parameter :: pi_half = pi/2.
    Real, Parameter :: rad     = pi/180.

    Real(Kind=realkind) :: lat
    Integer(Kind=maskind)   :: lw_mask ! auxiliary variable for land/water mask
    Integer :: X,Y, NN, N, I, J, I_in, I_out, I_inb

    Real :: t_sat_lim       ! satellite zenith angle limit (in radians)
    Real :: t_sol_lim       ! solar zenith angle limit (in radians)
    Real :: t_sat_wlim      ! limit for weighting equation (in radians)
    Real :: t_sol_wlim      ! limit for weighting equation (in radians)

    Integer, Dimension(:), Allocatable :: scenes_age

    Integer,    Dimension(1:N_scenes) :: mask_cma
    Logical,    Dimension(1:N_scenes) :: cloudy
    Logical,    Dimension(1:N_scenes) :: snowy
    Logical,    Dimension(1:N_scenes) :: bad_cma
    Logical,    Dimension(1:N_scenes) :: shadow
    Logical,    Dimension(1:N_scenes) :: refl_is_outlier
    Logical,    Dimension(1:N_scenes) :: valid
    Logical,    Dimension(1:N_scenes) :: valid0

    Integer :: age_max = huge(int(0,agekind))
    Integer :: age          ! "age" of last observation used
    Integer :: N_valid      ! number of valid !--NL
    Integer :: N_valid_obs  ! number of valid observations in time series
    Integer :: N_valid_snow ! number of valid observations with snow flag set
    Integer :: N_snow_limit ! minimum number for setting the snow flag
    Real    :: delta, ndvi_in, ndvi2

    Real,    Dimension(1:N_channels_in, 1:N_scenes) :: theta_sat
    Real,    Dimension(1:N_scenes) :: theta_sol
    Real,    Dimension(1:N_channels_in,1:N_scenes) :: t_sat_rel
    Real,    Dimension(1:N_scenes) :: t_sol_rel
    Real,    Dimension(1:N_channels_in, 1:N_scenes) :: phi_sat
    Real,    Dimension(1:N_scenes) :: phi_sol
    Real,    Dimension(1:N_channels_in,1:N_scenes) :: phi_del
    Real,    Dimension(1:N_channels_in,1:N_scenes) :: wi_angular

    Logical :: observations ! .true. if a sufficient number of observations are available
    Logical :: previous     ! .true. if previous estimate is available
    Logical :: snow         ! .true. if pixel is declared as snow covered
    Logical :: brdf_clim_activated      ! .true. if climatologic brdf are used
    Integer :: snow_mask

    Real :: cov_aux         ! auxiliary variable for covariance elements
    Real :: typical_value
    Real,  Dimension(1:N_scenes) :: refl_estimate
    Real :: maxdistance
    Real :: mean, variance, stdev
    Real :: sum_, sum_squares, tmp

    Real :: nan, nanhelper

    ! interface for matrix inversion
    Interface
         ! to do dim2 and dim3 hardcoded inverse (faster)
         Function invers_lapack (A)
            Real, Dimension (:, :), Intent (In) :: A
            Real, Dimension (Size(A, 1), Size(A, 1)) :: Ainv
      End Function invers_lapack
    End Interface

    nanhelper = 0.
    nan = nanhelper / nanhelper ! used to set a nan value

    If (debuglevel .ge. 10) print *, '---------------'
    If (debuglevel .ge. 10) print *, 'Entering model_fit.f90'

    errcode = 0
    errmsg = ''
    ! transform angle limits to radians
    t_sat_lim = theta_sat_limit * rad
    t_sol_lim = theta_sol_limit * rad
    t_sat_wlim = theta_sat_wlimit * rad
    t_sol_wlim = theta_sol_wlimit * rad

    ! calculate relative increment of covariance matrix
    delta = 2.**(2./timescale) - 1.

     If (debuglevel .ge. 200) print *, 'N_scenes =  ', N_scenes
     Do Y = ystart, yend
        Do X = xstart, xend
           If (debuglevel .ge. 100) print *, '--- Pixel loop --- YX=',Y,X,'lat/lon = ',latitude(X,Y),longitude(X,Y)
           If (debuglevel .ge. 10000) print *, '--- ',debuginfo
           If (debuglevel .ge. 500) print *, 'lwcs_mask=',lwcs_mask(X,Y,:,:)
           
           ! determine the valid observations in the time series
           ! extract time series and apply the scale factors
           ang_ok = .not. (isnan(zenith_sat(X,Y, 1,:))  .or. &
                       &   isnan(zenith_sol(X,Y,:))  .or. &
                       &   isnan(azimuth_sat(X,Y, 1,:)) .or. &
                       &   isnan(azimuth_sol(X,Y,:)) )

           ! propagate land/water mask information from the lastest valid input scene
           lw_mask = IAND(quality_in(X,Y,1) , int(B'00000011',quakind)) ! if no valid observation take the one in previous brdf (if this is also not available, take the initial value of quality_in)
           Do N = N_scenes,1, -1 ! decreasing loop to take the latest valid land-water mask
              If (debuglevel .ge. 300) print *, 'Mask from scene', N, '=',lwcs_mask(X,Y,1,N), IAND(lwcs_mask(X,Y,1,N), int(B'00000011', quakind)), lwcs_mask_missing
              If (ang_ok(N) .and. (lwcs_mask(X,Y,1,N) .ne. lwcs_mask_missing) ) Then
                  lw_mask = IAND(lwcs_mask(X,Y,1,N), int(B'00000011',quakind))
                  If (debuglevel .ge. 300) print *, 'Taking mask from scene', N, ':',lwcs_mask(X,Y,1,N), '-> lw_mask=', lw_mask
                  If (debuglevel .ge. 500) print *, lwcs_mask(X,Y,1,N),' && 00000001=',IAND(lwcs_mask(X,Y,1,N), B'00000001')
                  If (debuglevel .ge. 500) print *, lwcs_mask(X,Y,1,N),' && 00000010=',IAND(lwcs_mask(X,Y,1,N), B'00000010')
                  If (debuglevel .ge. 500) print *, lwcs_mask(X,Y,1,N),' && 00000100=',IAND(lwcs_mask(X,Y,1,N), B'00000100')
                  If (debuglevel .ge. 500) print *, lwcs_mask(X,Y,1,N),' && 00001000=',IAND(lwcs_mask(X,Y,1,N), B'00001000')
                  If (debuglevel .ge. 500) print *, lwcs_mask(X,Y,1,N),' && 00010000=',IAND(lwcs_mask(X,Y,1,N), B'00010000')
                  If (debuglevel .ge. 500) print *, lwcs_mask(X,Y,1,N),' && 00100000=',IAND(lwcs_mask(X,Y,1,N), B'00100000')
                  exit ! exit the N loop
              End If
           End Do

           If ( recursion ) Then
              !!! beware : they are 3 qualities : for brdf, for brdf1 and for the final albedo
              quality(X,Y,:) = lw_mask
              If (debuglevel .ge. 250) print *, 'Set quality from lw_mask= ', quality(X,Y,:), 'lw_mask=',lw_mask
              !quality_al(X,Y,:) = lw_mask ! NB: TODO quality_al lw_mask is done here instead of in the integration
           End If
           If ( composition ) quality1(X,Y,:) = lw_mask
           If (debuglevel .ge. 250) print *, 'Set quality1 from lw_mask= ', quality1(X,Y,:), 'lw_mask=',lw_mask


           ! check for continental pixels, if yes do the inversion
           If (debuglevel .ge. 200) print *, 'Mask', lw_mask, 'inlandwater=',MLW_WATER,'land=',MLW_LAND
           If ((N_scenes .gt. 0) .and. .not. ( lw_mask .eq. MLW_WATER .or. lw_mask .eq. MLW_LAND  ))  Then
                If (debuglevel .ge. 200) print *, 'Cycling (skipping pixel) : mask is water or land, lw_mask=', lw_mask
                cycle
           End If

           lat = latitude(X,Y)
           If (debuglevel .ge. 200) print *, 'lat', lat, isnan(lat)
           If ((N_scenes .gt. 0) .and. isnan(lat) )  Then
                If (debuglevel .ge. 200) print *, 'Cycling (skipping pixel) : lat = nan ', lat
                cycle
           End If
           If (debuglevel .ge. 110) print *, 'Processing pixel YX=',Y,X

           ! determine the valid observations in the time series
           ! extract time series and apply the scale factors
           Do I = 1, N_channels_in
               Where ( ang_ok )
                  theta_sat(I,:) = zenith_sat(X,Y,I,:) * rad
                  t_sat_rel(I,:) = theta_sat(I,:)/t_sat_wlim
                  Where ( t_sat_rel(I,:) .gt. 0.999 ) t_sat_rel(I,:) = 0.999
                  theta_sol = zenith_sol(X,Y,:) * rad
                  t_sol_rel = theta_sol/t_sol_wlim
                  Where ( t_sol_rel .gt. 0.999 ) t_sol_rel = 0.999
                  phi_sat(I,:)   = azimuth_sat(X,Y,I,:) * rad
                  Where(phi_sat(I,:) .gt. two_pi) phi_sat(I,:) = two_pi
                  phi_sol   = azimuth_sol(X,Y,:) * rad
                  Where(phi_sol .gt. two_pi) phi_sol = two_pi
                  phi_del(I,:)   = phi_sat(I,:) - phi_sol
                  Where(phi_del(I,:) .lt. 0.) phi_del(I,:) = phi_del(I,:) + two_pi
                  ! calculate angular weight via airmass
                  wi_angular(I,:)  = 0.5 * ( 1./Cos(t_sat_rel(I,:)*pi_half) +&
                       &                1./Cos(t_sol_rel*pi_half) )
               End Where
           End Do
           
           If (debuglevel .ge. 180) print *, 'ang_ok (1)', ang_ok
           ang_ok = ( ang_ok .and. &
                &    theta_sol .le. t_sol_lim .and. theta_sat(1,:) .le. t_sat_lim )
           If (debuglevel .ge. 580) print *, 'theta_sol',theta_sol, '<', t_sol_lim
           If (debuglevel .ge. 180) print *, 'theta_sat',theta_sat(1,:), '<', t_sat_lim
           If (debuglevel .ge. 180) print *, 'ang_ok (2)', ang_ok

           If ( .not. startseries ) Then
              Do I = 1, N_channels_in
                 Select Case (sat_specific)
                 Case (0) ! MSG
                     previous = any(BTest( quality_in(X,Y,:), BIT_MSG ) .and. .not. BTest( quality_in(X,Y,:), BIT_FAILS ))
                 Case (1) ! EPS
                     previous = any(BTest( quality_in(X,Y,:), BIT_EPS ) .and. .not. BTest( quality_in(X,Y,:), BIT_FAILS ))
                 Case (2) ! C3S
                     previous = any(.not. BTest( quality_in(X,Y,:), BIT_FAILS ))
                 End Select
                 If (debuglevel .ge. 530) print *, 'startseries = F -> quality_in, BIT_FAILS=', quality_in, BIT_FAILS
              End Do
           Else
              previous = .false.
              If (debuglevel .ge. 530) print *, 'startseries = T'
           End If
           If (debuglevel .ge. 130) print *, 'Is there a previous estimate ? previous = ', previous


           refl_is_outlier(:) = .false.
!           If ((previous) .and. ((refl_outliers_elim_band_ref .ne. -1) .and. (refl_outliers_elim_band_in .ne. -1))) Then
!               ! compare the distance between the values of 
!               !   - reflectance in band 'refl_outliers_elim_band_in' of the input
!               !   - estimated reflectance in band 'refl_outliers_elim_band_ref' from the brdf previous values
!               nreflect_in_one_band(:)= reflectance(X,Y,refl_outliers_elim_band_in,:)
!               k_in = brdf_in(X,Y,refl_outliers_elim_band_ref,:)
!               ! First loop to compute mean and stdev
!               refl_estimate(:) = nan
!               Do N = 1, N_scenes
!                   If (.not. ang_ok(N)) cycle
!                   If ( any(isnan(nreflect_in(:,N)))) Then
!                       cycle
!                   End If
!                   kernels_values = brdfmodel(theta_sat(N),phi_del(N),theta_sol(N),model)
!                   refl_estimate(N) = Dot_Product(kernels_values(0:MM), k_in(0:MM))
!               End Do
!
!               ! We could do this second loop within the first one, this may be more efficient.
!               ! But we could also separate this code to compute mean and variance in another module/function/subroutine
!               NN = 0
!               sum_ = 0.
!               sum_squares = 0.
!               Do N = 1, n
!                   tmp = refl_estimate(N)
!                   If (.not. isnan(tmp)) Then
!                       NN = NN + 1
!                       sum_ = sum_ + tmp
!                       sum_squares = sum_squares + tmp*tmp
!                   End If
!               End do
!               If ((NN .eq. 0) .or. (NN .eq. 1)) Then
!                   mean = nan
!                   stdev = nan
!               Else
!                   mean = sum_ / NN
!                   variance = (sum_squares - sum_*sum_/NN)/(NN-1)
!                   stdev   = sqrt(variance)
!               End If
!               If (debuglevel .ge. 600) print *, 'outliers detection : refl_estimate = ', refl_estimate
!               If (debuglevel .ge. 600) print *, 'outliers detection : mean/stdev = ', mean,stdev
!
!               maxdistance = (refl_outliers_elim_param1 * mean + refl_outliers_elim_param2 * stdev)
!               ! Second loop to remove outliers
!               Do N = 1, N_scenes
!                   If (abs(refl_estimate(N) - nreflect_in_one_band(N)) > maxdistance)  Then
!                      If (debuglevel .ge. 600) print *, 'Removing input',N, refl_estimate(N), 'because brdf estimate is',refl_estimate(N), 'maxdistance = ', maxdistance
!                      refl_is_outlier(N) = .true.
!                   End If
!               End Do
!           End if

         If (enable_normalisation) Then
            nreflect_in(:,:) = reflectance(X,Y,:,:)
            nreflect_cov_in(:,:) = reflectance_cov(X,Y,:,:)
            Do N = 1, N_scenes
              ! find Snow mask for each scene by looking at each band. Put it in the variable snow_mask
              snow_mask = 0
              Do I = 1, N_channels_in
                 If (IAND(lwcs_mask(X,Y,I,N),int(B'00010000', quakind)) .eq. int(B'00010000', quakind)  ) Then
                     If ((snow_mask .ne. 0) .and. (snow_mask .ne. 2)) Then
                            ! inconsistent snow flag. We have snow here but the snow mask is neither 'snow'(2) nor 'not yet set (0).
                            ! We should remove the data TODO : clarify this, add security if needed
                        nreflect_ref(:,N) = nan
                     End If
                     snow_mask = 2
                  else
                     If  ((snow_mask .ne. 0) .and. (snow_mask .ne. 1)) Then
                        nreflect_ref(:,N) = nan
                     End If
                     snow_mask = 1
                 End If
              End Do

              !print *,'spectral_normalisation',spectral_normalisation(snow_mask,1:N_channels_ref,0), snow_mask
              !print *,'spectral_normalisation_err',spectral_normalisation_err(snow_mask,1:N_channels_ref,0), snow_mask
              If (debuglevel .ge. 180) print *, 'snow_mask', snow_mask

              ! To improve the code, the lwcs_mask for the ref band could be computed from the lwcs_mask from the other band taking all of them into account
              ! but here we just take band 1
              lwcs_mask_ref(:,N) = lwcs_mask(X,Y,1,N)

              Do I = 1, N_channels_in
                 ! basic security checks
                 if ((nreflect_in(I,N)/100. > 1.2) .or. (nreflect_in(I,N)/100. < -0.1) .or. (nreflect_cov_in(I,N)/100. < -0.) .or.  (nreflect_cov_in(I,N)/100. > 10.)) Then
                     nreflect_ref(:,N) = nan
                     nreflect_cov_ref(:,N) = nan
                     If (debuglevel .ge. 180) print *, 'security check A on input, scene removed ', I, nreflect_in(I,N), nreflect_cov_in(I,N)
                     cycle
                 End If
                 if ( (nreflect_cov_in(I,N)/100.) > (abs(nreflect_in(I,N)/100.)*2. + 0.1) )  Then
                     nreflect_ref(:,N) = nan
                     nreflect_cov_ref(:,N) = nan
                     If (debuglevel .ge. 180) print *, 'security check B on input, scene removed ', I, nreflect_in(I,N), nreflect_cov_in(I,N)
                     cycle
                 End If
                 If (lwcs_mask_ref(I,N) .eq. lwcs_mask_missing) Then
                     nreflect_ref(:,N) = nan
                     nreflect_cov_ref(:,N) = nan
                     If (debuglevel .ge. 180) print *, 'security check C on input, scene removed ', I, nreflect_in(I,N), nreflect_cov_in(I,N)
                     cycle
                 End If
              End Do
              If ( any(isnan(nreflect_in(:,N))) .or. any(isnan(nreflect_cov_in(:,N))) ) Then
                  If (debuglevel .ge. 600) print *, 'one nan reflectance value -> set all to nan for scene ',N, 'refl was:', nreflect_in(:,N), 'refl_cov was:', nreflect_cov_in(:,N)
                  nreflect_ref(:,N) = nan
                  nreflect_cov_ref(:,N) = nan
                  cycle
              End If

              !print *,'spectral_normalisation',spectral_normalisation(snow_mask,1:N_channels_ref,0), snow_mask
              !print *,'spectral_normalisation_err',spectral_normalisation_err(snow_mask,1:N_channels_ref,0), snow_mask
              
              ! In the following we are doing harmonization. The spectral harmonization is based on spectral_normalisation() matrix
              ! where we can find also 2 factors for ajustment.
              ! then in the first line of the matrix, we have the constant parameter for normalisation and alpha and beta in adjustment
              ! normalisation:
              ! (1) NDVI(s) = (ref(s,NIR)-ref(s,RED))/(ref(s,NIR)+ref(s,RED))
              ! (2) ref_norm(s,c) = a(s,c)*ref(s,c) + b(s,c)*NDVI(s)*ref(s,c) + c(s,c)*NDVI(s)^2*ref(s,c) + d(s,c)*NDVI(s)^3*ref(s,c) + e(s,c) (avec s=sensor et c=channel) 
              ! adjustment:
              ! (3) NDVI_norm(s) = (ref_norm(s,NIR)-ref_norm(s,RED))/(ref_norm(s,NIR)+ref_norm(s,RED))
              ! (4) ref_adjusted(s,c) = ref_norm(s,c) + alpha(s,c)*NDVI_norm(s)+ beta(s,c)
              If (debuglevel .ge. 180) print *, 'snow_mask', snow_mask

                ! compute ndvi for this scene
                ndvi_in = ( nreflect_in(ndvi_nir,N) - nreflect_in(ndvi_red,N) ) /( nreflect_in(ndvi_nir,N) + nreflect_in(ndvi_red,N) )
                
                If (isnan(ndvi_in))  ndvi_in = 0.
                If (ndvi_in < -1.)  ndvi_in = -1.
                If (ndvi_in > 1.)   ndvi_in = 1.
                
                If (debuglevel .ge. 2000) print *, N, 'ndvi_in = ', ndvi_in
                If (debuglevel .ge. 2000) print *, N, 'nreflect_in(ndvi_nir,N) = ', nreflect_in(ndvi_nir,N)
                If (debuglevel .ge. 2000) print *, N, 'nreflect_in(ndvi_red,N) = ', nreflect_in(ndvi_red,N)

                nreflect_ref(:,N) = 0
                nreflect_cov_ref(:,N) = 0
                If (debuglevel .ge. 2000) print *, N, 'nreflect_ref global view before norma = ', nreflect_ref(:,:)
                If (debuglevel .ge. 2000) print *, '---------------'
                If (debuglevel .ge. 2000) print *, 'Normalisation scene ', N
                
                Do I_out = 1, N_channels_ref
                
                    If (debuglevel .ge. 2100) print *, N, 'nreflect_in(:,N)/100.=', nreflect_in(:,N)/100.
                    nreflect_ref(I_out,N) = nreflect_ref(I_out,N) + &
                           & spectral_normalisation(snow_mask,I_out, 0, 1)
                    Do I_in = 1, N_channels_in
                    
                        theta_sat_ref(I_out, N) = theta_sat(I_in,N)
                        phi_del_ref(I_out, N) = phi_del(I_in, N)
                                            
                        If (debuglevel .ge. 2100) print *, N, 'nreflect_in(I_in,N)/100.=', nreflect_in(I_in,N)/100.
!~                         nreflect_ref(I_out,N) = nreflect_ref(I_out,N)
                        nreflect_ref(I_out,N) = nreflect_ref(I_out,N) + &
                           & spectral_normalisation(snow_mask,I_out,I_in, 1) * nreflect_in(I_in,N)/100. + &
                           & spectral_normalisation(snow_mask,I_out,I_in, 2) * nreflect_in(I_in,N)/100. * ndvi_in + &
                           & spectral_normalisation(snow_mask,I_out,I_in, 3) * nreflect_in(I_in,N)/100. * ndvi_in * ndvi_in + &
                           & spectral_normalisation(snow_mask,I_out,I_in, 4) * nreflect_in(I_in,N)/100. * ndvi_in * ndvi_in * ndvi_in
                       If (debuglevel .ge. 2000) print *, snow_mask,I_out,I_in
                       If (debuglevel .ge. 2000) print *, N, 'nreflect_ref += ', spectral_normalisation(snow_mask,I_out, 0, 1)
                       If (debuglevel .ge. 2000) print *, N, 'nreflect_ref += ', spectral_normalisation(snow_mask,I_out,I_in, 1) ,'* nreflect_in(:,N)/100.'
                       If (debuglevel .ge. 2000) print *, N, 'nreflect_ref += ', spectral_normalisation(snow_mask,I_out,I_in, 2) ,'* nreflect_in(:,N)/100. * ndvi_in'
                       If (debuglevel .ge. 2000) print *, N, 'nreflect_ref += ', spectral_normalisation(snow_mask,I_out,I_in, 3) ,'* nreflect_in(:,N)/100. * ndvi_in * ndvi_in'
                       If (debuglevel .ge. 2000) print *, N, 'nreflect_ref += ', spectral_normalisation(snow_mask,I_out,I_in, 4) ,'* nreflect_in(:,N)/100. * ndvi_in * ndvi_in * ndvi_in'
                       If (debuglevel .ge. 2000) print *, N, 'not used :spectral_normalisation(snow_mask,I_out,0,2:4)', spectral_normalisation(snow_mask,I_out,0,2:4)

                       ! simple covariance propagation instead of using jacobian of the ndvi formula
                       ! 1 - Because ndvi is a corrective element, and the main covariance is from the band used without ndvi
                       ! 2 - To simplify the computation
                       ! 3 - To avoid potential discontinuities, numerical instability and unknown and terrible things
                       nreflect_cov_ref(I_out,N) = nreflect_cov_ref(I_out,N) + &
                           & Abs(spectral_normalisation(snow_mask,I_out,I_in, 1)) * nreflect_cov_in(I_in,N) * nreflect_cov_in(I_in,N)
                    End Do
                    
                    nreflect_cov_ref(I_out,N) = Sqrt(Abs(nreflect_cov_ref(I_out,N)))
                                              
                    If (debuglevel .ge. 2000) print *, N, 'nreflect_cov_ref = ', nreflect_cov_ref(I_out,N)
                    If (debuglevel .ge. 2000) print *, N, 'spectral_normalisation_err = ', spectral_normalisation_err(snow_mask,1:N_channels_ref,0)
                    If (debuglevel .ge. 2000) print *, N, 'spectral_normalisation_err = ', spectral_normalisation_err(snow_mask,1:N_channels_ref,1)
                    If (debuglevel .ge. 2000) print *, N, 'spectral_normalisation_err = ', spectral_normalisation_err(snow_mask,1:N_channels_ref,2)
!~                     nreflect_cov_ref(I_out,N) = spectral_normalisation_err(snow_mask,I_out,0) + &
!~                                                & spectral_normalisation_err(snow_mask,I_out,1) * nreflect_cov_ref(I_out,N)
                    If (debuglevel .ge. 2000) print *, N, '==> nreflect_cov_ref = ', nreflect_cov_ref(I_out,N)                           
                    nreflect_ref(I_out,N) = nreflect_ref(I_out,N) * 100.
                    If (debuglevel .ge. 2100) print *, N, 'nreflect_ref = ', nreflect_ref(I_out,N)
                    If (debuglevel .ge. 2100) print *, N, 'nreflect_ref global view = ', nreflect_ref(:,:)
                End Do ! loop on channels

!~               If (debuglevel .ge. 600) print *, 'reflcov_1', Sqrt(Abs(MatMul( Abs(spectral_normalisation(snow_mask,1:N_channels_ref,1:N_channels_in)), (nreflect_cov_in(:,N) * nreflect_cov_in(:,N))  )))
              If (debuglevel .ge. 600) print *, 'reflcov_2', nreflect_cov_ref(:,N)

              ! additional ndvi correction
              ! ndvi2 is computed from the normalisted reflectance, then it is used to correct the reflectance again
              ! (in the first version, these corrections have been defined empirically from aeronet station, not from simulation)
              if (snow_mask .eq. 1) Then ! no snow
                ndvi2 = ( nreflect_ref(ndvi2_nir,N) - nreflect_ref(ndvi2_red,N) ) / ( nreflect_ref(ndvi2_nir,N) + nreflect_ref(ndvi2_red,N) )
                If (debuglevel .ge. 2000) print *, N, 'ndvi2 = ', ndvi2
                If (debuglevel .ge. 2000) print *, N, 'nreflect_ref(ndvi2_nir,N) = ', nreflect_ref(ndvi2_nir,N)
                If (debuglevel .ge. 2000) print *, N, 'nreflect_ref(ndvi2_red,N) = ', nreflect_ref(ndvi2_red,N)
                Do I_out = 1, N_channels_ref
                    nreflect_ref(I_out, N) = nreflect_ref(I_out, N) + (ndvi2 * spectral_normalisation(snow_mask,I_out,0, 2) + spectral_normalisation(snow_mask,I_out,0, 3) ) * 100 
                End Do
              End If


              If ( any(isnan(nreflect_ref(:,N))) .or. any(isnan(nreflect_cov_ref(:,N))) ) Then
                  If (debuglevel .ge. 600) print *, 'security check D : one nan reflectance after normalisation -> set all to nan for scene ',N, 'refl was:', nreflect_in(:,N), 'refl_cov was:', nreflect_cov_in(:,N)
                  If (debuglevel .ge. 600) print *, '        after normalisation, refl was:', nreflect_ref(:,N), 'refl_cov was:', nreflect_cov_ref(:,N)
                  nreflect_ref(:,N) = nan
                  nreflect_cov_ref(:,N) = nan
                  cycle
              End If
              Do I = 1, N_channels_ref
                 ! more security checks
                 if ((nreflect_ref(I,N)/100. > 10.) .or. (nreflect_ref(I,N)/100. < -1.) .or. (nreflect_cov_ref(I,N)/100. < 0.0000001)) Then
                     If (debuglevel .ge. 180) print *, 'security check E on input, scene removed ', I, nreflect_ref(I,N), nreflect_cov_ref(I,N)
                     nreflect_ref(:,N) = nan
                     nreflect_cov_ref(:,N) = nan
                     cycle
                 End If
              End Do
              If (debuglevel .ge. 2180) print *, 'nreflect_in ', nreflect_in(:,N)
              If (debuglevel .ge. 2180) print *, 'nreflect_ref', nreflect_ref(:,N)
           End Do
           Else ! normalisation not enabled
               If (debuglevel .ge. 100) print *, 'Normalisation not enabled'
               nreflect_ref(:,:) = reflectance(X,Y,:,:)
               nreflect_cov_ref(:,:) = reflectance_cov(X,Y,:,:)
               
               theta_sat_ref(:,:) = theta_sat(:,:)
               phi_del_ref(:,:) = phi_del(:,:)
               Do I = 1, N_channels_ref
                  lwcs_mask_ref(I,:) =  lwcs_mask(X,Y,I,:) ! use first band only for lwcs mask
                  ! To improve this, the lwcs_mask for the ref band could be computed from the lwcs_mask
                  ! from the other bands,  taking all of them into account
               End Do
           End If

           If (debuglevel .ge. 200) print *, 'nreflect_ref', nreflect_ref(:,:)

           
           ! loop over channels
           valids = .false. !! ! valids is of type array-of-logical
           snow = .false. !! ! TODO snow is of type logical : bug here ? snow is not set to false in the loop for each channel ?
           Do I = 1, N_channels_ref
              If (debuglevel .ge. 150) print *, ' - - - - Channel loop - - Y,X,channel : ', Y,X,I
              If (debuglevel .ge. 200) print *, 'reflectance', reflectance(X,Y,I,:)
              If (debuglevel .ge. 200) print *, 'nreflect_ref_cov', nreflect_cov_ref(I,:)
              If (debuglevel .ge. 200) print *, 'nreflect_ref', nreflect_ref(I,:)
              ! check for correctly processed slots
              processed = BTest( lwcs_mask_ref(I,:), BIT_PROC ) .and. &
                   &      (.not. (isnan(nreflect_ref(I,:))))
              ! check cloud mask information
              mask_cma = IAND(lwcs_mask_ref(I,:),int(B'00011100', quakind))
              If (debuglevel .ge. 160) print *, 'mask_cma (cloud mask)      ', mask_cma
              cloudy   = mask_cma .eq. MCL_CLOUD    .or.  mask_cma .eq. MCL_CONTAM
              snowy    = mask_cma .eq. MCL_SNOW     .or.  mask_cma .eq. MCL_SNOW_X
              bad_cma  = mask_cma .eq. MCL_CLEAR_X  .or.  mask_cma .eq. MCL_SNOW_X
              shadow   = mask_cma .eq. MCL_SHADOW
              ! define valid scenes
              valid = ang_ok .and. processed .and. .not. cloudy
              If (debuglevel .ge. 160) print *, 'valid (1)                  ', valid
              ! TODO : explain different between valid vs valids ?
              ! eliminate observations with bad CMa quality
              If ( bad_CMa_elim ) valid = valid .and. .not. bad_cma
              ! eliminate observations marked with shadow flag
              If ( shadow_elim ) valid = valid .and. .not. shadow
              valid = valid .and. .not. refl_is_outlier
              ! eliminate potentially affected observations before or after cloudy slots
              If ( N_slot_elim .gt. 0 ) Then
                 Do N = 1, N_scenes
                ! TODO check this and clarify ! (note that it is identical to MDAL)
                    If ( cloudy(N) ) Then
                       valid(Maxval((/N-N_slot_elim,1/) ):Minval((/N+N_slot_elim,N_scenes/))) = .false.
                       If (debuglevel .ge. 160) print *, 'Cloudy at ',N,'-> valid=false for ', Maxval((/N-N_slot_elim,1/)),Minval((/N+N_slot_elim,N_scenes/))
                    End If
                 End Do
              End If
              If (debuglevel .ge. 160) print *, 'valid (2)                  ', valid

              !---- MODIS : determines whether the majority of clear observations was snow-covered or snow-free then----!
              !---- only calculates albedo for the majority condition (Schaaf et al., 2008).----------------------------!--NL

              ! valid : all valid (snow and no snow)
              ! valid0 : valid and no snow or valid and only snow (greater than N_snow_limit,e.g majority)
              N_valid = Count(valid) !
              valid0 = valid
              If ( .not. snow_flag_one ) Then
                  N_snow_limit = Count(valid)/2 + 1
              Else
                  N_snow_limit = 1
              End If
              Select Case (sat_specific)
              !Case (0) ! MSG
              Case (1) ! EPS
                If ( Count( snowy .and. valid ) .ge. N_snow_limit ) Then
                    valid  =  snowy .and. valid
                Else
                    valid  =  valid .and. .not. snowy
                End If
              Case (2) ! C3S
                If ( Count( snowy .and. valid ) .ge. N_snow_limit ) Then
                    valid  =  snowy .and. valid
                Else
                    valid  =  valid .and. .not. snowy
                End If
              End Select
              If (debuglevel .ge. 160) print *, 'valid (3)                  ', valid

              ! calculate the number of valid observations
              N_valid_obs = Count(valid)   ! only snow .or. no snow
              ! determine if a sufficient number of observations is available
              observations = ( N_valid_obs .ge. N_obs_limit )
              ! calculate number of valid snowy observations
              N_valid_snow = Count( snowy .and. valid ) ! = 0 ou N_valid_obs !--NL
              !If ( .not. snow_flag_one ) N_snow_limit = N_valid_obs/2 + 1   !--NL
              n_valid_obs_out(X,Y,I) = int(N_valid_obs,1)

              If (debuglevel .ge. 160) print *, 'N_valid_obs', N_valid_obs
              If (debuglevel .ge. 160) print *, 'processed  ', processed
              If (debuglevel .ge. 160) print *, 'N_snow_limit ', N_snow_limit
              If (debuglevel .ge. 160) print *, 'cloudy       ', cloudy
              If (debuglevel .ge. 160) print *, 'snowy        ', snowy
              If (debuglevel .ge. 160) print *, 'shadow       ', shadow
              If (debuglevel .ge. 160) print *, 'valid        ', valid
              If (debuglevel .ge. 160) print *, 'valid0       ', valid0
              If (debuglevel .ge. 1160) print *, 'bad_cma      ', bad_cma
              If (debuglevel .ge. 1160) print *, 'bad_CMa_factor      ', bad_CMa_factor
              If (debuglevel .ge. 1160) print *, 'shadow_factor      ', shadow_factor
              If (debuglevel .ge. 1160) print *, 'wi_angular      ', wi_angular
              If (debuglevel .ge. 1160) print *, 'sig_nadir_a      ', sig_nadir_a
              If (debuglevel .ge. 1160) print *, 'sig_nadir_b      ', sig_nadir_b
              If (debuglevel .ge. 1160) print *, 'sigrefl_min      ', sigrefl_min
              If (debuglevel .ge. 1160) print *, 'sigrefl_max      ', sigrefl_max
              ! if observations are available calculate matrix A and vector b
              If (debuglevel .ge. 160) print *, 'observations      ', observations
              If ( observations ) Then
                 ! calculate reflectance value and error estimate
                 ! with a coefficient 1/100. Because we are actually receiving radiances
                 ! and we transform it into reflectances without further thinking ?
                 ! or because it is per nm ? (not likely)
                 ! or because there is a wrong scale_factor in the AL1 output files ? (not likely)
                 ! or to avoid numerical instabilities ?
                 ! or because the nreflect_ref is actually in % ?
                 ! TODO
                 Where ( valid ) refl = nreflect_ref(I,:) / 100.
                 Where ( .not. valid ) refl = 0.
                 If (debuglevel .ge. 160) print *, '* nreflect_ref(I,:) ', nreflect_ref(I,:)
                 If (debuglevel .ge. 160) print *, '* valid      ', valid
                 If (debuglevel .ge. 160) print *, '* refl      ', refl
                 If (debuglevel .ge. 160) print *, '* nreflect_cov_ref(I,:)', nreflect_cov_ref(I,:)
                 Where ( valid ) sigrefl(I,:) = (sig_nadir_a(I)+sig_nadir_b(I)*refl)
                 If (debuglevel .ge. 11) print *, '* sigrefl 1', sigrefl(I,:)
                 !!!!!! This following step is probably no more relevant as we are doing a new normalisation !!!
                 !!!!!! Should be removed for the next version !!!!!!
!~                  Select Case (sat_specific)
!~                     Case (2) ! C3S    !!!
!~                         refl_cov_tmp(:) = nreflect_cov_ref(I,:) / typical_cov_rescale_values(I) * 0.75
!~                        If (debuglevel .ge. 160) print *, 'typical values    ==> ', typical_cov_rescale_values(I)
!~                         Where ( valid .and. refl_cov_tmp .lt. 0.1) refl_cov_tmp = 0.1
!~                         Where ( valid .and. refl_cov_tmp .gt. 1.0) refl_cov_tmp = 1.0
!~                         Where ( valid ) sigrefl(I,:) = 0.667 * sigrefl(I,:) +  0.333 * sigrefl(I,:) * refl_cov_tmp
!~                 End Select
                


                 If (debuglevel .ge. 100) print *, '* sigrefl 2', sigrefl(I,:)
                 Where ( valid .and. sigrefl(I, :) .lt. sigrefl_min) sigrefl(I, :) = sigrefl_min
                 Where ( valid .and. sigrefl(I, :) .gt. sigrefl_max) sigrefl(I, :) = sigrefl_max
                 I_inb = angle_index(I)
                 If (debuglevel .ge. 100) print *, 'I_in is in this case : ', I_inb
                 Where ( valid ) sigrefl(I, :) = sigrefl(I, :) * wi_angular(I_inb, :)
                 Where ( .not. valid ) sigrefl(I, :) = 0
                 If (debuglevel .ge. 100) print *, 'wi_angular(I_inb)      ', wi_angular(I_inb, :)
                 Where ( valid .and. bad_cma ) sigrefl(I, :) = sigrefl(I, :) * bad_CMa_factor
                 Where ( valid .and. shadow )  sigrefl(I, :) = sigrefl(I, :) * shadow_factor

                 If (debuglevel .ge. 100) print *, 'Computing linear model A,b'
                 If (debuglevel .ge. 100) print *, 'model      ', model
                 If (debuglevel .ge. 100) print *, 'sigrefl      ', sigrefl(I, :)

                 If (debuglevel .ge. 200) print *, N, 'spectral_normalisation_err = ', spectral_normalisation_err(1,1:N_channels_ref,:)
                 If (debuglevel .ge. 200) print *, N, 'spectral_normalisation_err = ', spectral_normalisation_err(2,1:N_channels_ref,:)

                 If (debuglevel .ge. 100) print *,'spectral_normalisation_err(snow_mask,I,0) =', spectral_normalisation_err(1,I,0) 
                 If (debuglevel .ge. 100) print *,'spectral_normalisation_err(snow_mask,I,1) =', spectral_normalisation_err(1,I,1) 
                 ! Error on unknown channels are changes according to parameters stored in spectral_normalisation_err
                sigrefl(I,:) = spectral_normalisation_err(1,I,0) + spectral_normalisation_err(1,I,1)*sigrefl(I,:)  
                  If (debuglevel .ge. 100) print *, 'sigrefl après bidouille CANAL I= ', I , sigrefl(I, :) 
                 
                 ! fill matrix A and vector b
                 NN = 0
                 Do N = 1, N_scenes
                    If ( valid(N) ) Then
                           NN = NN + 1
                           If (debuglevel .ge. 100) print *, N,NN,'theta_sat(I, N),phi_del(I, N),theta_sol(N),model, sigrefl(I, N)',theta_sat_ref(I, N),phi_del_ref(I, N),theta_sol(N),model,sigrefl(I, N)
                           A(NN,0:MM) = brdfmodel(theta_sat_ref(I, N),phi_del_ref(I, N),theta_sol(N),model) / sigrefl(I, N)
                           !If (debuglevel .ge. 100) print *, N,NN,'brdfmodel (A(NN,0:MM))/ sigrefl(I, N)= ',  A(NN,0:MM)
                           b(NN) = refl(N) / sigrefl(I, N)
                    End If
                 End Do

                 ! generate matrix ATA
                 AT = Transpose( A )
                 ATA = Matmul( AT(0:MM,1:N_valid_obs), A(1:N_valid_obs,0:MM) )
                 ! force the symmetry of the matrix ATA
                 ! which may have been lost due to round-off errors
                 Do N = 0, MM
                    Do NN = N+1, MM
                       ATA(N,NN) = 0.5*( ATA(N,NN)+ATA(NN,N) )
                       ATA(NN,N) = ATA(N,NN)
                    End Do
                 End Do
              Endif ! If ( observations )

              ! regularisation
              CkI_reg = 0.
              Do N = 0, MM
                 CkI_reg(N,N) = sig_k_reg(N,I)**(-2)
                 ! Some weight included in the Reg matrix for channels that are artificials
              End Do

              ! if applicable generate result based on previous estimate as a priori information
              If ( recursion ) Then
                 ! if previous estimate is available read parameter vector and covariance matrix
                 If ( previous ) Then
                    ! use previous result as a priori information
                    k_in = brdf_in(X,Y,I,:)
                    Do N = 0, MM
                       Do NN = N, MM
                          cov_aux = covariance_in(X,Y,I,N,NN)
                          Ck_in(N,NN) = cov_aux**2
                          If ( N .eq. NN ) Then
                             ! assure positive variances
                             Ck_in(N,N) = Maxval( (/ Ck_in(N,N), epsilon_var /) )
                          Else
                             If ( cov_aux .lt. 0 ) Ck_in(N,NN) = - Ck_in(N,NN)
                             ! set co-variances to zero for numerical reasons
                             Ck_in(N,NN) = 0. ! comment this line for using covariances
                             Ck_in(NN,N) = Ck_in(N,NN)
                          End If
                       End Do
                    End Do
                    ! apply "temporal weightfactor"
                    Ck_in = Ck_in * (1.+delta)**days_last_in
                    ! calculate the inverse
                    CkI_in = invers_lapack( Ck_in )
                 Else
                    ! no previous estimate available
                    k_in = 0.
                    CkI_in = 0.
                 End If ! If ( previous )
                 
                 
                 ! if climatologic estimate is available read parameter vector and covariance matrix
                 If ( brdf_clim_activated ) Then
                    ! use previous result as a priori information
                    k_clim_in = brdf_clim(X,Y,I,:)

                    Do N = 0, MM
                       Do NN = N, MM
                          Ck_clim_in(N,NN) = covariance_clim(X,Y,I,N,NN)
                          ! when the std is computed, we write sigma**2 => no square here
						  if (isnan(Ck_clim_in(N,NN))) Then  ! If covariance factor is nan, then use Ck_reg
										  Ck_clim_in(N,NN) = sig_k_reg(N,I) ** 2
						  End If 
                        
						  If ( N .eq. NN ) Then
                             ! assure positive variances
                             Ck_clim_in(N,N) = Maxval( (/ Ck_clim_in(N,N), epsilon_var /) )
                          Else
                             If ( Ck_clim_in(N,NN) .lt. 0 ) Ck_clim_in(N,NN) = - Ck_clim_in(N,NN)
                             ! set co-variances to zero for numerical reasons
                             Ck_clim_in(N,NN) = 0. ! comment this line for using covariances
                             Ck_clim_in(NN,N) = Ck_clim_in(N,NN)
                          End If
                       End Do
                    End Do
 
                    ! calculate the inverse
                    CkI_clim_in = invers_lapack( Ck_clim_in )
					If (debuglevel .ge. 5005) print *,  'CkI_clim_in avant le report de la modif', CkI_clim_in
					If (debuglevel .ge. 5005) print *,  'CkI_reg avant le report de la modif', CkI_reg

					If (debuglevel .ge. 5005) print *, I,'  K clim is, before correction nan ' , k_clim_in
					! Security when k_clim is nan => give reg values to K
					Do N = 0, MM
						if ( isnan(k_clim_in(N)) ) Then
							k_clim_in(N) = k_reg(N, I)
						End If
					End Do
					
					Do N = 0, MM ! Security check when no K_clim is available => CkI_clim = CkI_reg
						if ( isnan(brdf_clim(X,Y,I,N)) ) Then
							CkI_clim_in = CkI_reg
						End If
					End Do
					If (debuglevel .ge. 5005) print *,  'CkI_clim_in a le report de la modif', CkI_clim_in
                 Else
                    ! no previous estimate available
                    k_clim_in = 0.
                    CkI_clim_in = 0.
                 End If ! If ( brdf_clim_activated )
                 
                If (debuglevel .ge. 250) print *, I,'  K clim is ' , k_clim_in
				If (debuglevel .ge. 250) print *, I,'  K in is ' , k_in
                If (debuglevel .ge. 250) print *, I,'  CK clim is before normaliz' , Ck_clim_in

                ! A different weight is given to the channels : Less confidence in channels  Blue and MIR
                If (debuglevel .ge. 250) print *, I,' The weight given to the channel K clim is ' , spectral_normalisation_err(1,I,3)
                CkI_clim_in =     spectral_normalisation_err(1,I,3) *CkI_clim_in
                If (debuglevel .ge. 250) print *, I,'  CK clim is after normalisation  ' , Ck_clim_in
                 
                 ! perform calculation if observations and/or previous estimate are available
                 If ( observations .or. previous ) Then
                    Select Case (sat_specific)
                    Case (0) ! MSG
                        If (debuglevel .ge. 250) print *, I,'QUALITY: set quality + QUA_MSG = ', quality(X,Y,I), '+', QUA_MSG, '=', quality(X,Y,I) + QUA_MSG
                        quality(X,Y,I) = quality(X,Y,I) + QUA_MSG
                    Case (1) ! EPS
                        If (debuglevel .ge. 250) print *, I,'QUALITY: set quality + QUA_EPS = ', quality(X,Y,I), '+', QUA_EPS, '=', quality(X,Y,I) + QUA_EPS
                        quality(X,Y,I) = quality(X,Y,I) + QUA_EPS
                        If ( N_valid_snow .ne. N_valid .and. N_valid_snow .ne. 0 ) Then    !--NL  ! QUA_MAJORITY
                            If (debuglevel .ge. 250) print *, I,'QUALITY: set quality + QUA_MAJORITY = ', quality(X,Y,I), '+', QUA_MAJORITY, '=', quality(X,Y,I) + QUA_MAJORITY
                            quality(X,Y,I) = quality(X,Y,I) + QUA_MAJORITY
                        End If
                    Case (2) ! C3S
                    End Select

                    If ( observations ) Then
                       ! if observations are available calculate scenes_age & age = moyenne !median
                       ! memory allocation for time series variables
                       ! TODO in loop memory allocation : not good ?
                       Allocate(scenes_age (1:N_valid), STAT=astat)
                       If (astat .ne. 0) Then
                          print *, "Error when allocating time series variables"
                          STOP 1
                       End If

                       NN = 0
                       Do N = 1, N_scenes
                          If ( valid0(N) ) Then
                             NN = NN + 1
                             ! Convert int64 dates into age in days : 
                             ! 86400 = 3600 * 24 = number of seconds in one day
                             ! Moreover, the conversion can be tricky : see https://stackoverflow.com/questions/20411337/fortran-77-real-to-int-rounding-direction
                             ! that is the reason why you use "floor"
                             ! notice also the " + 1." : we see why this is required when considering the last scene (if valid),
                             ! which is the same day as the current date.
                             ! we would have for instance a scene date of 2002-09-10 11:45:12
                             ! while the current date (output date) would be 2002-09-10, i.e. 2002-09-10 00:00:00.
                             ! for this scene we want the age of the scene to be 0.
                             scenes_age(NN) = int(floor(real(currentdatetime - scenesdatetimes(N), 4) / 86400 + 1.), agekind)
                             If (debuglevel .ge. 40000) print *, 'Converting int64 date a:' ,currentdatetime , scenesdatetimes(N)
                             If (debuglevel .ge. 40000) print *, 'Converting int64 date b:' ,real(currentdatetime - scenesdatetimes(N), 4) / 86400 + 1.
                             If (debuglevel .ge. 40000) print *, 'Converting int64 date c:', floor(real(currentdatetime - scenesdatetimes(N), 4) / 86400 + 1.)
                             If (debuglevel .ge. 90000) print *, 'Converting int64 date d: scenesdatetimes(N) -> scenes_age(NN)', scenesdatetimes(N), ' ->', scenes_age(NN)
                          End If
                       End Do
                       If (debuglevel .ge. 130) print *, 'N_valid NN', N_valid, NN
                       If (N_valid .ne. NN) print *, 'ERROR : N_valid is not NN : ', N_valid, 'not =', NN

                       ! set snow flag
                       If (debuglevel .ge. 131) print *, 'N_valid_snow N_snow_limit', N_valid_snow, N_snow_limit
                       If ( N_valid_snow .ge. N_snow_limit ) Then
                          quality(X,Y,I) = quality(X,Y,I) + QUA_SNOW
                          If (debuglevel .ge. 250) print *,I, 'snow : set quality = ', quality(X,Y,I),QUA_SNOW
                          snow = .true.
                       End If

                       If (debuglevel .ge. 131) print *, 'CkI_in', CkI_in
                       If (debuglevel .ge. 131) print *, 'ATA', ATA
                       If (debuglevel .ge. 131) print *, 'AT(0:MM,1:N_valid_obs)', AT(0:MM,1:N_valid_obs)
                       If (debuglevel .ge. 131) print *, 'b', b(1:N_valid_obs)
                       If (debuglevel .ge. 131) print *, 'b total :', b
                       If (debuglevel .ge. 131) print *, '* Solving linear model'
                       
                       !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                       !!!!!!!!!!!!!!!!!!!!!!!!!! solve the linear least squares problem !!!!!!!!!!!!!!!!!!!!!!
                       !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                       
                       if  ( brdf_clim_activated ) Then
                           CkI =  ATA + CkI_in + CkI_reg + CkI_clim_in

                           Ck = invers_lapack( CkI )
                           k = Matmul( Ck, Matmul( AT(0:MM,1:N_valid_obs), b(1:N_valid_obs) ) &
                                & + Matmul( CkI_in, k_in ) + Matmul( CkI_reg, k_reg(0:MM,I) ) + Matmul( CkI_clim_in, k_clim_in ))
                                
                       Else
                           CkI =  ATA + CkI_in + CkI_reg 
                           Ck = invers_lapack( CkI )
                          
                           k = Matmul( Ck, Matmul( AT(0:MM,1:N_valid_obs), b(1:N_valid_obs) ) &
                                & + Matmul( CkI_in, k_in ) + Matmul( CkI_reg, k_reg(0:MM,I) ) )
                                
                       End If
                       If (debuglevel .ge. 250) print *, 'CkI   ', CkI
            If (debuglevel .ge. 250) print *, 'Ck   ', Ck
                       If (debuglevel .ge. 250) print *, 'k ===>   ', k

                       Select Case (sat_specific)
                       Case (0) ! MSG
                           age = 0
                       Case (1) ! EPS
                           age = sum(scenes_age)/N_valid  ! mean period valid
                       Case (2) ! C3S
                           age = sum(scenes_age)/N_valid  ! mean period valid
                           If (debuglevel .ge. 200) print *,'new age = ', age
                       End Select

                       ! memory deallocation scenes_age
                       Deallocate(scenes_age, STAT=astat )
                       If (astat .ne. 0) Then
                          print *, 'Error when deallocating variables'
                          STOP -1
                       End If

                    Else ! no new observations available: propagate previous estimate
                       If (debuglevel .ge. 131) print *, ' no new observations available: propagate previous estimate and mix with BRDF climatic'
                       If ( brdf_clim_activated ) Then
                       ! Kalman filter applicated even when no data are as input : both k_in and k_clim are equaly used as first guess
                       ! Regularisation matrix is used to ensure that the Kalman 
                           CkI =   CkI_in + CkI_reg + CkI_clim_in
                           Ck = invers_lapack( CkI )
                           k = Matmul( Ck, Matmul( CkI_in, k_in) + Matmul( CkI_reg, k_reg(0:MM,I) ) + Matmul( CkI_clim_in, k_clim_in ))
                       Else
                           k = k_in
                           Ck = Ck_in
                       end if

                       If ( age_obs_in(X,Y,I) .le. age_max-int(days_last_in) ) Then
                          age = age_obs_in(X,Y,I) + int(days_last_in, agekind)
                       Else
                          Select Case (sat_specific)
                          !Case (0) ! MSG
                          !    age = 0
                          !Case (1) ! EPS
                          !    quality(X,Y,I) = quality(X,Y,I) + QUA_NO_INPUT
                          Case (2) ! C3S
                              ! in c3s, the cloud mask is over-conservative, leading to some pixels in bright surface wrongly 
                              ! flagged as cloudy for 99% of the obsevations.
                              ! if age is very high, we suspect that we are in such case and set the appropriate flag
                               quality(X,Y,I) = quality(X,Y,I) + QUA_NO_INPUT
                          End Select
                          age = age_max
                       End If
                       If (debuglevel .ge. 131) print *, 'Setting age to ', age, '(', age_max, age_obs_in(X,Y,I), days_last_in,')'
                       If ( BTest( quality_in(X,Y,I), BIT_SNOW ) ) Then
                          snow = .true.
                          quality(X,Y,I) = quality(X,Y,I) + QUA_SNOW
                          If (debuglevel .ge. 250) print *, I, 'snow. : set quality = ', quality(X,Y,I), QUA_SNOW
                       End If
                    End If !If ( observations )

                    valids(I) = .true.
                    ! check range and store brdf parameters
                    Do N = 0, MM
                       k(N) = Minval( (/k(N), par_max/) )
                       k(N) = Maxval( (/k(N), par_min/) )
                    End Do
                    brdf(X,Y,I,:) = k
                    ! check range and store covariance matrix elements
                    Do N = 0, MM
                       Ck(N,N) = Maxval( (/ Ck(N,N), 0. /) )
                       sqcvm(N,N) = Sqrt( Ck(N,N) )
                       sqcvm(N,N) = Minval( (/ sqcvm(N,N), cxx_max /) )
                       sqcvm(N,N) = Maxval( (/ sqcvm(N,N), cxx_min /) )
                    End Do
                    Do N = 0, MM-1
                       Do NN = N+1, MM
                          sqcvm(N,NN) = Sign(Sqrt(Abs(Ck(N,NN))),Ck(N,NN))
                          sqcvm(N,NN) = Minval( (/sqcvm(N,NN), cxy_max/) )
                          sqcvm(N,NN) = Maxval( (/sqcvm(N,NN), cxy_min/) )
                          sqcvm(NN,N) = nan
                       End Do
                    End Do
                    covariance(X,Y,I,:,:) = sqcvm
                    ! store age of information
                    age_out(X,Y,I) = int(Minval( (/age, age_max/)), agekind)
                 End If ! If ( observations .or. previous )
              End If ! If ( recursion )

              ! if applicable and observations are available generate the daily composition result
              If ( composition .and. observations ) Then
                    Select Case (sat_specific)
                    Case (0) ! MSG
                        quality1(X,Y,I) = quality1(X,Y,I) + QUA_MSG
                    Case (1) ! EPS
                        quality1(X,Y,I) = quality1(X,Y,I) + QUA_EPS
                        If ( N_valid_snow .ne. N_valid .and. N_valid_snow .ne. 0 ) Then
                          quality1(X,Y,I) = quality1(X,Y,I) + QUA_MAJORITY
                        End If
                    Case (2) ! C3S
                    End Select
                    If (debuglevel .ge. 250) print *, I, 'QUALITY: set quality1 + QUA_MAJORITY = ', quality1(X,Y,I), QUA_MAJORITY

                 ! set snow flag
                 If ( N_valid_snow .ge. N_snow_limit ) Then
                    quality1(X,Y,I) = quality1(X,Y,I) + QUA_SNOW
                     If (debuglevel .ge. 250) print *, I, 'QUALITY: snow: set quality1 + QUA_SNOW = ', quality1(X,Y,I), QUA_SNOW
                    snow = .true.
                 End If
                 
                 
                   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                   !!!!!!!!!!!!!!!!!!!!!!!!!! solve the linear least squares problem !!!!!!!!!!!!!!!!!!!!!!
                   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

                 If (debuglevel .ge. 131) print *, '* Solving linear model for daily composition results'
                 
                 If  ( brdf_clim_activated ) Then
                     CkI =  ATA + CkI_reg + CkI_clim_in
                     Ck = invers_lapack( CkI )
                     k = Matmul( Ck, Matmul( AT(0:MM,1:N_valid_obs), b(1:N_valid_obs) ) &
                          & + Matmul( CkI_reg, k_reg(0:MM,I) ) + Matmul( CkI_clim_in, k_clim_in ))
                 Else
                     CkI =  ATA + CkI_reg 
                     Ck = invers_lapack( CkI )
                     k = Matmul( Ck, Matmul( AT(0:MM,1:N_valid_obs), b(1:N_valid_obs) ) &
                          & + Matmul( CkI_reg, k_reg(0:MM,I) ) )

                End If

!~                  If (debuglevel .ge. 125) print *, 'Ck', Ck
!~                  Ck = spectral_normalisation_err(0,I,2) + Ck * spectral_normalisation_err(0,I,3)
!~                  If (debuglevel .ge. 125) print *, 'spectral_normalisation_err', I, 'Ck = ',spectral_normalisation_err(0,I,0), ' + Ck *', spectral_normalisation_err(0,I,1)
!~                  If (debuglevel .ge. 125) print *, 'Ck', Ck

                 ! check range and store brdf parameters
                 Do N = 0, MM
                    k(N) = Minval( (/k(N), par_max/) )
                    k(N) = Maxval( (/k(N), par_min/) )
                 End Do
                 brdf1(X,Y,I,:) = k
                 ! check range and store covariance matrix elements
                 Do N = 0, MM
                    Ck(N,N) = Maxval( (/ Ck(N,N), 0. /) )
                    sqcvm(N,N) = Sqrt( Ck(N,N) )
                    sqcvm(N,N) = Minval( (/ sqcvm(N,N), cxx_max /) )
                    sqcvm(N,N) = Maxval( (/ sqcvm(N,N), cxx_min /) )
                 End Do
                 Do N = 0, MM-1
                    Do NN = N+1, MM
                       sqcvm(N,NN) = Sign(Sqrt(Abs(Ck(N,NN))),Ck(N,NN))
                       sqcvm(N,NN) = Minval( (/sqcvm(N,NN), cxy_max/) )
                       sqcvm(N,NN) = Maxval( (/sqcvm(N,NN), cxy_min/) )
                    End Do
                 End Do
                 covariance1(X,Y,I,:,:) = sqcvm
              End If  !If ( composition .and. observations )
           End Do !Do I = 1, N_channels_ref
           If ( recursion .and. Count(valids) .eq. N_channels_ref) Then
               If (snow) Then
                   snow_mask_out(X,Y) = 2 ! use snow coefficients
               Else
                   snow_mask_out(X,Y) = 1 ! use non-snow coefficients
               End If
           Else
               snow_mask_out(X,Y) = 0 ! do not process further
           End If
           If ( any(BTest( quality_in(X,Y,:), BIT_NO_INPUT )) ) Then
               snow_mask_out(X,Y) = 0 ! do not process further
           End If
           If (debuglevel .ge. 131) print *, '* Final snow_mask_out = ', snow_mask_out(X,Y)
        End Do  !Do X = 1, MSGpixX
     End Do     !Do Y = 1, Lines
End Subroutine MODEL_FIT
