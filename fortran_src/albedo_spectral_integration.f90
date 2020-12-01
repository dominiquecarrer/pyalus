Recursive Subroutine albedo_spectral_integration (errcode, errmsg, debuglevel,&
      & mask_array, &
      & sigma_co, &
      & coeffs, &
      & latitude, longitude, &
      & debuginfo, &
      & alb_max, alb_min, sig_max, sig_min, &
      & albedos, albedos_cov,albedos_age, albedos_quality, &
      & outalbedos, outalbedos_age, outalbedos_cov, outalbedos_quality, &
      & xstart, xend, ystart, yend, &
      & n_debuginfo, &
      & N_channels, MSGpixX, Lines, N_outalbedos, N_mask)

    Use algoconf
    Use brdfmodels
    Implicit None

    Integer, Parameter   :: N_inalbedos = 2
    Character (Len=1024) :: errmsg
    Integer              :: errcode

    Integer, Intent (In) :: debuglevel

    Integer, Intent(In)   :: xstart, xend, ystart, yend ! window to process

    ! Matrices dimensions
    Integer, Intent(in)   :: N_outalbedos
    Integer, Intent(in)   :: N_channels
    Integer, Intent(in)   :: Lines
    Integer, Intent(in)   :: N_mask
    Integer, Intent(in)   :: MSGpixX
    Integer, Intent(in)   :: n_debuginfo

    Real(Kind=realkind), Dimension(1:MSGpixX, 1:Lines),                    Intent(In) :: latitude
    Real(Kind=realkind), Dimension(1:MSGpixX, 1:Lines),                    Intent(In) :: longitude
    Integer(Kind=realkind), Dimension(1:n_debuginfo),                           Intent(In) :: debuginfo

    Integer (Kind=maskind), Dimension(1:MSGpixX, 1:Lines), Intent(In) :: mask_array
    ! 0 : do not process
    ! 1 : no snow
    ! 2 : snow

    Real(Kind=realkind), Intent (In) :: sigma_co ! estimate for the spectral to broadband conversion error

    Real, Intent(In) :: alb_max    ! maximum value for albedo
    Real, Intent(In) :: alb_min    ! minimum value for albedo
    Real, Intent(In) :: sig_max    ! maximum value for albedo error
    Real, Intent(In) :: sig_min    ! minimum value for albedo error

    Real (Kind=4),Dimension(0:N_channels,1:N_inalbedos,1:N_outalbedos,1:N_mask),Intent(In) :: coeffs
    !  ! spectral to broadband conversion coefficients (directional-hemispherical)
    !  Real, Dimension(0:N_channels) :: co_bb_dh       ! 300-4000 total shortwave
    !  Real, Dimension(0:N_channels) :: co_vi_dh       ! 400- 700 visible
    !  Real, Dimension(0:N_channels) :: co_ni_dh       ! 700-4000 NIR/SWIR
    !  Real, Dimension(0:N_channels) :: co_bb_dh_snow  ! 300-4000 total shortwave
    !  Real, Dimension(0:N_channels) :: co_vi_dh_snow  ! 400- 700 visible
    !  Real, Dimension(0:N_channels) :: co_ni_dh_snow  ! 700-4000 NIR/SWIR
    !  ! spectral to broadband conversion coefficients (bi-hemispherical)
    !  Real, Dimension(0:N_channels) :: co_bb_bh       ! 300-4000 total shortwave
    !  Real, Dimension(0:N_channels) :: co_vi_bh       ! 400- 700 visible
    !  Real, Dimension(0:N_channels) :: co_ni_bh       ! 700-4000 NIR/SWIR
    !  Real, Dimension(0:N_channels) :: co_bb_bh_snow  ! 300-4000 total shortwave
    !  Real, Dimension(0:N_channels) :: co_vi_bh_snow  ! 400- 700 visible
    !  Real, Dimension(0:N_channels) :: co_ni_bh_snow  ! 700-4000 NIR/SWIR

    ! Input spectral albedos data
    Real (Kind=4),Dimension(1:MSGpixX,1:Lines,1:N_channels,1:N_inalbedos),Intent(In) :: albedos
    Real (Kind=4),Dimension(1:MSGpixX,1:Lines,1:N_channels,1:N_inalbedos),Intent(In) :: albedos_cov
    Real (Kind=4),Dimension(1:MSGpixX,1:Lines,1:N_channels),Intent(In) :: albedos_age
    Real (Kind=4),Dimension(1:MSGpixX,1:Lines,1:N_channels),Intent(In) :: albedos_quality

    ! Output albedos
    Real (Kind=4),Dimension(1:MSGpixX,1:Lines,1:N_inalbedos,1:N_outalbedos),Intent(InOut) :: outalbedos
    Real (Kind=4),Dimension(1:MSGpixX,1:Lines,1:N_inalbedos,1:N_outalbedos),Intent(InOut) :: outalbedos_cov
    Real (Kind=4),Dimension(1:MSGpixX,1:Lines),Intent(InOut) :: outalbedos_age
    Real (Kind=4),Dimension(1:MSGpixX,1:Lines),Intent(InOut) :: outalbedos_quality

    !f2py intent(in,hide) n_debuginfo
    !f2py intent(in,hide) N_channels
    !f2py intent(in,hide) N_mask
    !f2py intent(in,hide) Lines
    !f2py intent(in,hide) MSGpixX
    !f2py intent(in,hide) N_outalbedos
    !f2py intent(out) errmsg
    !f2py intent(out) errcode

    ! Local variables
    Real (Kind=4),Dimension(0:N_channels) :: thiscoeffs
    Real (Kind=4),Dimension(1:N_channels) :: alb_perchannel, sig_perchannel
    Real                                  :: albedo, sigma
    Integer                               :: X,Y,i_outalbedo, i_inalbedo
    Integer                               :: mask

    errcode = 0
    errmsg = ''

    If (debuglevel .ge. 10) print *, '---------------'
    If (debuglevel .ge. 10) print *, 'Entering albedo_spectral_integration.f90'

    Do Y = ystart, yend
       Do X = xstart, xend
             If (debuglevel .ge. 100) print *, '--- pixel loop --- YX=',Y,X,'lat/lon = ',latitude(X,Y),longitude(X,Y)
             If (debuglevel .ge. 100) print *, '--- ',debuginfo
             mask = mask_array(X,Y)
             outalbedos_quality(X,Y) = albedos_quality(X,Y,1)
             If (mask .eq. 0) then
                 If (debuglevel .ge. 150) print *, 'skipping in spectral integration because mask is 0',X,Y
                 cycle
             else
                 If (debuglevel .ge. 150) print *, 'processing ',X,Y, mask
             End If
             Do i_inalbedo = 1, N_inalbedos ! DH and BH
                outalbedos_age(X,Y) = Maxval( albedos_age(X,Y,1:N_channels) )

                !! TODO : this piece of code may be needed for EPS somewhere :
!!!          ! set quality flag
!!!          quality_al(X,Y,N_channels+1) = quality_al(X,Y,N_channels+1) + QUA_EPS
!!!          If ( N_valid_snow .ne. N_valid .and. N_valid_snow .ne. 0 ) Then    !--NL  ! QUA_MAJORITY
!!!               quality_al(X,Y,N_channels+1) = quality_al(X,Y,N_channels+1) + QUA_MAJORITY
!!!          End If
!!!          If (snow) quality_al(X,Y,N_channels+1) = quality_al(X,Y,N_channels+1) + QUA_SNOW
                alb_perchannel = albedos(X,Y,:,i_inalbedo)
                sig_perchannel = albedos_cov(X,Y,:,i_inalbedo) ! Should there be a factor **2 to add here ? TODO: clarify
                Do i_outalbedo = 1, N_outalbedos ! BB VI NI
                  thiscoeffs = coeffs(:,i_inalbedo,i_outalbedo,mask)
                  albedo = thiscoeffs(0) + Dot_Product(alb_perchannel,thiscoeffs(1:N_channels))
                  If (.not. (isnan(albedo))) Then
                    albedo = Minval( (/ albedo, alb_max /) )
                    albedo = Maxval( (/ albedo, alb_min /) )
                  End If
                  outalbedos(X,Y,i_inalbedo, i_outalbedo) = albedo
                  If (debuglevel .ge. 150) print *, 'i_inalbedo', i_inalbedo
                  If (debuglevel .ge. 150) print *, 'i_outalbedo', i_outalbedo
                  If (debuglevel .ge. 150) print *, 'coeffs', coeffs
                  If (debuglevel .ge. 150) print *, 'mask', mask
                  If (debuglevel .ge. 150) print *, 'thiscoeffs',thiscoeffs
                  If (debuglevel .ge. 150) print *, 'albedo B bb/vi/ni - bh/dh', albedo

                  sigma = Sqrt( (albedo*sigma_co)**2 + Dot_Product(sig_perchannel**2, thiscoeffs(1:N_channels)**2) )
                  If (.not. (isnan(sigma))) Then
                    sigma = Minval( (/ sigma, sig_max /) )
                    sigma = Maxval( (/ sigma, sig_min /) )
                  End If
                  outalbedos_cov(X,Y,i_inalbedo, i_outalbedo) = sigma
                End Do
             End Do
             If (debuglevel .ge. 150) print *, 'albedo ',i_inalbedo, i_outalbedo, albedo
             If (debuglevel .ge. 1500) print *, 'albedo age, albedo quality',albedos_age, albedos_quality
             If (debuglevel .ge. 1500) print *, 'albedos_quality  ',albedos_quality
             If (debuglevel .ge. 1500) print *, 'outalbedos_quality  ', outalbedos_quality
        End Do
    End Do
End Subroutine albedo_spectral_integration
